#! /usr/bin/env python3.7

from cv2 import *
import numpy as np
from utils import *


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
    dark_blue = np.array([100, 50, 50])
    light_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv_image, dark_blue, light_blue)
    return mask


def yellow_mask(hsv_image):
    dark = np.array([20, 100, 100])
    light = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask


def green_mask(hsv_image):
    dark = np.array([65, 100, 100])
    light = np.array([75, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask

MASKS = {
    'blue': blue_mask,
    'red': red_mask,
    'green': green_mask,
    'yellow': yellow_mask,
}


def circle_detector(bicolor_img) -> bool:
    bi = bicolor_img.copy()
    gray_img = cv2.cvtColor(bi, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    debug_img(gray_img)
    ret,gray_img = cv2.threshold(gray_img,60,255,cv2.THRESH_BINARY)
    debug_img(gray_img, 'before')
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
    print(circles)

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            output = gray_img.copy()
            image = gray_img.copy()
            cv2.circle(output, (x, y), r, (255, 255, 255), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 0, 255), -1)
        # show the output image
            cv2.imshow("output", np.hstack([image, output]))
            cv2.waitKey(0)
            cv2.destroyWindow("output")

        return True, gray_img
    else:
        return False, gray_img


def apply_mask(bgr_img, mask_fn):
    hsv_image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    mask = mask_fn(hsv_image)
    bicol = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)

    return bicol
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    # rawCapture.truncate(0)


if __name__ == '__main__':
    img = imread('./img/color_wheel.jpg')
    for color, mask_fn in MASKS.items():
        bicol = apply_mask(img, mask_fn)
        if circle_detector(bicol):
            print(color + ': detected !')
        else:
            print(color + ': nope ')
