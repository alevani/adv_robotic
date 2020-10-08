'''
various utilitary function
'''
from cv2 import *

DEBUG = True


def debug_img(img, title=''):
    if DEBUG:
        cv2.imshow(title, img)
        waitKey(0)
        destroyWindow(title)

def get_center(cnt):
    # https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return (cX, cY)

