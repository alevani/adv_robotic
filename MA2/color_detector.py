#! /usr/bin/env python3.7

from cv2 import *

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

def circle_detector(2col_img) -> bool:
    gray_img = cv2.cvtColor(2col_img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)

    cv2.imshow('medianBlur', gray_img)

    rows = gray_img.shape[0]
    circles = cv2.HoughCircles(
        gray_img, cv2.HOUGH_GRADIENT, 1, rows/8, param1=100, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        return True
    else: False

def color_detector(bgr_img):
    # imshow('cam', img)
    # waitKey(0)
    # destroyWindow('cam')
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    for color, mask_fn in MASKS.items():
        mask = mask_fn(hsv_image)
        2colors_img = cv2.bitwise_and(image, image, mask=mask)
        if circle_detector(2colors_img):
            print(color + ': detected !')
        else:
            print(color + ': nope ')
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

    rawCapture.truncate(0)


if __name__ == '__main__':
    while True:
        cam = VideoCapture(0)
        s, img = cam.read()
        if s:
            color_detector(img)
        else:
            print('couldnt read img')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
