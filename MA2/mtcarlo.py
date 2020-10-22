from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean, array
from dataclasses import dataclass
import matplotlib.pyplot as plt
from math import floor, radians
from picamera import PiCamera
from Lidar import Lidar
from time import sleep
from random import *
import numpy as np
import shapely
import sys
import cv2

WORLD = None  # gonna be defined after World
NB_SAMPLES = 10
NB_BEST_CANDIDATES = 5
NB_LIDAR_RAY = 12


class World:
    def __init__(self):
        self.H = 1.18  # width of arena in meters
        self.W = 1.94  # height of arena in meters
        self.top_border = self.H/2  # 0.59
        self.bottom_border = -self.H/2
        self.right_border = self.W/2  # 0.97
        self.left_border = -self.W/2
        self.rectangle = LinearRing([(self.W/2,  self.H/2),
                                     (-self.W/2,  self.H/2),
                                     (-self.W/2, -self.H/2),
                                     (self.W/2, -self.H/2)])

    def return_inter(self, alpha, x, y):
        ''' Return world intersection with a ray'''
        # print("coor", alpha, x, y)
        a = radians(alpha)
        dest_x = x + cos(a) * 2*self.W
        dest_y = y + sin(a) * 2*self.H
        # print(x, y, dest_x, dest_y)
        line = [(x, y), (dest_x, dest_y)]
        try:
            ray = LineString(line)
        except:
            print("-----------")
            print(x)
            print("--")
            print(y)
            print("--")
            print(dest_x)
            print("--")
            print(dest_y)

        # print("ray", ray)

        # print("ray", ray)
        s = self.rectangle.intersection(ray)
        # print("s", s)
        return sqrt((s.x-x)**2+(s.y-y)**2)


WORLD = World()


@dataclass
class Robot:
    angle: float
    x: float
    y: float

    def get_simulated_lidar_values(self, world=WORLD, nb_ray=NB_LIDAR_RAY):
        ''' Get the lidar values for simulated samples'''
        rays = []
        for alpha in range(0, 360, 360//nb_ray):
            lid_angle = (self.angle + alpha) % 360
            ray = world.return_inter(lid_angle, self.x, self.y)
            rays.append(ray)
        return rays

    def move(self, dx, dy, da):
        self.x += dx
        self.y += dy
        self.angle += da

    def which_corner(self) -> str:
        ''' in which corner of the map is located the robot'''
        corner = ''
        if self.y > 0:
            corner += 'top_'
        else:
            corner += 'bottom_'
        if self.x > 0:
            corner += 'right'
        else:
            corner += 'left'
        return corner

    def is_in_corner(self, corner: str) -> bool:
        '''is the robot in the given corner of the map'''
        return corner == self.which_corner()

    def __repr__(self):
        return ("({}, {}, {})".format(
            round(self.x, 3),
            round(self.y, 3),
            self.angle))


def lidar_fitness(real_values: list, simulated_values: list) -> float:
    '''Fitness showing how close are the simulated lidar values
    to the real lidar values. Lower is better ( closer )
    '''
    return sum(abs(subtract(real_values, simulated_values)))


def create_random_sample(size=NB_SAMPLES, world=WORLD) -> list:
    candidates = []
    for _ in range(size):
        c = Robot(angle=randint(0, 360),
                  x=uniform(world.left_border, world.right_border),
                  y=uniform(world.bottom_border, world.top_border))
        candidates.append(c)
    return candidates


def get_best_candidates(samples,
                        real_robot_lidar,
                        nb_best_candidates=NB_BEST_CANDIDATES):
    '''
    Return the best candidates from a list of virtual robots positions
    compared to the real robot lidar values.
    '''
    candidates = []
    for virtual_robot in samples:
        vrl = virtual_robot.get_simulated_lidar_values()
        fit = lidar_fitness(real_robot_lidar, vrl)
        candidates.append((virtual_robot, fit))

    candidates.sort(key=lambda candidates: candidates[1])
    only_robots = [c[0] for c in candidates]
    return only_robots[: nb_best_candidates]


def resample_around(robot, size=NB_BEST_CANDIDATES, world=WORLD):
    '''
    create `size` new virtual robots located around the given robot
    '''
    pos_delta = 0.03
    angle_delta = 10
    new_candidates = []
    for _ in range(size):
        x = robot.x + uniform(-pos_delta, pos_delta)
        y = robot.y + uniform(-pos_delta, pos_delta)
        a = (robot.angle + randint(-angle_delta, angle_delta)) % 360

        # Keeps the resampling inside the arena
        if x > world.right_border:
            x = world.right_border - 0.01
        elif x < world.left_border:
            x = world.left_border + 0.01

        if y > world.top_border:
            y = world.top_border - 0.01
        elif y < world.bottom_border:
            y = world.bottom_border + 0.01

        new_candidates.append(Robot(angle=a, x=x, y=y))
    return new_candidates


class ParticleFiltering:
    def __init__(self, real_lidar: Lidar, n):
        self.position = None
        self.real_lidar = real_lidar
        # self.calibrate()
        self.dx = 0
        self.dy = 0
        self.da = 0
        self.aseba = n

    def set_delta(self, dx, dy, da):
        print("Delta x", dx)
        print("Delta y", dy)
        print("Delta angle", da)
        self.dx = dx
        self.dy = dy
        self.da = da

    def move_sample(self, sample):
        new_sample = []
        for r in sample:
            nr = Robot(angle=r.angle + self.da,
                       x=r.x + self.dx,
                       y=r.y + self.dy)
            new_sample.append(nr)
        self.dx = 0
        self.dy = 0
        self.da = 0
        return new_sample

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def calibrate(self):
        #! Do aseba init somewhere, but it's already being done in robot_dance so maybe to times might crash the whole thing.
        colorOrder = []
        self.stop()

        camera = PiCamera()
        camera.start_preview()
        camera.resolution = (320, 240)
        for _ in range(8):

            image = np.empty((240, 320, 3), dtype=np.uint8)
            camera.capture(image, 'bgr')

            for color, mask_fn in cv2.MASKS.items():
                bicol = cv2.apply_mask(image, mask_fn)
                isDetected = cv2.circle_detector(bicol)[1]
                if isDetected and color not in colorOrder:
                    colorOrder.append(color)

            left_wheel = 200
            right_wheel = -200

            self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])
            sleep(1.0)  # adjust depending on how long it will take to make 1/8 turn
            self.stop()
        camera.stop_preview()
        return colorOrder

    def localise(self):
        sample = create_random_sample()
        try:
            while True:

                sample = self.move_sample(sample)
                real_robot_lidar = self.real_lidar.get_scan_data()
                print(real_robot_lidar)

                best_candidates = get_best_candidates(sample, real_robot_lidar)
                new_candidates = []

                for virtual_robot in best_candidates:
                    cs = resample_around(virtual_robot)
                    new_candidates.extend(cs)

                sample = new_candidates
                self.position = best_candidates[0]

        except KeyboardInterrupt:
            sys.exit()


if __name__ == '__main__':
    from Lidar import FakeLidar
    fake_lidar = FakeLidar(Robot(x=0.30, y=0.50, angle=35))
    pf = ParticleFiltering(fake_lidar)
    pf.localise()


# not used but usefull

def old_main():
    WORLD = World()
    convergence_iteration = 10
    real_robot = Robot(x=.8, y=-0.23, angle=57)
    # real_robot = Robot(angle=0, x=0, y=0)
    sample = create_random_sample()

    try:
        while True:
            raw = input('continue')
            if len(raw) > 0:
                xy = [float(x) for x in raw.split(',')]
                print(xy)
                real_robot.x += xy[0]
                real_robot.y += xy[1]
            for _ in range(convergence_iteration):
                # change for real lidar value
                real_robot_lidar = real_robot.get_simulated_lidar_values()
                best_candidates = get_best_candidates(sample, real_robot_lidar)
                print("best", best_candidates[0])
                new_candidates = []
                for virtual_robot in best_candidates:
                    cs = resample_around(virtual_robot)
                    new_candidates.extend(cs)
                sample = new_candidates

                # sleep(0.1)
    except KeyboardInterrupt:
        sys.exit()
