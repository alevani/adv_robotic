#!/usr/bin/env python3
from ev3dev.ev3 import *
import math
import random
from time import sleep

# Attach large motors to ports B and C
mB = LargeMotor('outB')
mA = LargeMotor('outA')
cl_top = ColorSensor('in2')
cl_left = ColorSensor('in3')
cl_right = ColorSensor('in4')


''' Takes a distance in cm '''
def calculate_cm_rpm(x):
    # 175 being the tire circonference in mm
    # 360 because the function needs degrees
    return x * 10 / 175 * 360


''' Takes a distance in cm '''
def calculate_cm(x):
    return 10000 * x / 275


# 1 = left -1 = right
def rotate_degree_rpm(a, direction = 1):
    
    # 125 Being the distance between the two half of the wheels
    mB.run_to_rel_pos(position_sp= direction * calculate_cm_rpm(125 * math.pi / 10) * (a / 360), speed_sp=450, stop_action="brake")
    mA.run_to_rel_pos(position_sp= -1 * direction * calculate_cm_rpm(125 * math.pi / 10)  * (a / 360), speed_sp=450, stop_action="brake")

    mB.wait_while('running')
    mA.wait_while('running')
    
    sleep(.5)


''' Takes a distance in cm and whether the robot should move forward or not
Speed is not an argument as we didn't inlude it in the calcule as a variable '''
def move(x, forward=True, stop_action="brake"):

    f = 1 if forward else -1

    mB.run_to_rel_pos(position_sp= f * calculate_cm_rpm(x), speed_sp= 450, stop_action=stop_action)
    mA.run_to_rel_pos(position_sp= f * calculate_cm_rpm(x), speed_sp= 450, stop_action=stop_action)

    mB.wait_while('running')
    mA.wait_while('running')

    sleep(.5)



cl_top.mode='COL-REFLECT'

speedl = 300
speedr = 300
while True:

    # intersect (3)
    if cl_left.value() < 50 and cl_right.value() < 50 and cl_top.value() > 50:
        move(1)
        if random.randint(1, 2) % 2 == 0:
            rotate_degree_rpm(90)
        else: 
            rotate_degree_rpm(90, -1)
        sleep(0.5 )
    
    # big intersect (4)
    if cl_left.value() < 50 and cl_right.value() < 50 and cl_top.value() < 50:
        move(1)
        value = random.randint(1, 3)
        if value == 1:
            while cl_top.value() < 50:
                rotate_degree_rpm(10)
        elif value == 2: 
            while cl_top.value() < 50:
                rotate_degree_rpm(10, -1)
        else:
            move(3)
        sleep(0.5)

    if cl_left.value() < 50:
        speedl = 200
    else:
        speedl = 300
    
    if cl_right.value() < 50:
        speedr = 200
    else:
        speedr = 300
    
    mB.run_timed(time_sp = 200, speed_sp= speedr)
    mA.run_timed(time_sp = 200, speed_sp= speedl)
    mB.wait_while('running')
    mA.wait_while('running')
    sleep(0.2)
    mA.stop()
    mB.stop()



# rotate_degree_rpm(85)
# move(83.5, forward= False)
# rotate_degree_rpm(80, -1)
# move(7.5, forward= False)

#(0 to 30 0 black tape, 70 to 100 = reflective surface)