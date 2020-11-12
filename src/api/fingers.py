#!/usr/bin/python3
import requests

hand_matrix_endpoint = "http://192.168.0.31:5000/"

def wireframe(filelike, req):
    result = requests.post(hand_matrix_endpoint, params=req.args.to_dict(), data=filelike.read())
    if result.status_code == 200:
        return result.json()
    return None
