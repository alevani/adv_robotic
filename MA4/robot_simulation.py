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

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.94  # width of arena
H = 1.18  # height of arena


class Position:
    def __init__(self, x, y, a=None):
        self.x = x
        self.y = y
        self.a = a

    def __repr__(self):
        return "({}, {})".format(self.x, self.y, self.a)


top_border = H/2  # 0.59
bottom_border = -H/2
right_border = W/2  # 0.97
left_border = -W/2

SPEED = 0.5
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED), (-SPEED, -SPEED)]

ROBOT_TIMESTEP = 0.1        # 1/ROBOT_TIMESTEP equals update frequency of robot
# timestep in kinematics< sim (probably don't touch..)
SIMULATION_TIMESTEP = .01

# the WORLD is a rectangular arena with width W and height H
BLACK_TAPE = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

tresh = 0.10
WORLD = LinearRing([(W/2 + tresh, H/2 + tresh), (-W/2 - tresh, H/2 + tresh),
                    (-W/2 - tresh, -H/2 - tresh), (W/2 + tresh, -H/2 - tresh)])

SENSORS_POSITION = [Position(-0.0097, 0.074),
                    Position(0.0097, 0.074)]


FILE = open("trajectory.json", "w")


def simulationstep(x, y, q, left_wheel_velocity, right_wheel_velocity):
    # step model time/timestep times
    for step in range(int(ROBOT_TIMESTEP/SIMULATION_TIMESTEP)):
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)

        x += v_x * SIMULATION_TIMESTEP
        y += v_y * SIMULATION_TIMESTEP
        q += omega * SIMULATION_TIMESTEP
    return x, y, q


def get_state(sensors_values):
    left = sensors_values[0]
    right = sensors_values[1]

    if (left, right) == (0, 0):
        return 0
    elif (left, right) == (1, 0):
        return 1
    elif (left, right) == (0, 1):
        return 2
    elif (left, right) == (1, 1):
        return 3


def get_sensors_values(sensors):
    box_left = Point(sensors[0].x, sensors[0].y).buffer(0.05)
    box_right = Point(sensors[1].x, sensors[1].y).buffer(0.05)

    return (0 if Polygon(BLACK_TAPE).contains(box_left) else 1, 0 if Polygon(BLACK_TAPE).contains(box_right) else 1)


def has_collided(x, y, a):
    a = a - math.radians(90)

    box_x = 0.0525
    box_y_top = 0.0725 + 0.03
    box_y_bottom = 0.0725 - 0.03

    collision_box = Polygon(
        ((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
         (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom)))
    collision_box = rotate(collision_box, a, (x, y), use_radians=True)

    bpos = []
    x, y = collision_box.exterior.coords.xy

    return collision_box.intersects(WORLD), tuple(zip(x, y))


def update_sensors_pos(sensors, x, y):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
    return sensors


def rotate_all_pos(sensors, x, y, a):
    for pos in sensors:
        point = rotate(Point(pos.x, pos.y), a,
                       (x, y), use_radians=True)
        pos.x = point.x
        pos.y = point.y

    return sensors


def train(epoch, sensors):
    global Q
    print(Q)
    imut_s = deepcopy(sensors)

    print("----------\n\n\n RUNNING \n\n\n----------")
    for i in range(0, epoch):
        print("Epoch: ", i)
        x = 0.0   # robot position in meters - x direction - positive to the right
        y = 0.0   # robot position in meters - y direction - positive up
        # robot heading with respect to x-axis in radians
        q = math.radians(90)
        action_index = 0
        state = 1
        sensors = deepcopy(imut_s)
        left_wheel_velocity = SPEED   # robot left wheel velocity in radians/s
        right_wheel_velocity = SPEED  # robot right wheel velocity in radians/s
        update_sensors_pos(sensors, 0, 0)
        for cnt in range(10000):
            robot_draw = {
                'rpos': [],
                'spos': [],
                'bpos': []
            }

            robot_position = Position(x, y, q)

            # use __dict__ to make it jsonable
            robot_draw['rpos'] = robot_position.__dict__

            sensors_values = get_sensors_values(sensors)

            robot_draw['spos'] = [(sensors[0].x, sensors[0].y),
                                  (sensors[1].x, sensors[1].y)]

            ###### Q Learning #######
            state = get_state(sensors_values)

            left_wheel_velocity, right_wheel_velocity = ACTIONS[np.argmax(
                Q[state])]

            # # step simulation
            new_x, new_y, new_q = simulationstep(
                x, y, q, left_wheel_velocity, right_wheel_velocity)

            # new_x, new_y = bound_xy(new_x, new_y)

            sensors = update_sensors_pos(
                sensors, new_x - x, new_y - y)
            sensors = rotate_all_pos(sensors, new_x, new_y, new_q-q)

            x = new_x
            y = new_y
            q = new_q

            # # check collision with arena walls
            collided, box_position = has_collided(x, y, q)
            robot_draw['bpos'] = deepcopy(box_position)

            if collided:
                print("collided")
                break
            if cnt % 20 == 0:
                FILE.write(json.dumps(robot_draw))
                FILE.write("\n")


Q = [[500.,  500.,          500., ],
     [182.78982847,  181.26465671, 443.38240004],
     [-181.78253385, 500, -148.97787374],
     [-349.99999961, 500, -349.99999962]]
epoch = 200


train(epoch, SENSORS_POSITION)
FILE.close()
