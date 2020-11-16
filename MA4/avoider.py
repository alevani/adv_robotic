'''
SPRINT 1
- Basic requirements (LEDs.. Comm..)
    - turn LED blue
    - turn LED green if in safe zone
    - stand still if receive 1
    - transmit 2.
    - If in safe zone and receive 2
        -  leave safe zone
        - wait 5 sec to transmit 2 again
- Random walk in the arena
- Behaviour based wall avoidance
- Behaviour based safe zone detection

SPRINT 2
- safe zone color detection
- seeker avoidance color based

SPRINT 3
- Learning?
'''
#! /usr/bin/env python3.7
import Thymio
from random import randint
import globals
from time import sleep
import os


def main():
    thymio = Thymio()
    thymio.set_info_to_send(2)
    thymio.set_led(globals.BLUE)
    notTagged = True
    try:
        while notTagged:

            sensor_state = thymio.get_sensor_state()
            time = 0

            if sensor_state == (1, 0):
                left_motor = 500
                right_motor = -500
                time = 1

            elif sensor_state == (0, 1):
                left_motor = -500
                right_motor = 500
                time = 1

            elif sensor_state == (1, 1):
                left_motor = 500
                right_motor = -500
                time = 0.7

            elif sensor_state == (2, 2):  # avoider
                thymio.drive(0, 0)
                thymio.set_led(globals.GREEN)
                thymio.set_info_to_send(1000)

                while thymio.rx != 2:
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
                    left_motor = -1000
                    right_motor = 1000
                elif prox_state == (0, 0, 1):
                    left_motor = -1000
                    right_motor = 1000
                elif prox_state == (1, 0, 0) or prox_state == (0, 1, 0):
                    left_motor = 1000
                    right_motor = -1000
                else:
                    left_motor = randint(-1000, 1000)
                    right_motor = randint(-1000, 1000)

            else:
                print("undefined sensor value: ", sensor_state)

            if thymio.rx == 1:
                notTagged = False
                left_motor = 0
                right_motor = 0
                thymio.set_led(globals.PURPLE
                               )
            thymio.drive(left_motor, right_motor, time=time)

    except KeyboardInterrupt:
        print("Keyboard interrupt")
        print("Stopping robot")
        thymio.drive(0, 0)
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")

        thymio.drive(left_motor, right_motor)


if __name__ == '__main__':
    main()
