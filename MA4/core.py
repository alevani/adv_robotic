#! /usr/bin/env python3.7
import Thymio
from random import randint
from time import sleep


def main():
    thymio = Thymio()
    while True:

        sensor_state = thymio.get_sensor_state()

        if sensor_state == (1, 0):
            left_motor = 1000
            right_motor = 0

        elif sensor_state == (0, 1) or sensor_state == (1, 1):
            left_motor = 0
            right_motor = 1000

        elif sensor_state == (2, 2): # avoider
            left_motor = 0
            right_motor = 0
            thymio.set_led('orange')
            while thymio.receiver != 2:
                sleep(0.1)
            thymio.stop_transmission(5)
            thymio.set_led('red')

        elif sensor_state(0, 0):
            left_motor = randint(-1000, 1000)
            right_motor = randint(-1000, 1000)

        else:
            print("undefined sensor value: ", sensor_state)

        thymio.drive(left_motor, right_motor)


if __name__ == '__main__':
    main()

