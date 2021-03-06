from Thymio import Thymio
from random import randint
from time import sleep
import numpy as np
from lidar import Lidar
import globals
import os


def main():
    # l = Lidar()
    thymio = Thymio()
    thymio.set_info_to_send(1)
    thymio.set_led(globals.RED)
    notTagged = True
    try:
        while notTagged:
            sensor_state = thymio.get_sensor_state()
            time = 0
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

            elif sensor_state == (2, 2):
                left_motor = 500
                right_motor = -500

            elif sensor_state == (0, 0):
                prox_state = thymio.get_prox_state()

                # ? add time
                # ? speed
                # ? use back sensor to get away from the seeker?
                if prox_state == (1, 0, 1):
                    left_motor = -200
                    right_motor = 200
                elif prox_state == (0, 0, 1):
                    left_motor = 200
                    right_motor = -200
                elif prox_state == (1, 0, 0) or prox_state == (0, 1, 0):
                    left_motor = -200
                    right_motor = 200
                else:
                    left_motor = randint(0, 700)
                    right_motor = randint(0, 700)
                # left_motor = 500
                # right_motor = 500
                # time = 0.1
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
                print("undefined sensor value: ", sensor_state)
                left_motor = 500
                right_motor = 500

            if thymio.rx == 1:
                notTagged = False
                left_motor = 0
                right_motor = 0
                thymio.set_led(globals.PURPLE
                               )

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
    main()
