#! /usr/bin/env python3.7
from Thymio import Thymio
from random import randint
from time import sleep
import globals
import os


def main():
    thymio = Thymio()
    thymio.set_info_to_send(2)
    thymio.set_led(globals.BLUE)
    notTagged = True
    try:
        while notTagged:
            sensor_state = thymio.get_sensor_state()
            time = 0 #
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
                thymio.stop()
                thymio.set_led(globals.GREEN)
                thymio.set_info_to_send(1000)

                while thymio.rx != 2:
                    sleep(0.1)
                thymio.drive(1000, 1000,  3)
                thymio.restart()
                thymio.set_led(globals.BLUE)
                sleep(0.1)
                thymio.drive(1000, 1000,  3)
                thymio.restart()
                thymio.set_led(globals.BLUE)

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
                    left_motor =  randint(0, 500)
                    right_motor = randint(0, 500)



            else:
                print("undefined sensor value: ", sensor_state)
                left_motor =  500
                right_motor = 500

            if thymio.rx == 1:
                notTagged = False
                left_motor = 0
                right_motor = 0
                thymio.set_led(globals.PURPLE
                               )
 
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
