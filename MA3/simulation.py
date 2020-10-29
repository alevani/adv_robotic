import shapely
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
import numpy as np
from random import *
from utils import Position
from utils import distance

epsilon = 0.5  # up to 1
gamma = 0.8  # up to 0.99
lr = 1  # up to 1

actions = [(0.4, 0.4), (-0.4, 0.4), (-0.4, 0.4), (0.4, -0.4)]
Q = zeros((2, 4))


# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 1.18  # width of arena
H = 1.94  # height of arena

robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
# timestep in kinematics< sim (probably don't touch..)
simulation_timestep = 0.01

# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

left_wheel_velocity = random()   # robot left wheel velocity in radians/s
right_wheel_velocity = random()  # robot right wheel velocity in radians/s

# Kinematic model
#################
# updates robot position and heading based on velocity of wheels and the elapsed time
# the equations are a forward kinematic model of a two-wheeled robot - don't worry just use it

#! induire que les murs sont bien reeles


def simulationstep():
    global x, y, q

    # step model time/timestep times
    for step in range(int(robot_timestep/simulation_timestep)):
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)

        x += v_x * simulation_timestep
        y += v_y * simulation_timestep
        q += omega * simulation_timestep


# Simulation loop
#################
file = open("trajectory.dat", "w")


def create_rays(pos, robot_position):
    x = pos.x + robot_position.x
    y = pos.y + robot_position.y
    a = pos.a + robot_position.a
    return LineString([(x, y), (x+cos(q)*2*W, (y+sin(q)*2*H))])


# Order is : Top, left most, second to left, second to right, right most
sensors_position = [Position(-0.05, 0.06, 40), Position(-0.025,
                                                        0.075, 18.5), Position(0, 0.0778, 0), Position(0.05, 0.06, -40), Position(0.025, 0.025, -18.5)]


def get_state(top):
    if top < 0.3:
        return 0
    else:
        return 1


action_index = 0
state = 1
for i in range(0, 10):
    print("Epoch: ", i)
    #! place it in the middle so half width half height
    #! Might already be the middle?
    x = 0.0   # robot position in meters - x direction - positive to the right
    y = 0.0   # robot position in meters - y direction - positive up
    q = 0.0   # robot heading with respect to x-axis in radians
    for cnt in range(5000):
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
            reward = -10
        else:
            reward = 20

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
            action = actions[action_index]
            left_wheel_velocity = action[0]
            right_wheel_velocity = action[1]
        else:
            """
            Exploit: select the action with max value (future reward)
            """

            action_index = np.argmax(Q[state])
            action = actions[action_index]

            left_wheel_velocity = action[0]
            right_wheel_velocity = action[1]

        # step simulation
        simulationstep()

        # check collision with arena walls
        if (world.distance(Point(x + 0.0778, y)) < L/2):
            print("collided")
            break

        # if cnt % 50 == 0:
        #     file.write(str(x) + ", " + str(y) + ", " + str(q) + "\n")
        if cnt % 50 == 0:
            # print(Q)
            file.write(str(x) + ", " + str(y) + ", " +
                       str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")
    print(Q)


file.close()
