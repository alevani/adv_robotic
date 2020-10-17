from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean, array
# from adafruit_rplidar import RPLidar
import threading
from threading import Thread
import matplotlib.pyplot as plt
from math import floor, radians
from random import *
import shapely
import sys
from time import sleep
from dataclasses import dataclass

@dataclass
class World:
    def __init__(self):
        self.H = 1.18  # width of arena in meters
        self.W = 1.94  # height of arena in meters
        self.top_border    =  self.H/2 # 0.59
        self.bottom_border = -self.H/2 
        self.right_border  =  self.W/2 # 0.97
        self.left_border   = -self.W/2
        self.map = LinearRing([( self.W/2,  self.H/2),
                               (-self.W/2,  self.H/2),
                               (-self.W/2, -self.H/2),
                               ( self.W/2, -self.H/2)])

    def return_inter(self, alpha, x, y):
        ''' Return world intersection with a ray'''
        # print("coor", alpha, x, y)
        a = radians(alpha)
        dest_x =  x + cos(a) * 2*self.W
        dest_y =  y + sin(a) * 2*self.H
        line = [(x, y), (dest_x, dest_y)]
        ray = LineString(line)
        # print("ray", ray)
        s = self.map.intersection(ray)
        # print("s", s)
        return sqrt((s.x-x)**2+(s.y-y)**2)

  
ARENA = World()
NB_SAMPLES = 200
NB_BEST_CANDIDATES = 20
NB_LIDAR_RAY = 4


@dataclass
class Robot:
    angle   :float
    x       :float
    y       :float

    def get_simulated_lidar_values(self, world=ARENA, nb_ray=NB_LIDAR_RAY):
        ''' Get the lidar values for simulated samples'''
        rays = []
        for alpha in range(0, 360, 360//nb_ray):
            lid_angle = (self.angle + alpha) % 360
            ray = world.return_inter(lid_angle, self.x, self.y)
            rays.append(ray)
        return rays

    def __repr__(self):
        return ("({}, {}, {})".format(
                                round(self.x, 2),
                                round(self.y, 2),
                                self.angle))


def lidar_fitness(real_values: list, simulated_values: list) -> float:
    return sum(abs(subtract(real_values, simulated_values)))
    # return sum(abs(array([a**2 if a < 0.02 and a > -0.02 else a for a in subtract(a, b)])))

def create_random_sample(size=NB_SAMPLES, world=ARENA) -> list:
    candidates = []
    for _ in range(size):
        c = Robot(angle=randint(0, 360),
                  x=uniform(world.left_border, world.right_border),
                  y=uniform(world.bottom_border, world.top_border))
        candidates.append(c)
    return candidates


def get_best_candidates(samples,
                        real_lidar_values,
                        nb_best_candidates=NB_BEST_CANDIDATES):
    '''
    Return the nb_best_candidates best candidates
    '''
    candidates = []
    for robot in samples:
        fit = lidar_fitness(real_lidar_values,
                            robot.get_simulated_lidar_values())
        candidates.append((robot, fit))

    candidates.sort(key=lambda candidates: candidates[1])
    only_robots = [c[0] for c in candidates]
    return only_robots[: nb_best_candidates]


def resample_around(robot, sample_size=NB_BEST_CANDIDATES, world=ARENA):
    '''
    create nb_best_candidates new candidates around the given robot
    '''
    pos_delta      = 0.03
    angle_delta    = 10
    new_candidates = []
    for _ in range(sample_size):
        x = robot.x + uniform(-pos_delta, pos_delta)
        y = robot.y + uniform(-pos_delta, pos_delta)
        a = (robot.angle + randint(-angle_delta, angle_delta)) % 360

        # Keeps the resampling in the arena
        if x > world.right_border:
            x = world.right_border -0.01
        elif x < world.left_border:
            x = world.left_border + 0.01

        if y > world.top_border:
            y = world.top_border - 0.01
        elif y < world.bottom_border:
            y = world.bottom_border + 0.01

        new_candidates.append(Robot(angle=a, x=x, y=y))
    return new_candidates



def localize(delta_x, delta_y, delta_angle, best_candidates):
    while True:
        # Move and Resample
        re_candidates = []
        for robot in best_candidates:
            robot.x     += delta_x
            robot.y     += delta_y
            robot.angle += delta_angle
            # ? reset to zero as it should only be done once?
            # self.set_xya(0, 0, 0)
            # Creates nb_best_candidates new subsample for each best candidate
            re_candidates = resample_around(robot)
        new_best_candidates = get_best_candidates(re_candidates)
        self.position = self.new_best_candidates[0]


if __name__ == '__main__':
    ARENA = World()

    real_robot = Robot(x=0.60, y=-0.30, angle=320)
    # real_robot = Robot(angle=0, x=0, y=0)
    sample = create_random_sample()
    try:
        while True:
            print("sample",  len(sample))
            # input('continue')
            rr_lidar = real_robot.get_simulated_lidar_values()
            best_candidates = get_best_candidates(sample, rr_lidar)
            print("best_candidates", best_candidates[0])
            # input('continue')
            new_candidates = []
            for virtual_robot in best_candidates:
                c = resample_around(virtual_robot)
                new_candidates.extend(c)
            sample = new_candidates
         
            # sleep(0.1)

    except KeyboardInterrupt:
        sys.exit()

