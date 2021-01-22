#!/usr/bin/python3
import sys
from flask import Flask, request, send_file, jsonify
import io
# project imports
import camera
import fingers
import match
import passive

server = Flask("handy")

passive.start_worker()

@server.route("/handy/debug")
def debug_endpoint():
    return jsonify({
        "name": "handy",
        "python": sys.version,
        "cache_max": passive.max_cache_items,
        "cache_avg": (len(passive.cache_pictures) + len(passive.cache_fingers) + len(passive.cache_matches))/3,
        "worker_period": passive.debug_worker_period
    })


@server.route("/handy/camera")
def camera_endpoint():
    if request.args.get("live", default=False, type=bool):
        file = io.BytesIO()
        while True:
            try:
                camera.picture(file, format="png")
                break
            except Exception as e:
                file.seek(0, 0)
                if not request.args.get("nofail", default=False, type=bool):
                    return send_file(file, mimetype="image/png"), 500
        file.seek(0, 0)
        return send_file(file, mimetype="image/png")
    else:
        if len(passive.cache_pictures) == 0:
            return jsonify({"reason": "no pictures"}), 418
        file = passive.cache_pictures[-1]
        file.seek(0,0)
        return send_file(file, mimetype="image/png")

@server.route("/handy/fingers", methods=["GET", "POST"])
def fingers_endpoint():
    if request.args.get("live", default=False, type=bool):
        img = io.BytesIO()
        if request.method == "GET":
            camera.picture(img, format="png")
        elif request.method == "POST":
            img.write(request.data)
        img.seek(0, 0)
        points = fingers.wireframe(img, request)
        if points is None:
            return jsonify({"reason": "hand processing back-end failure"}), 500
        return jsonify(points)
    else:
        if len(passive.cache_fingers) == 0:
            return jsonify({"reason": "no hands"}), 418
        return jsonify(passive.cache_fingers[-1])

@server.route("/handy/sign", methods=["GET", "POST"])
def sign_endpoint():
    algo = request.args.get("algorithm", default="naive", type=str).lower()
    use_cache = not request.args.get("live", default=False, type=bool)
    if use_cache and algo == "naive":
        if len(passive.cache_matches) == 0:
            return jsonify({"reason": "no hands"}), 418
        return jsonify(passive.cache_matches[-1])
    if algo in match.algorithms:
        if use_cache:
            if len(passive.cache_fingers) == 0:
                return jsonify({"reason": "no hands"}), 418
            return jsonify(passive.cache_fingers[-1])
        else:
            img = io.BytesIO()
            if request.method == "GET":
                camera.picture(img, format="png")
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