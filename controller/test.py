#!/usr/bin/env python3
from ev3dev.ev3 import *
from ev3dev2.sound import Sound
import math
import random
from time import sleep

cl_top = ColorSensor('in2')
cl_top.mode = 'COL-REFLECT'

while True:
    left = 0 if cl_top.value() >= 1 else 1
    print(cl_top.value())