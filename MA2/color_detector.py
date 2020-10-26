#! /usr/bin/env python3.7

import cv2 
import numpy as np
import time
import utils


def red_mask(hsv_image):
    dark_red_down = np.array([0, 50, 50])
    light_red_down = np.array([10, 255, 255])

    dark_red_up = np.array([170, 50, 50])
    light_red_up = np.array([180, 255, 255])
    mask_down = cv2.inRange(hsv_image, dark_red_down, light_red_down)
    mask_up = cv2.inRange(hsv_image, dark_red_up, light_red_up)

    mask = mask_up + mask_down
    return mask


def blue_mask(hsv_image):
    dark_blue = np.array([90, 100, 100])
    light_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv_image, dark_blue, light_blue)
    return mask


def yellow_mask(hsv_image):
    dark = np.array([20, 100, 100])
    light = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask


def green_mask(hsv_image):
    dark = np.array([40, 100, 50])
    light = np.array([60, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask


MASKS = {
    'blue': blue_mask,
    'red': red_mask,
    'green': green_mask,
    'yellow': yellow_mask,
}


# not used, but process could be usefull
def find_circle_w_hough(bicolor_img) -> list:
    thres_val = 60
    bi = bicolor_img.copy()
    gray_img = cv2.cvtColor(bi, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    ret, im2 = cv2.threshold(gray_img, thres_val, 255, cv2.THRESH_BINARY_INV)
    gray_img = img.copy()
    rows = gray_img.shape[0]
    circles = cv2.HoughCircles(
        gray_img,
        cv2.HOUGH_GRADIENT,
        1,
        rows/6,
        # param1=50,
        # param2=30,
        minRadius=0,
        maxRadius=0)
    return circles


def find_contours(bicolor_img) -> list:
    bi = bicolor_img.copy()
    thres_val = 60 # move to config
    gray_img = cv2.cvtColor(bi, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    ret, im2 = cv2.threshold(gray_img, thres_val, 255, cv2.THRESH_BINARY_INV)
    conts, hierarchy = cv2.findContours(gray_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return conts


def circle_detector(bicolor_img) -> tuple:
    min_area = 400
    contours = find_contours(bicolor_img)
    conts_w_area = [ (c, cv2.contourArea(c)) for c in contours ]
    conts_w_area = [ x for x in conts_w_area if x[1] > min_area]
    if len(conts_w_area) > 0:
        sorted_conts = sorted(conts_w_area, key=lambda x: x[1]) # sort by area size
        sorted_conts = list(reversed(sorted_conts)) # decreasing order
        largest = sorted_conts[0][0]
        el = cv2.fitEllipse(largest)
        # if DEBUG:
        #     print(largest)
        #     blob = cv2.ellipse(bicolor_img.copy(),el, (120, 255, 0), 5)
        #     show(blob, 'largest' )
        # circle_center = get_center(largest)
        return True, el


    else:
        return False, None


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

def find_colored_circle(img):
    detected_colors = []
    for color, mask_fn in MASKS.items():
        bicol = apply_mask(img, mask_fn)
        is_circle, circle = circle_detector(bicol)
        if is_circle:
            # print(cv2.contourArea(circle))
            area = circle[1][0] * circle[1][1] * np.pi
            detected_colors.append((color, area, circle ))

    print(detected_colors)
    return detected_colors

def find_color(img):
    circles = find_colored_circle(img)
    if not circles:
        return None
    else:
        return circles[0][0]


if __name__ == '__main__':
    img = cv2.imread('./img/color_wheel.jpg')
    for color, mask_fn in MASKS.items():
        bicol = apply_mask(img, mask_fn)
        if circle_detector(bicol):
            print(color + ': detected !')
        else:
            print(color + ': nope ')
