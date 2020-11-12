#!/usr/bin/python3
import picamera

def picture(filelike, **kwargs):
    with picamera.PiCamera() as cam:
        cam.capture(filelike, **kwargs)
