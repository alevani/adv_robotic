import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
import math
import sys
import numpy as np
from random import *
from utils import Position
from utils import distance
import json
from copy import deepcopy

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.94  # width of arena
H = 1.18  # height of arena


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
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

SENSORS_POSITION = [Position(-0.05, 0.06, math.radians(40)), Position(-0.025,
                                                                      0.075, math.radians(18.5)), Position(0, 0.0778, math.radians(0)), Position(0.025, 0.075, math.radians(-18.5)), Position(0.05, 0.06, math.radians(-40)), Position(-0.03, -0.03, math.radians(180)), Position(0.03, -0.03, math.radians(180))]


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


def create_rays(sensors):
    rays = []
    spos = []
    for sensor in sensors:
        nx = sensor.x
        ny = sensor.y
        na = sensor.a
        nx_end = nx+cos(na)*2*W
        ny_end = ny+sin(na)*2*H
        spos.append([(nx, ny), (nx_end, ny_end)])
        rays.append(LineString([(nx, ny), (nx_end, ny_end)]))
    return rays, spos


def get_state(sensors_values):
    top = sensors_values[2]
    leftest = sensors_values[0]
    left = sensors_values[1]
    right = sensors_values[3]
    rightest = sensors_values[4]
    bottom_left = sensors_values[5]
    bottom_right = sensors_values[6]

    tr = 0.02
    if top < 0.07 + tr and leftest < 0.05 + tr:
        return 2
    elif top < 0.07 + tr and rightest < 0.05 + tr:
        return 3
    elif top < 0.03 + tr:
        return 0
    elif bottom_left < 0.03 + tr or bottom_right < 0.03 + tr:
        return 4
    else:
        return 1


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


def update_sensors_pos(sensors, x, y, a):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.a = pos.a + a
    return sensors


def rotate_all_pos(sensors, x, y, a):
    for pos in sensors:
        point = rotate(Point(pos.x, pos.y), a,
                       (x, y), use_radians=True)
        pos.x = point.x
        pos.y = point.y

    return sensors


def simulate(Q, ttl):
    x = 0.0   # robot position in meters - x direction - positive to the right
    y = 0.0   # robot position in meters - y direction - positive up
    # robot heading with respect to x-axis in radians
    q = math.radians(90)
    action_index = 0
    state = 1
    sensors = deepcopy(SENSORS_POSITION)
    left_wheel_velocity = SPEED   # robot left wheel velocity in radians/s
    right_wheel_velocity = SPEED  # robot right wheel velocity in radians/s
    update_sensors_pos(sensors, 0, 0, math.radians(90))
    fitness = 0
    for _ in range(ttl):
        robot_draw = {
            'rpos': [],
            'spos': [],
            'bpos': []
        }

        robot_position = Position(x, y, q)

        # use __dict__ to make it jsonable
        robot_draw['rpos'] = robot_position.__dict__

        rays, spos = create_rays(sensors)

        robot_draw['spos'] = deepcopy(spos)

        sensors_values = [
            distance(WORLD.intersection(ray), sensors[index].x, sensors[index].y) for index, ray in enumerate(rays)]

        ###### Q Learning #######
        state = get_state(sensors_values)
        if state == 1:
            fitness += 1

        action_index = np.argmax(Q[state])

        left_wheel_velocity, right_wheel_velocity = ACTIONS[action_index]

        # # step simulation
        new_x, new_y, new_q = simulationstep(
            x, y, q, left_wheel_velocity, right_wheel_velocity)

        # new_x, new_y = bound_xy(new_x, new_y)

        sensors = update_sensors_pos(
            sensors, new_x - x, new_y - y, new_q - q)
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
    FILE.close
    return fitness
