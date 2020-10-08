'''
various utilitary function
'''
from cv2 import *
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv

DEBUG = True

def show(img, title=''):
    title = str(title)
    cv2.imshow(title, img)
    waitKey(0)
    destroyWindow(title)


def rgb2hsv(r, g ,b): 
    hsv = rgb_to_hsv((r, g, b)) 
    return (hsv[0] * 180, hsv[1] * 255 , hsv[2]) 
                    

def debug_img(img, title=''):
    if DEBUG:
        show(img, title='')

def get_center(cnt):
    # https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return (cX, cY)

