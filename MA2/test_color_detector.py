from color_detector import *
import pytest


def test_4color_image():
    for c in MASKS.keys():
        print(" === " + c)
        img = imread('./img/{}.jpg'.format(c))
        bicol = apply_mask(img, c)
        imshow(c, bicol)
        waitKey(0)
        destroyWindow(c)
        detected, gray_img =  circle_detector(bicol)
        print("circle detected", detected)
        imshow(str(detected), gray_img)
        waitKey(0)
        destroyWindow(c)


def test_wheel():
    for c in MASKS.keys():
        print(" === " + c)
        img = imread('./img/color_wheel.jpg')
        bicol = apply_mask(img, c)
        imshow(c, bicol)
        waitKey(0)
        destroyWindow(c)
        detected, gray_img =  circle_detector(bicol)
        imshow(str(detected), gray_img)
        waitKey(0)
        destroyWindow(c)


if __name__ == '__main__':
    # test_wheel()
    test_4color_image()
