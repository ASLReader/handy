#!/usr/bin/python3
import requests

hand_matrix_endpoint = "https://handy.zettagram.com/"

def wireframe(filelike, req):
    result = requests.post(hand_matrix_endpoint, params=req.args.to_dict(), data=filelike.read())
    if result.status_code == 200:
        #print(result.content)
        return result.json()
    return None

def wireframe_reqless(filelike):
    result = requests.post(hand_matrix_endpoint, data=filelike.read())
    if result.status_code == 200:
        #print(result.content)
        return result.json()
    return None