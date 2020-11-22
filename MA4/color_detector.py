#! /usr/bin/env python3.7

import cv2 
import numpy as np
import time
import utils
from dataclasses import dataclass


def blue_mask(hsv_image):
    dark_blue = np.array([90, 100, 100])
    light_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv_image, dark_blue, light_blue)
    return mask


def find_contours(bicolor_img) -> list:
    bi = bicolor_img.copy()
    thres_val = 60 # move to config
    gray_img = cv2.cvtColor(bi, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    ret, im2 = cv2.threshold(gray_img, thres_val, 255, cv2.THRESH_BINARY_INV)
    conts, hierarchy = cv2.findContours(gray_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return conts

@dataclass
class Blob:
    area: float
    d2c:  float
    d2b:  float




def parse_blob(cnt, W, H) -> Blob:
        cnt_center = utils.get_center(cnt)
        d2c = cnt_center[0] - W/2
        d2b = H - cnt_center[1]
        area = cv2.contourArea(cnt)
        return Blob(d2c=d2c, d2b=d2b, area=area)


def find_blobs(bicolor_img):
    MIN_CNT_AREA = 5000
    output = bicolor_img.copy()
    image_height, image_width, _ = output.shape
    cnts = find_contours(bicolor_img)
    blobs = []
    for cnt in cnts:
        if cv2.contourArea(cnt) > MIN_CNT_AREA:
            center = utils.get_center(cnt)
            cv2.drawContours(output, [cnt], -1, (255, 255, 0), 2)
            cv2.circle(output, center, 7, (255, 255, 255), -1)
            cv2.line(output, (center[0],image_height), ( center[0],0), (0,255,255), 2)
            cv2.line(output, (image_width,center[1]), (0, center[1]), (255,0,255), 2)
            b = parse_blob(cnt, image_width, image_height)
            blobs.append(b)
            print(b)
            utils.show(output)
    return blobs

def find_best_prey(blobs):
    return sorted(blobs, key=lambda b: b.d2b)[0]


# def find_biggest_blob(bicolor_img) -> tuple:
#     min_area = 400
#     contours = find_contours(bicolor_img)
#     conts_w_area = [ (c, cv2.contourArea(c)) for c in contours ]
#     conts_w_area = [ x for x in conts_w_area if x[1] > min_area]
#     if len(conts_w_area) > 0:
#         sorted_conts = sorted(conts_w_area, key=lambda x: x[1]) # sort by area size
#         sorted_conts = list(reversed(sorted_conts)) # decreasing order
#         largest = sorted_conts[0][0]
#         # if DEBUG:
#         #     print(largest)
#         #     blob = cv2.ellipse(bicolor_img.copy(),el, (120, 255, 0), 5)
#         #     show(blob, 'largest' )
#         # circle_center = get_center(largest)
#         return True, largest


#     else:
#         return False, None


def apply_mask(bgr_img, mask_fn):
    hsv_image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    mask = mask_fn(hsv_image)
    bicol = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)
    return bicol

def raspi_take_picture():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.1)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    # display the image on screen and wait for a keypress
    return image

if __name__ == '__main__':
    img = cv2.imread('./img/b.jpg')
    for i in range(1, 4):
        ip =  './img/b/{}.png'.format(i)
        print(i, ip)
        img = cv2.imread(ip)
        utils.show(img)
        bicol = apply_mask(img, blue_mask)
        blobs = find_blobs(bicol)
        for b in blobs:
            print('blob', b)
        if len(blobs) > 0:
            print(find_best_prey(blobs))
