import shapely
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt
from random import random

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

# Variables
###########
x_blue = 0
y_blue = 0
#! Changer pour avoir un carré
blue_pole = Polygon([(x_blue, y_blue), (x_blue, y_blue + 0.01),
                     (x_blue + 0.01, y_blue + 0.01), (x_blue + 0.01, y_blue)])
x_red = 0
y_red = 0
red_pole = Polygon([(x_red, y_red), (x_red, y_red + 0.01),
                    (x_red + 0.01, y_red + 0.01), (x_red + 0.01, y_red)])


#! place it in the middle so half width half height
x = 0.0   # robot position in meters - x direction - positive to the right
y = 0.0   # robot position in meters - y direction - positive up
q = 0.0   # robot heading with respect to x-axis in radians

left_wheel_velocity = random()   # robot left wheel velocity in radians/s
right_wheel_velocity = random()  # robot right wheel velocity in radians/s

# Kinematic model
#################
# updates robot position and heading based on velocity of wheels and the elapsed time
# the equations are a forward kinematic model of a two-wheeled robot - don't worry just use it


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

for cnt in range(5000):
    # simple single-ray sensor
    # a line from robot to a point outside arena in direction of q
    ray = LineString([(x, y + 0.0778), (x+cos(q)*2*W, (y+sin(q)*2*H))])
    # ray1 = LineString(
    #     [(x - 0.05, y + 0.06), (x+cos(q + 40)*2*W, (y+sin(q + 40)*2*H))])
    # ray2 = LineString(
    #     [(x - 0.025, y + 0.075), (x+cos(q + 18.5)*2*W, (y+sin(q + 18.5)*2*H))])
    # ray3 = LineString(
    #     [(x + 0.05, y + 0.06), (x+cos(q)*2*W, (y+sin(q - 40)*2*H))])
    # ray4 = LineString(
    #     [(x + 0.025, y + 0.025), (x+cos(q)*2*W, (y+sin(q - 18.5)*2*H))])
    # ray5 = LineString([(x - 3, y - 3), (x+cos(q)*2*W, (y+sin(q)*2*H))])
    # ray6 = LineString([(x + 3, y - 3), (x+cos(q)*2*W, (y+sin(q)*2*H))])

    #! Need to be a plan, and check if plan intesect with blue or/and red
    camera = Polygon([(.., ..), (x, y + 0.0778), (.., ..)])

    if camera.intesect(blue_pole) and camera.intesect(red_pole):
        pass
    elif camera.intesect(blue_pole):
        pass
    elif camera.intesect(red_pole):
        pass

    s = world.intersection(ray)
    # distance to wall
    distance = sqrt((s.x-x)**2+(s.y-y)**2)

    # simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
    if (distance < 0.5):
        left_wheel_velocity = -0.4
        right_wheel_velocity = 0.4
    else:
        if cnt % 100 == 0:
            left_wheel_velocity = random()
            right_wheel_velocity = random()

    # step simulation
    simulationstep()

    # check collision with arena walls
    if (world.distance(Point(x, y)) < L/2):
        break

    if cnt % 50 == 0:
        file.write(str(x) + ", " + str(y) + ", " +
                   str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")

file.close()
