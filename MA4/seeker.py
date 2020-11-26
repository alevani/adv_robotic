#! /usr/bin/env python3.7
from Thymio import Thymio
from random import randint
import numpy as np
from time import sleep
import numpy as np
from lidar import Lidar
import globals
from lidar import Lidar
from color_detector import find_prey, Blob, get_width_cam, start_thread_video
import os


def main():
    # l = Lidar()
    thymio = Thymio()
    thymio.set_info_to_send(1)
    thymio.set_led(globals.RED)
    notTagged = True
    LAST_D2C = 0

    try:
        while notTagged:
            sensor_state = thymio.get_sensor_state()
            time = 0.2

            # BORDER AVOIDANCE
            if 1 in sensor_state:
                if sensor_state == (1, 0) or sensor_state == (1, 2):
                    left_motor = 500
                    right_motor = -500

                    time = 0.4
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)

                elif sensor_state == (0, 1) or sensor_state == (2, 1):
                    left_motor = -500
                    right_motor = 500

                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)
                    time = 0.4

                elif sensor_state == (1, 1):
                    left_motor = 500
                    right_motor = -500

                    time = 1.2
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)

                else:
                    print("undefined sensor value: ", sensor_state)

            # SAFE ZONE AVOIDANCE
            elif sensor_state == (2, 2):  # avoider
                left_motor = 500
                right_motor = -500

            # MAIN LOGIC
            elif sensor_state == (0, 0):

                prey = find_prey()
                print(prey)

                left_motor = 1000
                right_motor = 1000

                if prey is None:  # No pray upfront
                    print("NO PREY, RANDOM")
                    if LAST_D2C < 0:
                        left_motor  = -500
                        right_motor =  500
                    else:
                        left_motor  =  500
                        right_motor = -500

                    time = 0.1


                    # data = l.get_scan_data()
                    # index = np.argmin(data)

                    # if index < 180:
                    #     new_index = 180 - index
                    #     shift = (new_index * 500 / 180)  #  500 or 0 1000 or 0
                    #     shift *= 2
                    #     right_motor += shift
                    #     left_motor -= shift
                    # elif index > 179:
                    #     new_index = index - 180
                    #     shift = (new_index * 500 / 180)
                    #     shift *= 2
                    #     right_motor -= shift
                    #     left_motor += shift

                else:
                    print("PREY FOUND")
                    value_to_decrease = 1000 * abs(prey.d2c) / globals.MAX_D2C

                    if prey.d2c == 0:
                        left_motor  = 1000
                        right_motor = 1000
                    if prey.d2c < 0:
                        left_motor  = 1000 - value_to_decrease
                    elif prey.d2c > 0:
                        right_motor = 1000 - value_to_decrease
            else:
                print("\n\n\n UNDEFINED SENSOR VALUE: ", sensor_state)
                left_motor  = 500
                right_motor = 500

            if thymio.rx == 1:
                notTagged   = False
                left_motor  = 0
                right_motor = 0
                thymio.set_led(globals.PURPLE)

            print("right_motor", right_motor)
            print("left_motor", left_motor)
            thymio.drive(left_motor, right_motor)
            if time > 0:
                print('sleeping for ', time)
            sleep(time)
            # print('sleeping..')

    except KeyboardInterrupt:
        print("Keyboard interrupt")
        print("Stopping robot")
        thymio.drive(0, 0)
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")


if __name__ == '__main__':
    os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
    print('starting asebamedulla')
    sleep(1)
    cam_w = get_width_cam()
    globals.MAX_D2C = cam_w / 2
    print(globals.MAX_D2C)
    print('start threat')
    start_thread_video()
    sleep(1)
    print('start main')
    main()
