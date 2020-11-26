#! /usr/bin/env python3.7

import cv2 
import numpy as np
import time
import threading
from time import sleep
import utils
import globals
from dataclasses import dataclass
SHARED_IMG = None


def blue_mask(hsv_image):
    dark_blue = np.array([90, 100, 100])
    light_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv_image, dark_blue, light_blue)
    return mask

def green_mask(hsv_image):
    dark = np.array([75, 100, 200])
    light = np.array([90, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask

def purple_mask(hsv_image):
    dark = np.array([140, 100, 200])
    light = np.array([160, 255, 255])
    mask = cv2.inRange(hsv_image, dark, light)
    return mask

MASK = green_mask

def find_contours(bicolor_img, version_cv2=globals.CV2) -> list:
    bi = bicolor_img.copy()
    THRES_VAL = 60 # move to config?
    gray_img = cv2.cvtColor(bi, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    ret, im2 = cv2.threshold(gray_img, THRES_VAL, 255, cv2.THRESH_BINARY_INV)
    # raspi and local don't have same cv2 version
    if version_cv2 == 2:
        _, conts, hierarchy = cv2.findContours(gray_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        conts, hierarchy = cv2.findContours(gray_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return conts


@dataclass
class Blob:
    area: float
    d2c:  float
    d2b:  float


def parse_blob(cnt, W, H) -> Blob:
        cnt_center = utils.get_center(cnt)
        d2c = cnt_center[0] - W/2
        d2b = H - cnt_center[1]
        area = cv2.contourArea(cnt)
        return Blob(d2c=d2c, d2b=d2b, area=area)


def find_blobs(bicolor_img, show_im=False):
    output = bicolor_img.copy()
    image_height, image_width, _ = output.shape
    cnts = find_contours(bicolor_img)
    blobs = []
    for cnt in cnts:
        if cv2.contourArea(cnt) > globals.MIN_CNT_AREA:
            center = utils.get_center(cnt)
            cv2.drawContours(output, [cnt], -1, (255, 255, 0), 2)
            cv2.circle(output, center, 7, (255, 255, 255), -1)
            cv2.line(output, (center[0],image_height), ( center[0],0), (0,255,255), 2)
            cv2.line(output, (image_width,center[1]), (0, center[1]), (255,0,255), 2)
            b = parse_blob(cnt, image_width, image_height)
            blobs.append(b)
            # print(b)
            if show_im:
                print("show_im", show_im)
                utils.show(output)
                # imshow('find_blobs', output)
    return blobs

def find_best_prey(blobs):
    return sorted(blobs, key=lambda b: b.d2b)[0]


# def find_biggest_blob(bicolor_img) -> tuple:
#     min_area = 400
#     contours = find_contours(bicolor_img)
#     conts_w_area = [ (c, cv2.contourArea(c)) for c in contours ]
#     conts_w_area = [ x for x in conts_w_area if x[1] > min_area]
#     if len(conts_w_area) > 0:
#         sorted_conts = sorted(conts_w_area, key=lambda x: x[1]) # sort by area size
#         sorted_conts = list(reversed(sorted_conts)) # decreasing order
#         largest = sorted_conts[0][0]
#         # if DEBUG:
#         #     print(largest)
#         #     blob = cv2.ellipse(bicolor_img.copy(),el, (120, 255, 0), 5)
#         #     show(blob, 'largest' )
#         # circle_center = get_center(largest)
#         return True, largest


#     else:
#         return False, None


def apply_mask(bgr_img, mask_fn):
    hsv_image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    mask = mask_fn(hsv_image)
    bicol = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)
    return bicol

def cam_thread(camera, rawCapture):
    print("   STARTING CAM THREAD \n\n")
    print("camera", camera)
    print("rawCapture", rawCapture)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        global SHARED_IMG
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        # show the frame
        # if globals.SHOW_IM:
        #     cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        rotated = cv2.rotate(image, cv2.ROTATE_180)
        SHARED_IMG = rotated.copy()
        if globals.SHOW_IM:
            if key == ord("q"):
            	break

def start_thread_video():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    RES = (640, 480)
    camera.resolution = RES
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=RES)
    # allow the camera to warmup
    # grab an image from the camera
    threading.Thread(target=cam_thread, args=(camera, rawCapture)).start()

    # camera.capture(rawCapture, format="bgr")
    # image = rawCapture.array
    # # display the image on screen and wait for a keypress
    # rotated = cv2.rotate(image, cv2.ROTATE_180)
    # camera.close()
    # return rotated




def raspi_take_picture():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    RES = (640, 480)
    camera.resolution = RES
    camera.framerate = 20
    rawCapture = PiRGBArray(camera, size=RES)
    # allow the camera to warmup
    time.sleep(0.05)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    # display the image on screen and wait for a keypress
    rotated = cv2.rotate(image, cv2.ROTATE_180)
    camera.close()
    return rotated

def get_width_cam():
    img = raspi_take_picture()
    image_height, image_width, _ = img.shape
    return image_width 

def find_prey():
    # img = raspi_take_picture()
    global SHARED_IMG
    if SHARED_IMG.all() == None :
        print('SHARED_IMG is None')
        return None
    img = SHARED_IMG.copy()
    # if globals.SHOW_IM:
    #     cv2.imshow('raw',img)
    bicol = apply_mask(img, MASK)
    # if globals.SHOW_IM:
    #     cv2.imshow('mask',img)
    #     key = cv2.waitKey(1)
    # utils.show(bicol)
    if globals.SHOW_IM:
        output = np.hstack((bicol, img))
        cv2.imshow('prey', output)
        # key = cv2.waitKey(1)
    blobs = find_blobs(bicol)
    if len(blobs) > 0:
        print(find_best_prey(blobs))
        # return find_best_prey(blobs)
        return sorted(blobs, key=lambda b: b.d2b)[0]
    else:
        return None

def test_pi_cam():
    # bicol = apply_mask(img, MASK)
    # blobs = find_blobs(bicol)
    # if len(blobs) > 0:
    #     print(find_best_prey(blobs))
    #     # return find_best_prey(blobs)
    #     return sorted(blobs, key=lambda b: b.d2b)[0]
    # else:
    #     return None

    paused = False
    while(True):
        # sleep(0.05)
        frame = raspi_take_picture()
        # Display the resulting frame
        if globals.SHOW_IM:
            cv2.imshow('Frame',frame)
        current_col = ""
        output = frame.copy()

        bicol = {}
        bicol = apply_mask(frame, MASK)
        # detected, el = circle_detector(bicol[c])
        # if detected:
        #     current_col += c
        #     cv2.ellipse(output, el, rgb_color[c], 5)
        # current_col += '\t'
        blobs = find_blobs(bicol)

        output = np.hstack((output, frame))

        # cv2.imshow('Frame', output)
        if len(blobs) > 0:
            left_motor  = 0
            right_motor = 0
            prey = find_best_prey(blobs)
            print("BEST", prey  )
            value_to_decrease = prey.d2c * 1000 / globals.MAX_D2C
            if prey.d2c == 0:
                left_motor = 1000
                right_motor = 1000
            if prey.d2c < 0:
                left_motor = 1000 - value_to_decrease
            elif prey.d2c > 0:
                right_motor = 1000 - value_to_decrease
            print(left_motor, right_motor)


        else:
            print("NO BLOBS")

        if not paused:
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('p'):
                cv2.waitKey(-1)  # wait until any key is pressed
                paused = True

        if paused:
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            if key == ord('p'):
                # cv2.waitKey(-1) #wait until any key is pressed
                paused = False

if __name__ == '__main__':
    img = cv2.imread('./img/b.jpg')
    for i in range(1, 4):
        ip =  './img/b/{}.png'.format(i)
        print(i, ip)
        img = cv2.imread(ip)
        utils.show(img)
        bicol = apply_mask(img, blue_mask)
        blobs = find_blobs(bicol)
        for b in blobs:
            print('blob', b)
        if len(blobs) > 0:
            print(find_best_prey(blobs))
