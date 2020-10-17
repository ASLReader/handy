#!/usr/bin/python3
import sys
from flask import Flask

server = Flask("handy")

@server.route("/handy/debug")
def debug_endpoint():
    return "Python " + sys.version + "\n"


@server.route("/handy/camera")
def camera_endpoint():
    return "Camera endpoint\n"

@server.route("/handy/fingers")
def fingers_endpoint():
    return "Fingers endpoint\n"

@server.route("/handy/sign")
def sign_endpoint():
    return "Sign endpoint\n"

