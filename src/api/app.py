#!/usr/bin/python3
import sys
from flask import Flask, request, send_file, jsonify
import io
# project imports
import camera
import fingers
import match

server = Flask("handy")

@server.route("/handy/debug")
def debug_endpoint():
    return "Python " + sys.version + "\n"


@server.route("/handy/camera")
def camera_endpoint():
    file = io.BytesIO()
    while True:
        try:
            camera.picture(file, format="png")
            break
        except Exception as e:
            file.seek(0, 0)
            if not requests.args.get("nofail", default=False, type=bool):
                return send_file(file, mimetype="image/png"), 500
    file.seek(0, 0)
    return send_file(file, mimetype="image/png")

@server.route("/handy/fingers", methods=["GET", "POST"])
def fingers_endpoint():
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

@server.route("/handy/sign", methods=["GET", "POST"])
def sign_endpoint():
    algo = request.args.get("algorithm", default="naive", type=str).lower()
    if algo in match.algorithms:
        img = io.BytesIO()
        if request.method == "GET":
            camera.picture(img, format="png")
        elif request.method == "POST":
            img.write(request.data)
        img.seek(0, 0)
        points = fingers.wireframe(img, request)
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