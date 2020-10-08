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
