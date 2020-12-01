#!/usr/bin/python3
import requests

import os
import sys
import json
import time

if __name__ == '__main__':
    script_name = sys.argv[0]
    img_dir = os.getcwd()
    if len(sys.argv) > 1:
        img_dir = sys.argv[1]
    print(sorted(os.listdir(img_dir)))
    wireframes = {}
    for filename in sorted(os.listdir(img_dir)):
        fullname = os.path.join(img_dir, filename)
        try:
            if os.path.isfile(fullname) and filename.endswith(".png"):
                print("POSTing img", fullname, "for wireframe")
                with open(fullname, 'rb') as img:
                    wireframe_resp = requests.post("http://192.168.0.31:5000/handy/fingers", data=img)
                if wireframe_resp.status_code == 200:
                    wireframes[filename[:-4]] = wireframe_resp.json()
        except Exception as e:
            print(e)
        time.sleep(0.1)
    print("Done generating wireframes, writing...")
    with open("wireframes.json", 'w') as out:
        json.dump(wireframes, out, indent=" "*2)
