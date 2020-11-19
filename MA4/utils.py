'''
various utilitary function for color detection
'''
import cv2
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
from math import atan, cos, sin, pi, radians

DEBUG = True


def show(img, title=''):
    title = str(title)
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyWindow(title)


def rgb2hsv(r, g, b):
    hsv = rgb_to_hsv((r, g, b))
    return (hsv[0] * 180, hsv[1] * 255, hsv[2])


def debug_img(img, title=''):
    if DEBUG:
        show(img, title='')


def get_center(cnt):
    # https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return (cX, cY)


if __name__ == '__main__':
    from sys import argv
    r = int(argv[1])
    g = int(argv[2])
    b = int(argv[3])
    print(rgb2hsv(r, g, b))
