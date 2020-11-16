#! /usr/bin/env python3.7
from Thymio import Thymio
from random import randint
from time import sleep
import os


def main():
    thymio = Thymio()
    try:
        while True:
            sensor_state = thymio.get_sensor_state()
            time=0 # 

            if sensor_state == (1, 0):
                left_motor  =  500
                right_motor = -500
                time=1

            elif sensor_state == (0, 1):
                left_motor  = -500
                right_motor =  500
                time=1

            elif sensor_state == (1, 1):
                left_motor  =  500
                right_motor = -500
                time=0.7

            elif sensor_state == (2, 2): # avoider
                left_motor = 0
                right_motor = 0
                thymio.set_led('orange')
                while thymio.receiver != 2:
                    sleep(0.1)
                thymio.stop_transmission(5)
                thymio.set_led('red')
                print('waiting for other robot')

            elif sensor_state == (0, 0):
                # left_motor =  randint(0, 1000)
                # right_motor = randint(0, 1000)
                left_motor =  500
                right_motor = 500

            else:
                print("undefined sensor value: ", sensor_state)

            thymio.drive(left_motor, right_motor, time=time)
            print('\n motors', left_motor, right_motor)
            print('sensors', sensor_state)

    except KeyboardInterrupt:
        print("Keyboard interrupt")
        print("Stopping robot")
        thymio.drive(0,0)
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")


if __name__ == '__main__':
    os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
    main()
