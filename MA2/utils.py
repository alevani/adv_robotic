'''
various utilitary function
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


def calculate_angular_speed_rotation(speed, degree=1, wheel_diam=9.45):
    peri = pi * wheel_diam
    sec_to_turn = peri / speed
    return (sec_to_turn * degree) / 360.0


def polar2cart(a, r):
    a = radians(a)
    x = r * sin(a)
    y = r * cos(a)
    try:
        return (x[0], y[0])
    except:
        return (x, y)


def caculate_angle_to_dest(robot_angle,
                           robot_x, robot_y,
                           dest_x, dest_y):
    """
    Use the angle of the robot, its position, and the position of the
    destination to calculate the angle of the destination from the origin.
    Angles are in degrees.
    """
    from math import degrees
    dx = abs(robot_x - dest_x)
    dy = abs(robot_y - dest_y)
    if dest_x == robot_x:
        if dest_y > robot_y:
            return 90
        elif dest_y < robot_y:
            return 270
        else:
            return 0
    elif dest_y == robot_y:
        if dest_x > robot_x:
            return 0
        elif dest_x < robot_x:
            return 180
        else:
            return 0
    elif dest_x > robot_x:
        a = atan(dy/dx)
        if dest_y > robot_y:
            return degrees(a)
        elif dest_y <= robot_y:
            return 360 - degrees(a)
    elif dest_x < robot_x:
        a = atan(dx/dy)
        if dest_y > robot_y:
            return 90 + degrees(a)
        elif dest_y <= robot_y:
            return 270 - degrees(a)
def timer(func):
    import time
    def wrapper(*arg, **kw):
        '''source: http://www.daniweb.com/code/snippet368.html'''
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print((t2 - t1), res, func.__name__)
        return res
    return wrapper

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
