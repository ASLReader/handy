#!/usr/bin/python3
import sys
from flask import Flask, request, send_file, jsonify
import io
import requests
# project imports
import camera
import fingers

server = Flask("handy")

@server.route("/handy/debug")
def debug_endpoint():
    return "Python " + sys.version + "\n"


@server.route("/handy/camera")
def camera_endpoint():
    file = io.BytesIO()
    camera.picture(file, format="png")
    file.seek(0, 0)
    return send_file(file, mimetype="image/png")

@server.route("/handy/fingers")
def fingers_endpoint():
    file = io.BytesIO()
    camera.picture(file, format="png")
    file.seek(0, 0)
    points = fingers.wireframe(file)
    return jsonify(points)

@server.route("/handy/sign")
def sign_endpoint():
    return "Sign endpoint\n"
