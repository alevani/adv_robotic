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
cl_top.mode = 'COL-REFLECT'
cl_right.mode = 'COL-REFLECT'
cl_left.mode = 'COL-REFLECT'

sequence = [1, 0, 3, 2, 2, 2, 0, 3, 2, 2, 2, 0, 3, 2, 2, 2, 0, 3]
sequence = [1 ,1 ,1 , 4, 1, 2, 0, 3, 2, 0, 3, 1] #solution prof
sequence = [4]


FULL_SPEED = 300

def calculate_cm_rpm(x):
    # 175 being the tire circonference in mm
    # 360 because the function needs degrees
    return x * 10 / 175 * 360


def rotate_degree_rpm(a, direction=1):

    # 125 Being the distance between the two half of the wheels
    mB.run_to_rel_pos(position_sp=direction *
                      calculate_cm_rpm(125 * math.pi / 10) * (a / 360), speed_sp=450)
    mA.run_to_rel_pos(position_sp=-1 * direction *
                      calculate_cm_rpm(125 * math.pi / 10) * (a / 360), speed_sp=450)
    sleep(1)


def run(speedl=FULL_SPEED, speedr=FULL_SPEED, f=False):
    time_sp = 200

    if f:
        # Elongate the time if moving forward so that the sensors
        # are not trigger too fast
        time_sp += 500

    mB.run_timed(time_sp=time_sp, speed_sp=speedl)
    mA.run_timed(time_sp=time_sp, speed_sp=speedr)


def get_sensor_values(use_top=True):
    left = 0 if cl_left.value() > 50 else 1
    right = 0 if cl_right.value() > 50 else 1
    top = 0 if cl_top.value() > 50 else 1
    #top = 0 if cl_top.value() >= 1 else 1
    
    if use_top:
        return str(left) + str(top) + str(right)
    else:
        return str(left) + str(right)


def wait_for_intersect(value='00'):
    # We don't take the top sensor in consideration
    # as we only need to wait for the sensor to be trigerred.
    while value != '11':
        speedl = FULL_SPEED
        speedr = FULL_SPEED

        if value == '01':  # slightly turn to the right
            speedr = 0
        elif value == '10':  # slightly turn to the left
            speedl = 0

        run(speedl, speedr)
        value = get_sensor_values(False)


def perform_action(speedl, speedr, value, f):
    # Maybe note that if it does not detect 010 instantly after going here it's because
    # there's a not controlled delayed due to physics law
    while value != '010':
        run(speedl, speedr, f)
        value = get_sensor_values()


# while goal no reach ?
for to in sequence:
    wait_for_intersect()

    forward = False
    speedl = FULL_SPEED
    speedr = FULL_SPEED
    value = get_sensor_values()

    if to == 0:  # Forward
        forward = True
    elif to == 1:  #  Right turn
        speedr = 0
    elif to == 2:  # Left turn
        speedl = 0
    elif to == 3:  # Turn around (180)
        # Run backward a little so it does not move the cane when rotating
        mB.run_timed(time_sp=600, speed_sp=-FULL_SPEED)
        mA.run_timed(time_sp=600, speed_sp=-FULL_SPEED)
        sleep(0.7)
        rotate_degree_rpm(20)
        speedr = -FULL_SPEED
    elif to == 4: #short turn left
        # Run backward a little so it does not move the cane when rotating
        
        while value != '010':
            run(speedl, 0, forward)
            value = get_sensor_values()
        
        mB.run_timed(time_sp=1600, speed_sp=FULL_SPEED)
        mA.run_timed(time_sp=1600, speed_sp=FULL_SPEED)
        sleep(1.7)
        mB.run_timed(time_sp=500, speed_sp=-FULL_SPEED)
        mA.run_timed(time_sp=500, speed_sp=-FULL_SPEED)
        sleep(0.6)
        rotate_degree_rpm(40)
        speedl = -FULL_SPEED
    elif to == 4: #short turn right
        pass
    elif to == 5: #long turn left
        pass
    elif to == 6: #long turn right
        pass
    
    perform_action(speedl, speedr, value, forward)
    print(get_sensor_values)



#! Maybe here we will need to implement:
#! if the robot does not go straight, we have to get it back to a straight
#! That is, do the basic line following robot -> yes, this is causing trouble. (a lot)
# ? this might be solved by 44 to 50.
# ? now logical chicane don't need to be given in the sequence as
# ? the robot will have no other choice anyway.
# TODO problem with the robot not pushing the cane in the center of the axis
#! try: but the top sensor aligned to the two others
#! it could work now that we don't use it to detect intesect anymore
# ? solved by putting the sensor higher, it actually works well but very scary.
#! no we can't actually go straight on edges because the sensors fuck.
#! we might need to add the top sensor again but I don't remeber why I
#! Deleted it in the first place...
# ? well I know why: because if we wanted to detect T, then robot would give 011. but that's
# ? the same as if the robot is just not going so straight on a straight a needs to be re aligned.
# todo solution: au lieu de le faire aller tout droit et qu'il parte en couille, on dit au plannar
# todo d'aller a droite ;;) comme théo a expliqué
#! on a eu un problème: on vient de s'apervecvoir qu'on avait des problème avec les coins
#! aussi expliquer qu'on a du se separer des doublons dans le planner et des corner
#! et changer les edges