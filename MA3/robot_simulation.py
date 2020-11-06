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


def bound_xy(x, y):
    if x > right_border:
        x = right_border - 0.02
    elif x < left_border:
        x = left_border + 0.02

    if y > top_border:
        y = top_border - 0.02
    elif y < bottom_border:
        y = bottom_border + 0.02
    return x, y


def train(epoch, epsilon, gamma, lr, sensors):
    global Q
    imut_s = deepcopy(sensors)

    print("----------\n\n\n TRAINING \n\n\n----------")
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
        update_sensors_pos(sensors, 0, 0, math.radians(90))
        for cnt in range(10000):
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
            new_state = get_state(sensors_values)
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

            Q[state, action_index] = Q[state, action_index] + lr * \
                (reward + gamma *
                    np.max(Q[new_state, :]) - Q[state, action_index])

            action_index = None
            state = new_state

            if uniform(0, 1) < epsilon:
                action_index = randint(0, 3)
            else:
                action_index = np.argmax(Q[state])

            action = ACTIONS[action_index]

            left_wheel_velocity = action[0]
            right_wheel_velocity = action[1]

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
            if cnt % 20 == 0:
                FILE.write(json.dumps(robot_draw))
                FILE.write("\n")

        print(Q)


epoch = 30
epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.8  # up to 1

# -> after 0 epoch
Q = zeros((5, 4))

# -> after 30 epoch
Q = np.array([[367.33065844, 367.31604822, 374.32882045, 478.50111249],
              [500., 500., 500., 500.],
              [429.62138512, 414.26322872, 430.09934211, 499.54848364],
              [228.86190391, 350.94647765, 229.71211325, 488.70948977],
              [0.,  0.,  0.,           0.]])

# -> after 60 epoch
Q = np.array([[369.99554475, 353.98312678, 370.63470555, 499.99999998],
              [499.993344,  499.99996559, 220.,        500.],
              [150.,         150.,         150.,         150., ],
              [423.68993213, 429.71843168, 443.97215264, 499.9992832],
              [0.,           0.,           0.,           0., ]])

epoch = 30
epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.2  # up to 1
# -> after that point, he understand that going backward is a good shot, so we introduced the bottom sensors and a fith state

# -> after 90 epoch and backward train, try now with this Q table and the real life robot.
Q = np.array([[369.9964358, 359.66944091, 423.39774031, 499.97425085],
              [499.99999732, 499.99999839, 499.99999981, 500.],
              [294.06487264, 302.23336612, 392.04913343, 485.97948166],
              [402.88469108, 424.46200914, 445.19314212, 421.93306663],
              [494.45403245, 267.45412931, 239.16202428, 208.38844952]])

train(epoch, epsilon, gamma, lr, SENSORS_POSITION)
# run()
FILE.close()


# with 4 states
# -> after 30 epoch
# Q = np.array([[321.50923495, 334.34584792, 365.98182595, 468.78194103],
#               [500, 500, 500, 500],
#               [410.7222787, 482.64201304, 419.64017922, 424.76266086],
#               [421.07805923, 478.95939229, 497.81728592, 499.56978585]])


# # -> goes backward as the best solution to avoid an obstacle is to run away from it.
# epoch = 30
# epsilon = 0.3  # up to 1
# gamma = 0.8  # up to 0.99
# lr = 0.2  # up to 1
# # -> after 60 epoch
# Q = np.array([[336.33577031, 369.71909863, 286.78809154, 499.99979062],
#               [500, 500, 500, 500],
#               [424.03139507, 415.21783748, 424.82847922, 480.26656155],
#               [383.40508086, 420.54691597, 483.43643064, 457.84480262]])
