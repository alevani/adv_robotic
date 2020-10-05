#!/usr/bin/python3
import threading
from math import cos, sin, pi, floor
from adafruit_rplidar import RPLidar
import dbus.mainloop.glib
import dbus
from time import sleep
from picamera import PiCamera
from picamera.array import PiRGBArray as pia
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")


print("Starting robot")

# -----------------------init script--------------------------
camera = PiCamera()


def dbusError(self, e):
    # dbus errors can be handled here.
    # Currently only the error is logged. Maybe interrupt the mainloop here
    print('dbus error: %s' % str(e))


# init the dbus main loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# # get stub of the aseba network
# bus = dbus.SessionBus()
# asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')

# # prepare interface
# asebaNetwork = dbus.Interface(
#     asebaNetworkObject,
#     dbus_interface='ch.epfl.mobots.AsebaNetwork'
# )

# # load the file which is run on the thymio
# asebaNetwork.LoadScripts(
#     'thympi.aesl',
#     reply_handler=dbusError,
#     error_handler=dbusError
# )

# signal scanning thread to exit
exit_now = False

# Setup the RPLidar
# PORT_NAME = '/dev/ttyUSB0'
# lidar = RPLidar(None, PORT_NAME)
# This is where we store the lidar readings
scan_data = [0]*360
# --------------------- init script end -------------------------


''' BLOB DETECTOR '''
# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 10
params.maxThreshold = 200

# Filter by Area.
params.filterByArea = True
params.minArea = 1500

# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.01

# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3:
    detector = cv2.SimpleBlobDetector(params)
else:
    detector = cv2.SimpleBlobDetector_create(params)


def max_contour(contours):
    max_area = 0
    max_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour
    return max_contour


def testCameraLive():

    camera.resolution = (640, 480)
    camera.framerate = 32

    rawCapture = pia(camera, size=(640, 480))

    sleep(0.1)
    '''
     # Convert the image to grey scale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create a binary image with the defined tresholding
    _, thresh = cv2.threshold(gray_img,230,250,cv2.THRESH_BINARY_INV)

    kernel = np.ones((2,2),np.uint8)

    # Dilate white pixels, so erode the black one
    erosion = cv2.dilate(thresh,kernel,iterations = 1)

    kernel = np.ones((3,3),np.uint8)

    # Erode the white pixels so dilate the black one
    dilatation = cv2.erode(erosion,kernel,iterations = 1)
    cv2.imshow("",dilatation)
    '''
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        from color_detector import color_detector
        res = color_detector(image)

def testCamera():
    print("Camera test")
    camera.start_preview()
    sleep(5)

    # we capture to openCV compatible format
    # you might want to increase resolution

    camera.resolution = (320, 240)
    camera.framerate = 24
    sleep(2)
    image = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(image, 'bgr')

    cv2.imshow('live', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    camera.stop_preview()
    cv2.imwrite('out.png', image)
    print("saved image to out.png")
    print("\nyou can safely quit")


# def testThymio():
#     left_wheel = 20
#     right_wheel = 200
#     asebaNetwork.SendEventName(
#         'motor.target',
#         [left_wheel, right_wheel]
#     )
#     print("motor should be running now")
#     sleep(5)
#     asebaNetwork.SendEventName(
#         'motor.target',
#         [0, 0]
#     )


# NOTE: if you get adafruit_rplidar.RPLidarException: Incorrect descriptor starting bytes
# try disconnecting the usb cable and reconnect again. That should fix the issue
# def lidarScan():
#     print("Starting background lidar scanning")
#     for scan in lidar.iter_scans():
#         if(exit_now):
#             return
#         for (_, angle, distance) in scan:
#             scan_data[min([359, floor(angle)])] = distance


# scanner_thread = threading.Thread(target=lidarScan)
# scanner_thread.daemon = True
# scanner_thread.start()


# def testLidar():
#     print(scan_data)

# ------------------ Main loop here -------------------------


def mainLoop():
    pass
    # do stuff
    # print(scan_data)

    # ------------------- Main loop end ------------------------


if __name__ == '__main__':
    # testCamera()
    testCameraLive()
    # testThymio()
    # testLidar()
    try:
        while True:
            # mainLoop()
            pass
    except KeyboardInterrupt:
        print("STOPPING ROBOT, DO NOT PRESS CTRL-C/Z")
        exit_now = True
        sleep(1)
        # lidar.stop()
        # lidar.disconnect()
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
