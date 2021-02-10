#!/usr/bin/python3
import picamera
import numpy as np
import cv2
import io

bgRemover = None
# cv2.createBackgroundSubtractorMOG2(0, 50)

def picture(filelike, **kwargs):
    global bgRemover
    with picamera.PiCamera() as cam:
        cam.capture(filelike, **kwargs)
    if bgRemover is not None:
        remove_bg(filelike)
    return filelike

def remove_bg(filelike):
    global bgRemover
    #print("Removing bg")
    # code inspired by
    # https://medium.com/swlh/roi-segmentation-contour-detection-and-image-thresholding-using-opencv-c0d2ea47b787
    filelike.seek(0,0)
    filelike2 = io.BytesIO()
    filelike2.write(filelike.read())
    nparr = np.frombuffer(filelike2.getbuffer(), dtype=np.uint8)
    img = cv2.flip(cv2.imdecode(nparr, cv2.IMREAD_COLOR), 1)

    # build & apply bg mask
    mask = bgRemover.apply(img,learningRate=0)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    no_bg = cv2.bitwise_and(img, img, mask=mask)

    # save image
    filelike.seek(0,0)
    data = cv2.imencode(".png", no_bg)[1].tobytes()
    filelike.write(data)

def use_bg(filelike):
    global bgRemover
    bgRemover = cv2.createBackgroundSubtractorMOG2(0, 50)
    # use image to teach bg subtractor
    nparr = np.frombuffer(filelike.getbuffer(), dtype=np.uint8)
    img = cv2.flip(cv2.imdecode(nparr, cv2.IMREAD_COLOR), 1)
    bgRemover.apply(img,learningRate=0)



