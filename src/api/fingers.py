#!/usr/bin/python3
import requests

hand_matrix_endpoint = "http://192.168.0.30:5000/"

def wireframe(filelike, req):
    result = requests.post(hand_matrix_endpoint, params=req.args.to_dict(), data=filelike.read())
    if result.status_code == 200:
        #print(result.content)
        return result.json()
    return None