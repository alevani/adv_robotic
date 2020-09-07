#!/usr/bin/env python3
from ev3dev.ev3 import *
from ev3dev2.sound import Sound
import math
import random
from time import sleep

mB = LargeMotor('outB')
mA = LargeMotor('outA')
cl_top = ColorSensor('in2')
cl_left = ColorSensor('in3')
cl_right = ColorSensor('in4')
cl_top.mode='COL-REFLECT'


#! Maybe here we will need to implement:
        #! if the robot does not go straight, we have to get it back to a straight
        #! That is, do the basic line following robot -> yes, this is causing trouble. (a lot)
        #? this might be solved by 44 to 50.
        #? now logical chicane don't need to be given in the sequence as
        #? the robot will have no other choice anyway.

sequence = [0,1,0,3,2,2,2,0]

def run(speedl = 300,speedr = 300, f = False):
    time_sp = 200
    
    if f:
        # Elongate the time if moving forward so that the sensors
        # are not trigger too fast
        time_sp += 500

    mB.run_timed(time_sp = time_sp, speed_sp= speedl)
    mA.run_timed(time_sp = time_sp, speed_sp= speedr)

def get_sensor_values(use_top = True):
    left = 0 if cl_left.value() > 50 else 1
    right = 0 if cl_right.value() > 50 else 1
    top = 0 if cl_top.value() > 50 else 1
    
    if use_top:
        return str(left) + str(top) + str(right)
    else:
        return str(left) + str(right)

def wait_for_intersect(value = '00'):
    # We don't take the top sensor in consideration
    # as we only need to wait for the sensor to be trigerred.
    while value != '11':
        speedl = 300
        speedr = 300
        
        if value == '01': # slightly turn to the right
            speedr = 0
        elif value == '10': # slightly turn to the left
            speedl = 0
        
        run(speedl,speedr)
        value = get_sensor_values(False)
        
def perform_action(speedl,speedr,value,f):
    # Maybe note that if it does not detect 010 instantly after going here it's because
    # there's a not controlled delayed due to physics law
    while value != '010':
        run(speedl, speedr,f)
        value = get_sensor_values()

#while goal no reach ? 
for to in sequence:
    forward = False
    speedl = 300
    speedr = 300
    
    value = get_sensor_values()

    if to == 0: # Forward
        forward = True
        pass
    elif to == 1: # Right turn
        speedr = 0
    elif to == 2: # Left turn
        speedl = 0
    elif to == 3: # Turn around (180)
        #! TODO: Will it be enough to perform ..?
        # Run backward a little so it does not move the can when rotating
        # mB.run_timed(time_sp = 200, speed_sp= -300)
        # mA.run_timed(time_sp = 200, speed_sp= -300)
        # mB.wait_while('running')
        # mA.wait_while('running')
        speedl = 300
        speedr = -300
    
        perform_action(speedl,speedr,value, forward)
    wait_for_intersect()