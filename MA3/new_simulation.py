import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
from random import *
from utils import Position
from utils import distance
from copy import deepcopy

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.94  # width of arena
H = 1.18  # height of arena

SPEED = 0.5
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED), (-SPEED, -SPEED)]

ROBOT_TIMESTEP = 0.1        # 1/ROBOT_TIMESTEP equals update frequency of robot
# timestep in kinematics< sim (probably don't touch..)
SIMULATION_TIMESTEP = .01

# the WORLD is a rectangular arena with width W and height H
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

SENSORS_POSITION = [Position(-0.05, 0.06, math.radians(40)), Position(-0.025,
                                                                      0.075, math.radians(18.5)), Position(0, 0.0778, math.radians(0)), Position(0.025, 0.075, math.radians(-18.5)), Position(0.05, 0.06, math.radians(-40))]
Q = zeros((4, 4))
FILE = open("trajectory.dat", "w")


def train(epoch, epsilon, gamma, lr, sensors):
    global Q
    sensors_start_position = deepcopy(sensors)

    for i in range(0, epoch):
        print("Epoch: ", i)
        x = 0.0
        y = 0.0
        a = math.radians(90)
        # TODO changer les sensors en conséquence

        action_index = 0
        state = 1

        sensors = deepcopy(sensors_start_position)

        left_wheel_velocity = SPEED
        right_wheel_velocity = SPEED
