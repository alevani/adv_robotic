#! /usr/bin/env python3.7
from Thymio import Thymio
from random import randint
from time import sleep
from lidar import Lidar
import numpy as np
import globals
import os


def main():
    l = Lidar()
    thymio = Thymio()
    thymio.set_info_to_send(2)
    thymio.set_led(globals.RED)
    notTagged = True
    try:
        while notTagged:
            sensor_state = thymio.get_sensor_state()
            time = 0
            print(sensor_state)
            if 1 in sensor_state:
                if sensor_state == (1, 0) or sensor_state == (1, 2):
                    left_motor = 500
                    right_motor = -500
                    time = 0.4

                elif sensor_state == (0, 1) or sensor_state == (2, 1):
                    left_motor = -500
                    right_motor = 500

                    time = 0.4

                elif sensor_state == (1, 1):
                    left_motor = 500
                    right_motor = -500
                    time = 1.2

                else:
                    pass

            elif sensor_state == (2, 2):  # avoider
                # drive in the zone
                thymio.drive(500, 500)
                sleep(0.6)

                left_motor = 0
                right_motor = 0
                thymio.stop()
                thymio.set_led(globals.ORANGE)
                thymio.set_info_to_send(500)

                while thymio.rx[0] != 2:
                    thymio.drive(100, -100)
                    sleep(0.1)
                thymio.rx[0] = 500
                thymio.restart()
                thymio.drive(500, 500)
                sleep(1.3)
            elif sensor_state == (2, 0):
                left_motor = -500
                right_motor = 500
                time = 0.4
            elif sensor_state == (0, 2):
                left_motor = 500
                right_motor = -500
                time = 0.4
            elif sensor_state == (0, 0):
                prox_state = thymio.get_prox_state()

                # ? add time
                # ? speed
                # ? use back sensor to get away from the seeker?
                if prox_state == (1, 0, 1):
                    left_motor = -500
                    right_motor = 500
                elif prox_state == (0, 0, 1):
                    left_motor = -500
                    right_motor = 500
                elif prox_state == (1, 0, 0) or prox_state == (0, 1, 0):
                    left_motor = 500
                    right_motor = -500
                else:
                    left_motor = 500
                    right_motor = 500
                    time = 0.1
                    data = l.get_scan_data()
                    index = np.argmin(data)
                    # 500 - ((180 - 90) * 500 / 180)
                    if index < 180:
                        new_index = 180 - index
                        right_motor = (new_index * 500 / 180)
                        # print("LEFT")
                    elif index > 179:
                        new_index = index - 180
                        left_motor = (new_index * 500 / 180)
                        # print("RIGHT")
                        # print("index: ", new_index)
                        # print("power left: ", left_motor)
                        # print("power right: ", right_motor)
            else:
                print("undefined sensor value: ", sensor_state)
                left_motor = 500
                right_motor = 500

            if thymio.rx[0] == 1:
                notTagged = False
                left_motor = 0
                right_motor = 0
                thymio.set_led(globals.PURPLE
                               )
            thymio.drive(left_motor, right_motor)
            sleep(time)

    except KeyboardInterrupt:
        print("Keyboard interrupt")
        print("Stopping robot")
        thymio.drive(0, 0)
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")


if __name__ == '__main__':
    os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
    main()
