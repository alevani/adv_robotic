#!/usr/bin/env python3
from ev3dev.ev3 import *
from ev3dev2.sound import Sound
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

def get_sensor_values():
    left = 0 if cl_left.value() > 50 else 1
    right = 0 if cl_right.value() > 50 else 1
    top = 0 if cl_top.value() > 50 else 1
    return left, right, top

def do_while(previous, speedr, speedl):
    value = previous
    while value != '010':
        mB.run_timed(time_sp = 200, speed_sp= speedl)
        mA.run_timed(time_sp = 200, speed_sp= speedr)
        
        left, right, top = get_sensor_values()
        value = str(left) + str(top) + str(right)

def forward():
    mB.run_timed(time_sp = 200, speed_sp= 300, stop_action= "brake")
    mA.run_timed(time_sp = 200, speed_sp= 300,stop_action= "brake")

def mario():
    sound = Sound()
    
    sound.play_tone(1500, 0.1)
    sound.play_tone(1500, 0.1)
    sleep(0.2)
    sound.play_tone(1500, 0.1)
    sleep(0.1)
    sound.play_tone(1000, 0.1)
    sound.play_tone(1500, 0.1)
    sleep(0.2)
    sound.play_tone(2000, 0.1)
    sleep(0.3)
    sound.play_tone(500, 0.1)

    
#mario()

# Wonder around
while True:
    f = False
    speedl = 300
    speedr = 300
    
    left, right, top = get_sensor_values()
    value = str(left) + str(top) + str(right)

    if value == '000':
        f = True
        forward()
    
    elif value == '001':
        speedr = 0
    
    elif value == '010':
        f = True
        forward()
    
    elif value == '011':
        speedr = 0
    
    elif value == '100':
        speedl = 0
    
    elif value == '101':
        #! could also be right
        speedr = 0
    
    elif value == '110':
        speedl = 0
    
    elif value == '111':
        #! could also be right and top
        speedl = 0
    
    # Used to that it turns all the way before continuing any action
    while value != '010' and f == False:
        mB.run_timed(time_sp = 200, speed_sp= speedl,stop_action= "brake")
        mA.run_timed(time_sp = 200, speed_sp= speedr,stop_action= "brake")
        
        left, right, top = get_sensor_values()
        value = str(left) + str(top) + str(right)