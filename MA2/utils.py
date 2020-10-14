'''
various utilitary function
'''
from cv2 import *
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
from math import atan, abs, cos, sin

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

def polar2cart(a, r):
    x = r * sin(a)
    y = r * cos(a)
    return (x, y)

def caculate_angle_to_dest(robot_angle,
                           robot_x, robot_y,
                           dest_x, dest_y):
    """
    Use the angle of the robot, its position, and the position of the
    destination to calculate the angle of the destination from the origin.
    Angles are in degrees.
    """
    dx = abs(robot_x - dest_x)
    dy = abs(robot_y - dest_y)
    if dest_x > robot_x:
        a = atan(dy/dx)
        if dest_y > robot_y:
            return a
        elif dest_y <= robot_y:
            return 360 - a
    elif dest_x <= robot_x:
        a = atan(dx/dy)
        if dest_y > robot_y:
            return 90 + a
        elif dest_y <= robot_y:
            return 270 - a 


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
