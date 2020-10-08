#! /usr/bin/env python3.7

from cv2 import *
import numpy as np

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

MASKS = {
    'blue': blue_mask,
    'red': red_mask,
}

def circle_detector(bicolor_img) -> bool:
    gray_img = cv2.cvtColor(bicolor_img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)

    cv2.imshow('medianBlur', gray_img)

    rows = gray_img.shape[0]
    circles = cv2.HoughCircles(
        gray_img, cv2.HOUGH_GRADIENT, 1, rows/8, param1=100, param2=30, minRadius=0, maxRadius=0)
    print(circles)

    if circles is not None:
        return True, gray_img
    else:
        return False, gray_img

def apply_mask(bgr_img, color):
    # imshow('cam', img)
    # waitKey(0)
    # destroyWindow('cam')
    hsv_image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    mask_fn = MASKS[color]
    mask = mask_fn(hsv_image)
    bicol = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)
    return bicol
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    # rawCapture.truncate(0)


if __name__ == '__main__':
    img = imread('./color_wheel.jpeg')
    for c in MASKS.keys():
        bicol = apply_mask(img, c)
        imshow(c, bicol)
        waitKey(0)
        destroyWindow(c)
        if circle_detector(bicol):
            print(color + ': detected !')
        else:
            print(color + ': nope ')
    exit(0)
    while True:
        # cam = VideoCapture(0)
        # s, img = cam.read()
        img = imread('./color_wheel.jpeg')
        if s:
            apply_mask(img)
        else:
            print('couldnt read img')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
