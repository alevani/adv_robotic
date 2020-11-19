from Thymio import Thymio
from random import randint
from time import sleep
import globals
import os


def find_best_prey():
    return 0, 0, 0


def main():

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

            elif sensor_state == (2, 2):  # avoider
                left_motor = 500
                right_motor = -500

            elif sensor_state == (0, 0):
                area, d2c, d2b = find_best_prey()

                left_motor = 1000
                right_motor = 1000

                if (area, d2c, d2b) == (None, None, None):  # No pray upfront
                    left_motor = randint(0, 1000)
                    right_motor = randint(0, 1000)
                else:
                    value_to_decrease = d2c * 1000 / globals.MAX_DOC

                    if d2c == 0:
                        left_motor = 1000
                        right_motor = 1000
                    if d2c < 0:
                        left_motor = 1000 - value_to_decrease
                    elif d2c > 0:
                        right_motor = 1000 - value_to_decrease

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
