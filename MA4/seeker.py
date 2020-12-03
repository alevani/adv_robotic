from Thymio import Thymio
from random import randint
from time import sleep
import numpy as np
from lidar import Lidar
import globals
import os

Q = [[500.,      500.,     500.,     500.],
     [466.64332349,  290.81018532, 303.2886649, 499.95643249],
     [276.53894095, 365.71203966, 365.68375976, 499.99973376],
     [-63.55928509, -108.10324207, -147.71559015, 276.32008158]]

SPEED = 500
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED), (-SPEED, -SPEED)]


def argmin_ban(list, bans):
    mi = 5001
    index = 1000
    for k, v in enumerate(list):
        if v < mi and k not in bans:
            mi = v
            index = k
    return index


def main():
    l = Lidar()
    thymio = Thymio()
    thymio.set_info_to_send(1)
    thymio.set_led(globals.RED)
    while True:
        try:
            left_motor = 0
            right_motor = 0
            state = -1
            sensor_state = thymio.get_sensor_state()
            time = 0
            if 1 in sensor_state:
                if sensor_state == (1, 2):
                    # left_motor = 500
                    # right_motor = -500

                    time = 0.4
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)

                elif sensor_state == (2, 1):
                    # left_motor = -500
                    # right_motor = 500

                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)
                    time = 0.4
                elif sensor_state == (1, 0):
                    state = 1
                    time = 0.2
                elif sensor_state == (0, 1):
                    state = 2
                    time = 0.2
                elif sensor_state == (1, 1):
                    state = 3
                    time = 0.2
                else:
                    print("undefined sensor value: ", sensor_state)

            elif sensor_state == (2, 2):
                # left_motor = 500
                # right_motor = -500
                pass

            elif sensor_state == (0, 0):

                left_motor = 500
                right_motor = 500
                time = 0.2
                data = l.get_scan_data()

                index = argmin_ban(
                    data, [])
                print("argmin: ", index)

                print(data[index])
                if index < 180:
                    new_index = 180 - index
                    shift = (new_index * 500 / 180)  #  500 or 0 1000 or 0
                    shift *= 2
                    right_motor -= shift
                    left_motor += shift
                    print("LEFT")
                    print("new index, :", new_index)
                    print("left: ", left_motor)
                    print("right: ", right_motor)
                elif index > 179:
                    new_index = index - 180
                    shift = (new_index * 500 / 180)
                    shift *= 2
                    right_motor += shift
                    left_motor -= shift
                    print("RIGHT")
                    print("new index, :", new_index)
                    print("left: ", left_motor)
                    print("right: ", right_motor)

            else:
                print("undefined sensor value: ", sensor_state)
                left_motor = 500
                right_motor = 500

            if state != -1:
                action_index = np.argmax(Q[state])
                left_motor, right_motor = ACTIONS[action_index]

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
