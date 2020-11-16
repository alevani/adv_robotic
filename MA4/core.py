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
            if 1 in sensor_state:
                if sensor_state == (1, 0) or sensor_state == (1, 2):
                    left_motor  =  500
                    right_motor = -500
                    time=0.4
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)

                elif sensor_state == (0, 1) or sensor_state == (2, 1) :
                    left_motor  = -500
                    right_motor =  500
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)
                    time=0.4

                elif sensor_state == (1, 1):
                    left_motor  =  500
                    right_motor = -500
                    time=1.2
                    print('\n motors', left_motor, right_motor)
                    print('sensors', sensor_state)

                else:
                    print("undefined sensor value: ", sensor_state)


            elif sensor_state == (2, 2): # avoider
                left_motor = 0
                right_motor = 0
                thymio.set_led('orange')
                thymio.stop()
                print('waiting for other robot')
                while thymio.receiver != 2:
                    sleep(0.1)
                print('done')
                thymio.stop_transmission(5)
                thymio.set_led('red')

            elif sensor_state == (0, 0):
                # left_motor =  randint(0, 1000)
                # right_motor = randint(0, 1000)
                left_motor =  500
                right_motor = 500

            else:
                print("undefined sensor value: ", sensor_state)
                left_motor =  500
                right_motor = 500

            thymio.drive(left_motor, right_motor)
            if time > 0 :
                print('sleeping for ', time)
            sleep(time)
            # print('sleeping..')

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
