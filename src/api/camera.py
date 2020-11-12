#!/usr/bin/python3
import picamera

def picture(file, **kwargs):
    with picamera.PiCamera() as cam:
        cam.capture(file, **kwargs)
