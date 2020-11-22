#! /usr/bin/env python3.7
from Thymio import Thymio
from random import randint
from time import sleep
import globals
from color_detector import find_prey, Blob, get_width_cam, start_thread_video
import os


def main():

    thymio = Thymio()
    thymio.set_info_to_send(1)
    thymio.set_led(globals.RED)
    notTagged = True

    try:
        while notTagged:
            sensor_state = thymio.get_sensor_state()
            time = 0.2
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

            elif sensor_state == (2, 2):  # avoider
                left_motor = 500
                right_motor = -500

            elif sensor_state == (0, 0):
                prey = find_prey()
                print(prey)

                left_motor = 1000
                right_motor = 1000

                if prey == None:  # No pray upfront
                    print("NO PREY, RANDOM ")
                    left_motor = randint(0, 1000)
                    right_motor = randint(0, 1000)
                else:
                    print("PREY FOUND")
                    value_to_decrease = abs(prey.d2c) * 1000 / globals.MAX_D2C

                    if prey.d2c == 0:
                        left_motor = 1000
                        right_motor = 1000
                    if prey.d2c < 0:
                        left_motor = 1000 - value_to_decrease
                    elif prey.d2c > 0:
                        right_motor  = 1000 - value_to_decrease

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

            print("right_motor", right_motor)
            print("left_motor", left_motor)
            # thymio.drive(left_motor, right_motor)
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
