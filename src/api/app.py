#!/usr/bin/python3
import sys
from flask import Flask, request, send_file, jsonify
import io
# project imports
import camera
import fingers
import match
import passive
import database

server = Flask("handy")

passive.start_worker()

@server.route("/handy/debug")
def debug_endpoint():
    # misc debug info, this should not be relied on
    return jsonify({
        "name": "handy",
        "python": sys.version,
        "cache_max": passive.max_cache_items,
        "cache_avg": (len(passive.cache_pictures) + len(passive.cache_fingers) + len(passive.cache_matches))/3,
        "worker_period": passive.debug_worker_period,
        "lifetime": passive.lifetime(),
        "start": passive.debug_lifetime
    })


@server.route("/handy/camera")
def camera_endpoint():
    if request.args.get("live", default=False, type=bool):
        # take new picture (legacy)
        nofail = request.args.get("nofail", default=False, type=bool)
        file = io.BytesIO()
        while True:
            try:
                file = camera.picture(file, format="png")
                break
            except Exception as e:
                file.seek(0, 0)
                if not nofail:
                    return send_file(file, mimetype="image/png"), 500
        file.seek(0, 0)
        return send_file(file, mimetype="image/png")
    else:
        # use cached picture
        if len(passive.cache_pictures) == 0:
            return jsonify({"reason": "no pictures"}), 418
        file = passive.cache_pictures[-1]
        file.seek(0,0)
        # flask automatically closes files (for some reason, without a way to disable it)
        # so provide a copy so it doesn't close the cached buffer
        file2 = io.BytesIO()
        file2.write(file.read())
        file2.seek(0,0)
        return send_file(file2, mimetype="image/png")

@server.route("/handy/fingers", methods=["GET", "POST"])
def fingers_endpoint():
    if request.args.get("live", default=False, type=bool):
        # use live data (legacy)
        img = io.BytesIO()
        if request.method == "GET":
            img = camera.picture(img, format="png")
        elif request.method == "POST":
            img.write(request.data)
        img.seek(0, 0)
        points = fingers.wireframe(img, request)
        if points is None:
            return jsonify({"reason": "hand processing back-end failure"}), 500
        return jsonify(points)
    else:
        # cached functionality
        count = request.args.get("count", default=0, type=int)
        if count <= 0:
            if len(passive.cache_fingers) == 0:
                return jsonify({"reason": "no hands"}), 418
            return jsonify(passive.cache_fingers[-1])
        else:
            # list cached finger data
            if len(passive.cache_matches) < count:
                return jsonify({"reason": "not enough hands"}), 418
            return jsonify(passive.cache_fingers[-count:])

@server.route("/handy/sign", methods=["GET", "POST"])
def sign_endpoint():
    algo = request.args.get("algorithm", default="naive", type=str).lower()
    use_cache = not request.args.get("live", default=False, type=bool)
    count = request.args.get("count", default=0, type=int)
    if use_cache and algo == "naive":
        # use pre-cached naive match data
        if count <= 0:
            if len(passive.cache_matches) == 0:
                return jsonify({"reason": "no hands"}), 418
            return jsonify(passive.cache_matches[-1])
        else:
            # list cached match data
            if len(passive.cache_matches) < count:
                return jsonify({"reason": "not enough hands"}), 418
            return jsonify(passive.cache_matches[-count:])
    if algo in match.algorithms:
        if use_cache:
            if count <= 0:
                # use cached finger data since no cached match data for chosen algorithm
                if len(passive.cache_fingers) == 0:
                    return jsonify({"reason": "no hands"}), 418
                item = match.algorithms[algo](passive.cache_fingers[-1], request)
                return jsonify(item)
            else:
                # use cached finger data to generate list of match data
                if len(passive.cache_matches) < count:
                    return jsonify({"reason": "not enough hands"}), 418
                items = list()
                for f in passive.cache_fingers:
                    items.append(match.algorithms[algo](f, request))
                return jsonify(items)
        else:
            # generate match data live (legacy)
            img = io.BytesIO()
            if request.method == "GET":
                img = camera.picture(img, format="png")
            elif request.method == "POST":
                img.write(request.data)
            points = None
            img.seek(0, 0)
            points = fingers.wireframe(img, request)
            if points is None:
                return jsonify({"reason": "No finger data found"}), 400
            #print("ML detection:", points["landmarks"])
            result = match.algorithms[algo](points, request)
            #print("Matches:", result)
            return jsonify(result)
    else:
        return jsonify({"reason": "algorithm not found"}), 404

# do response chores
@server.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# sync firebase db to new algorithm reference struct
match.known_hands_NEW = database.known_hands_FIREBASE