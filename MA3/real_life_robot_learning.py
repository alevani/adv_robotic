#!/usr/bin/python3
import dbus.mainloop.glib
import dbus
import os
from time import sleep
from numpy import sin, cos, pi, sqrt, zeros
import numpy as np
import threading
from random import uniform, randint

os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")

SPEED = 200
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED), (-SPEED, -SPEED)]

# -> after 0 epoch
Q = zeros((6, 4))

Q = np.array([[193.38523951 - 124.75660773,  368.03106067,  271.08635208],
              [497.86800903, 489.12481136, 492.98011406,  488.32601119],
              [272.27422576, 271.30298892, 255.15523551, 219.300659],
              [-20.74843692, -51.95336118, -25.79651922, 465.62617088],
              [-39.82916913, 461.80326017, -39.25137081, 169.07727127],
              [-405.37098974, 34.53929659, -412.54938562,  39.08051556]])

epoch = 30
epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.8  # up to 1


class Thymio:
    def __init__(self):
        self.setup()

    def setup(self):
        print("Setting up")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        self.asebaNetworkObject = bus.get_object("ch.epfl.mobots.Aseba", "/")

        self.asebaNetwork = dbus.Interface(
            self.asebaNetworkObject, dbus_interface="ch.epfl.mobots.AsebaNetwork"
        )
        # load the file which is run on the thymio
        self.asebaNetwork.LoadScripts(
            "thympi.aesl", reply_handler=self.dbusError, error_handler=self.dbusError
        )

        sleep(3)
        self.sense()

    def sense(self):
        self.prox_horizontal = self.asebaNetwork.GetVariable(
            "thymio-II", "prox.horizontal")
        threading.Timer(.2, self.sense).start()

    def dbusError(self, e):
        print("dbus error: %s" % str(e))

    def getSensorValues(self):
        self.SC = self.prox_horizontal[2]  # Sensor Central
        self.SL = self.prox_horizontal[0]  # Sensor Left
        self.SR = self.prox_horizontal[4]  # Sensor Right
        self.BL = self.prox_horizontal[5]  # Sensor back left
        self.BR = self.prox_horizontal[6]  # Sensor back right

    def getCurrentState(self):
        self.getSensorValues()

        if self.SR > 2650 and self.SL > 2750:
            CurrentState = 5
        elif self.SR > 2650:
            CurrentState = 3  # apporximately 6 cm from wall, robot has angle towards wall
        elif self.SL > 2750:
            CurrentState = 2  # apporximately 6 cm from wall, robot has angle towards wall
        elif self.SC > 1500:
            # approximately 10 cm from wall, robot has not or very small angle towards wall
            CurrentState = 0
        elif self.BL > 1500 or self.BR > 1500:
            CurrentState = 4
        else:
            CurrentState = 1  # no obstacle detected

        return CurrentState

    def drive(self, l, r):
        self.asebaNetwork.SendEventName('motor.target', [l, r])
        sleep(.2)

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.asebaNetwork.SendEventName(
            "motor.target", [left_wheel, right_wheel])


if __name__ == '__main__':
    try:
        robot = Thymio()
        action_index = 0
        state = 1
        while True:

            ###### Q Learning #######
            new_state = robot.getCurrentState()
            if new_state == 0:
                reward = -30
            elif new_state == 2:
                reward = 30
            elif new_state == 3:
                reward = 30
            elif new_state == 1:
                reward = 100
            elif new_state == 4:
                reward = -30
            elif new_state == 5:
                reward = - 100

            Q[state, action_index] = Q[state, action_index] + lr * \
                (reward + gamma *
                    np.max(Q[new_state, :]) - Q[state, action_index])

            state = new_state
            if uniform(0, 1) < epsilon:
                action_index = randint(0, 3)
            else:
                action_index = np.argmax(Q[state])

            left_wheel_velocity, right_wheel_velocity = ACTIONS[action_index]

            robot.drive(left_wheel_velocity, right_wheel_velocity)
            print(Q)

    except KeyboardInterrupt:
        print("Stopping robot")
        robot.stop()
        exit_now = True
        sleep(1)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
