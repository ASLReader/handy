#!/usr/bin/python3
import io
import sys
import threading as thread
import time
# project imports
import camera
import fingers
import match

max_cache_items = 5

cache_pictures = list()
cache_fingers = list()
cache_matches = list()

debug_worker_period = -1.0

def worker():
    global cache_pictures, cache_fingers, cache_matches, debug_worker_period
    start = time.time()
    while not sys.is_finalizing(): # loop until shutdown
        # take a picture
        file = io.BytesIO()
        try:
            camera.picture(file, format="png")
            # will fail when camera is being used by something else
        except KeyboardInterrupt:
            return
        except Exception as e:
            continue
        if len(cache_pictures) > max_cache_items:
            del(cache_pictures[0])
        file.seek(0,0)

        # analyse pic
        wireframe = fingers.wireframe_reqless(file)
        file.seek(0,0)
        if wireframe is None or len(wireframe["landmarks"]) == 0:
            continue

        # match fingers
        sign = match.algorithms["naive"](wireframe)
        # add to cache and keep same cache size
        cache_fingers.append(wireframe)
        if len(cache_fingers) > max_cache_items:
            del(cache_fingers[0])
            del(cache_matches[0])
        cache_matches.append(sign)
        if len(cache_matches) > max_cache_items:
            del(cache_matches[0])
        now = time.time()
        debug_worker_period = now - start
        start = now

def start_worker():
    thread.Thread(target=worker).start()
