import shapely
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
import math
import numpy as np
from random import *
from utils import Position
from utils import distance

epsilon = 0.3  # up to 1
gamma = 0.8  # up to 0.99
lr = 0.7  # up to 1

speed = 0.5

actions = [(speed, speed), (-speed, speed), (speed, -speed), (-speed, -speed)]
Q = zeros((2, 4))


# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.94  # width of arena
H = 1.18  # height of arena

robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
# timestep in kinematics< sim (probably don't touch..)
simulation_timestep = .1

# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

# First foward motion
left_wheel_velocity = speed   # robot left wheel velocity in radians/s
right_wheel_velocity = speed  # robot right wheel velocity in radians/s
#! induire que les murs sont bien reeles

# Order is : Top, left most, second to left, second to right, right most
sensors_position = [Position(-0.05, 0.06, math.radians(40)), Position(-0.025,
                                                                      0.075, math.radians(18.5)), Position(0, 0, math.radians(0)), Position(0.05, 0.06, math.radians(-40)), Position(0.025, 0.025, math.radians(-18.5))]
#Position(0, 0.0778, 0)


file = open("trajectory.dat", "w")
epoch = 10


def simulationstep(x, y, q):
    # step model time/timestep times
    for step in range(int(robot_timestep/simulation_timestep)):
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)

        x += v_x * simulation_timestep
        y += v_y * simulation_timestep
        q += omega * simulation_timestep
    return x, y, q


def create_rays(pos, robot_position):
    nx = pos.x + robot_position.x
    ny = pos.y + robot_position.y
    na = pos.a + robot_position.a
    return LineString([(nx, ny), (nx+cos(na)*2*W, (ny+sin(na)*2*H))])


def get_state(top):
    # si on veut que ça marche il va falloir induire plus d'état. maintenant si il tourne un peu a gauche, il va croire que d'avoir fait
    # ça c'est pas ouf parce qu'il aura toujours un mure devant lui.
    # si on inclut tous les sensors on pourra dire du genre "si top and rightest contre mur essaie encore de tourner a gauche pour voir" -> maybe ça le debloquera
    if top < 0.06:  # in cm
        return 0
    else:
        return 1


for i in range(0, epoch):
    print("Epoch: ", i)
    x = 0.0   # robot position in meters - x direction - positive to the right
    y = 0.0   # robot position in meters - y direction - positive up
    q = math.radians(90.0)  # robot heading with respect to x-axis in radians
    action_index = 0
    state = 1
    for cnt in range(10000):
        robot_position = Position(x, y, q)

        rays = [create_rays(pos, robot_position)
                for pos in sensors_position]
        sensors_values = [
            distance(world.intersection(ray), x, y) for ray in rays]

        top = sensors_values[2]
        # leftest = sensors_values[0]
        # left = sensors_values[1]
        # right = sensors_values[3]
        # rightest = sensors_values[4]

        new_state = get_state(top)

        if new_state == 0:
            reward = -15
        else:
            reward = 100

        Q[state, action_index] = Q[state, action_index] + lr * \
            (reward + gamma *
             np.max(Q[new_state, :]) - Q[state, action_index])

        # Set the percent you want to explore
        action_index = None
        state = new_state

        if uniform(0, 1) < epsilon:
            """
            Explore: select a random action
            """
            action_index = randint(0, 3)
        else:
            """
            Exploit: select the action with max value (future reward)
            """
            action_index = np.argmax(Q[state])

        action = actions[action_index]
        left_wheel_velocity = action[0]
        right_wheel_velocity = action[1]

        # step simulation
        x, y, q = simulationstep(x, y, q)

        # check collision with arena walls
        if (world.distance(Point(x, y)) < 0.005):
            # if (world.distance(Point(x, y)) < L/2):
            print(x, y)
            print("collided")
            print(world.distance(Point(x, y)))
            print("\n\n\n")
            break

        # if cnt % 50 == 0:
        #     file.write(str(x) + ", " + str(y) + ", " + str(q) + "\n")
        if i == epoch - 1:
            if cnt % 20 == 0:
                # print(Q)
                file.write(str(x) + ", " + str(y) + ", " +
                           str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")
    print(Q)

file.close()
