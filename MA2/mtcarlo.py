
from Lidar import Lidar
from dataclasses import dataclass
from math import radians, cos, sin, sqrt
from random import randint, uniform
from shapely.geometry import LinearRing, LineString
from time import sleep, time
import matplotlib.pyplot as plt
import numpy as np
import sys


WORLD = None  # gonna be defined after World
NB_SAMPLES = 15
NB_BEST_CANDIDATES = 10
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
        if x > self.right_border or x < self.left_border \
                or y > self.top_border or y < self.bottom_border:
            print("XXXXXXXXXXXX\n" * 30)
            print(" VALUES OUT OF WORLD'S BORDERS", x, y, alpha)
            print("XXXXXXXXXXXX\n" * 30)
            return None
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

    # def move(self, dx, dy, da):
    #     self.x += dx
    #     self.y += dy
    #     self.angle += da

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
    # TODO: refactored with numpy function, verify if still accurate
    return np.sum(np.abs(np.subtract(real_values, simulated_values)))


def create_random_sample(size=NB_SAMPLES, world=WORLD) -> list:
    candidates = []

    for _ in range(size):
        c = Robot(angle=randint(0, 360),
                  x=uniform(world.left_border, world.right_border),
                  y=uniform(world.bottom_border, world.top_border))
        candidates.append(c)

    #! to delete
    n = []
    for c in candidates:
        if c.x > 0 and c.y > 0:
            n.append(c)
    # return candidates
    print(n)
    return n


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
    # only_robots = [c[0] for c in candidates]
    return candidates[: nb_best_candidates]


def keep_inside_world(world, x, y, a):
    # Keeps the resampling inside the arena
    if x > world.right_border:
        x = world.right_border - 0.01
    elif x < world.left_border:
        x = world.left_border + 0.01

    if y > world.top_border:
        y = world.top_border - 0.01
    elif y < world.bottom_border:
        y = world.bottom_border + 0.01

    return Robot(angle=a, x=x, y=y)


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

        new_candidates.append(keep_inside_world(world, x, y, a))

    return new_candidates


class ParticleFiltering:
    def __init__(self, real_lidar: Lidar, n=None):
        self.position = None
        self.real_lidar = real_lidar
        self.dx = 0
        self.dy = 0
        self.nb_conv = 0
        self.da = 0
        self.aseba = n

    def set_delta(self, dx, dy, da):
        self.has_converged = False
        self.dx = dx
        self.dy = dy
        self.da = da

    def move_sample(self, sample):
        new_sample = []
        for r in sample:

            angle = r.angle + self.da
            x = r.x + self.dx
            y = r.y + self.dy
            nr = keep_inside_world(WORLD, x, y, angle)
            new_sample.append(nr)
        self.dx = 0
        self.dy = 0
        self.da = 0
        return new_sample

    def localise(self):
        sample = create_random_sample()
        try:
            while True:
                sample = self.move_sample(sample)
                real_robot_lidar = self.real_lidar.get_scan_data()
                # print(real_robot_lidar)

                best_candidates_w_fitness = get_best_candidates(
                    sample, real_robot_lidar)
                best_candidates = [x[0] for x in best_candidates_w_fitness]
                new_candidates = []

                for virtual_robot in best_candidates:
                    cs = resample_around(virtual_robot)
                    new_candidates.extend(cs)

                sample = new_candidates
                self.position = best_candidates[0]
                fitness = best_candidates_w_fitness[0][1]
                self.has_converged = True
                print("-------------------------- Converged with fitness: ", fitness)

        except KeyboardInterrupt:
            sys.exit()


if __name__ == '__main__':
    from Lidar import FakeLidar
    import threading
    fake_lidar = FakeLidar(Robot(x=0.80, y=0.30, angle=90))
    print(fake_lidar.get_scan_data())
    pf = ParticleFiltering(fake_lidar)
    # pf.localise()
    # scanner_thread = threading.Thread(target=pf.localise)
    scanner_thread = threading.Thread(target=pf.localise)
    scanner_thread.start()
    while True:
        cmd = input('command')
        if cmd == 'print':
            print()
