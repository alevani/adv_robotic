import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
import math
import sys
import numpy as np
import json
from random import *
from utils import Position
from utils import distance


# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.94  # width of arena
H = 1.18  # height of arena
SPEED = 0.5
ACTIONS = [(SPEED, SPEED), (-SPEED, SPEED), (SPEED, -SPEED), (-SPEED, -SPEED)]

ROBOT_TIMESTEP = 0.1        # 1/ROBOT_TIMESTEP equals update frequency of robot
# timestep in kinematics< sim (probably don't touch..)
SIMULATION_TIMESTEP = .001

# the WORLD is a rectangular arena with width W and height H
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

SENSORS_POSITION = [Position(-0.05,   0.06, math.radians(40)),
                    Position(-0.025,  0.075, math.radians(18.5)),
                    Position(0, 0.0778, math.radians(0)),
                    Position(0.025,  0.025, math.radians(-18.5)),
                    Position(0.05,   0.06, math.radians(-40))]


FILE = open("trajectory.dat", "w")


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


def create_rays(pos, robot_position):
    nx = pos.x + robot_position.x
    ny = pos.y + robot_position.y
    na = pos.a + robot_position.a
    return LineString([(nx, ny), (nx+cos(na)*2*W, (ny+sin(na)*2*H))])


def get_state(sensors_values):
    # print(sensors_values)
    top = sensors_values[2]
    leftest = sensors_values[0]
    left = sensors_values[1]
    right = sensors_values[3]
    rightest = sensors_values[4]
    print(sensors_values)
    if top < 0.7 and leftest < 0.05:
        return 2
    elif top < 0.7 and rightest < 0.05:
        return 3
    elif top < 0.05:
        return 0
    else:
        return 1


def is_colliding(x, y, a):
    a = a - math.radians(90)
    print("entry points: ", x, y, a)
    box_x = 0.0525
    box_y_top = 0.0725 + 0.03
    box_y_bottom = 0.0725 - 0.03

    collision_box = Polygon(
        ((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
         (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom)))

    collision_box = rotate(collision_box, a, (x, y), use_radians=True)
    return collision_box.intersects(WORLD)


def train(epoch, epsilon, gamma, lr):
    global Q

    # print("----------\n\n\n TRAINING \n\n\n----------")

    left_wheel_velocity = SPEED   # robot left wheel velocity in radians/s
    right_wheel_velocity = SPEED  # robot right wheel velocity in radians/s
    for i in range(0, epoch):
        # print("Epoch: ", i)
        x = 0.3   # robot position in meters - x direction - positive to the right
        y = 0.5   # robot position in meters - y direction - positive up
        # robot heading with respect to x-axis in radians
        q = math.radians(45)
        action_index = 0
        state = 1
        pygame_drawings = []
        for cnt in range(10000):
            robot_draw = {
                'rpos': [],
                'spos': []
            }
            robot_position = Position(x, y, q)
            # use __dict__ to make it jsonable
            robot_draw['rpos'] = robot_position.__dict__
            rays = []
            # create rays
            for i, spos in enumerate(SENSORS_POSITION):
                # nx = spos.x + robot_position.x
                # ny = spos.y + robot_position.y
                na = (spos.a + robot_position.a) % 360
                start_ray = (robot_position.x, robot_position.y)
                end_ray = (robot_position.x + cos(na)*2*W,
                           robot_position.y + sin(na)*2*H)
                robot_draw['spos'].append((start_ray, end_ray))
                ray = LineString([start_ray, end_ray])
                rays.append(ray)
            print(robot_draw)
            print(json.dumps(robot_draw))

            # rays = [create_rays(pos, robot_position)
            #         for pos in SENSORS_POSITION]  # ! Might be a problem. imagine if robot is (0,0,180) and then you add
            #! sensors positions, would the ray be pointing at 180°?

            sensors_values = [
                distance(WORLD.intersection(ray), x + SENSORS_POSITION[index].x, y + SENSORS_POSITION[index].y) for index, ray in enumerate(rays)]  # ! same problem as above?

            new_state = get_state(sensors_values)

            if new_state == 0:
                reward = -30
            elif new_state == 2:
                reward = 30
            elif new_state == 3:
                reward = 30
            elif new_state == 1:
                reward = 100

            Q[state, action_index] = Q[state, action_index] + lr * \
                (reward + gamma *
                    np.max(Q[new_state, :]) - Q[state, action_index])

            # Set the percent you want to explore
            action_index = None
            state = new_state

            if uniform(0, 1) < epsilon:
                action_index = randint(0, 3)
            else:
                action_index = np.argmax(Q[state])

            action = ACTIONS[action_index]
            action = ACTIONS[0]

            left_wheel_velocity = action[0]
            right_wheel_velocity = action[1]

            # step simulation
            x, y, q = simulationstep(
                x, y, q, left_wheel_velocity, right_wheel_velocity)

            # check collision with arena walls
            if is_colliding(x, y, q):
                print(x, y)
                print("collided")
                print(WORLD.distance(Point(x, y)))
                print("\n\n\n")
                sys.exit(0)
                break
            if cnt % 30 == 0:
                FILE.write(str(x) + ", " + str(y) + ", " +
                           str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")
        print(Q)


def run():
    global Q
    print("----------\n\n\n RUNNING \n\n\n----------")

    x = 0.0   # robot position in meters - x direction - positive to the right
    y = 0.0   # robot position in meters - y direction - positive up
    # robot heading with respect to x-axis in radians
    q = math.radians(90.0)
    for cnt in range(10000):
        robot_position = Position(x, y, q)

        rays = [create_rays(pos, robot_position)
                for pos in SENSORS_POSITION]
        sensors_values = [
            distance(WORLD.intersection(ray), x, y) for ray in rays]

        state = get_state(sensors_values)

        action_index = np.argmax(Q[state])
        action = ACTIONS[action_index]

        left_wheel_velocity = action[0]
        right_wheel_velocity = action[1]

        # step simulation
        x, y, q = simulationstep(
            x, y, q, left_wheel_velocity, right_wheel_velocity)

        # check collision with arena walls
        if is_colliding(x, y, q):
            print(x, y)
            print("collided")
            print(WORLD.distance(Point(x, y)))
            print("\n\n\n")
            break

        if cnt % 30 == 0:
            FILE.write(str(x) + ", " + str(y) + ", " +
                       str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")


epoch = 10
epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.7  # up to 1

Q = zeros((4, 4))

train(epoch, epsilon, gamma, lr)
run()
FILE.close()
