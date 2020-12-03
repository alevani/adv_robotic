import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from numpy import sin, cos, pi, sqrt, zeros
import math
import sys
import numpy as np
from random import *
import json
from copy import deepcopy
from time import sleep
import os
from Thymio import Thymio

SPEED = 500
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED)]

robot = Thymio()


def train(epsilon, gamma, lr):
    global Q

    print("----------\n\n\n ONLINE TRAINING \n\n\n----------")
    state = 0
    action_index = 0
    while True:
        try:

            values = robot.get_sensor_state()
            print(values)
            if values == (0, 0):
                new_state = 0
            elif values == (1, 0):
                new_state = 1
            elif values == (0, 1):
                new_state = 2
            else:
                new_state = 3

            ###### Q Learning #######
            if new_state == 0:
                reward = 100
            elif new_state == 1:
                reward = 70
            elif new_state == 2:
                reward = 70
            elif new_state == 3:
                reward = 30

            Q[state, action_index] = Q[state, action_index] + lr * \
                (reward + gamma *
                    np.max(Q[new_state, :]) - Q[state, action_index])

            action_index = None
            state = new_state

            if uniform(0, 1) < epsilon:
                action_index = randint(0, len(ACTIONS)-1)
            else:
                action_index = np.argmax(Q[state])

            left_wheel_velocity, right_wheel_velocity = ACTIONS[action_index]
            robot.drive(left_wheel_velocity, right_wheel_velocity)
            sleep(0.2)
        except KeyboardInterrupt:
            print(Q)
            print("Keyboard interrupt")
            print("Stopping robot")
            robot.drive(0, 0)
            sleep(1)
            os.system("pkill -n asebamedulla")
            print("asebamodulla killed")


epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.8  # up to 1

# -> after 0 epoch
Q = zeros((4, len(ACTIONS)))
Q = np.array([[500., 200., 200.], [200., 200., 500.],
              [200., 500., 200.], [200., 500., 200.]])
train(epsilon, gamma, lr)
