from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean, array
# from adafruit_rplidar import RPLidar
import threading
from threading import Thread
import matplotlib.pyplot as plt
from math import floor
from random import *
import shapely
import sys
from time import sleep


class ParticleFiltering:
    def __init__(self):
        self.H = 1.18  # width of arena
        self.W = 1.94  # height of arena

        # the world is a rectangular arena with width W and height H
        self.world = LinearRing(
            [(self.W/2, self.H/2), (-self.W/2, self.H/2), (-self.W/2, -self.H/2), (self.W/2, -self.H/2)])

        self.nb_samples = 200
        self.nb_candidates = 20
        self.scan_data = [0]*360

        # Create nb_samples samples
        self.samples = [[uniform(-.96, .96), uniform(-0.58, .58), randint(0, 360)]
                        for _ in range(0, self.nb_samples)]

        self.best_candidates = self.get_best_candidates(self.samples)
        # [(plt.scatter(be[1][0], be[1][1], c='b')) for be in best_candidates]

        self.x = 0.0
        self.y = 0.0
        self.angle = 0
        self.position = (0, 0, 0)

    #     # Setup the RPLidar
    #     PORT_NAME = '/dev/ttyUSB0'
    #     self.lidar = RPLidar(None, PORT_NAME)

    #     print('start lidar scan thread')
    #     self.scanner_thread = threading.Thread(target=self.lidarScan)
    #     self.scanner_thread.daemon = True
    #     self.scanner_thread.start()

    # def lidarScan(self):
    #     print("Starting background lidar scanning")
    #     for scan in self.lidar.iter_scans():
    #         for (_, angle, distance) in scan:
    #             self.scan_data[min([359, floor(angle)])] = distance

    def set_xya(self, x, y, a):
        self.x = x
        self.y = y
        self.angle = a

    # return the average position of the robot on the map
    def avg_xya(self, os):
        return (mean([x[1][0] for x in os]), mean([x[1][1]
                                                   for x in os]), mean([x[1][2] for x in os]))

    # Fitness function
    def calculate_distance(self, a, b):
        return sum(abs(subtract(a, b)))
        # return sum(abs(array([a**2 if a < 0.02 and a > -0.02 else a for a in subtract(a, b)])))

    # Return world intersection with a ray
    def return_inter(self, alpha, x, y):
        ray = LineString(
            [(x, y), (x+cos(alpha)*2*self.W, (y+sin(alpha)*2*self.H))])
        s = self.world.intersection(ray)
        return sqrt((s.x-x)**2+(s.y-y)**2)

    # Get the lidar values for simulated samples
    def get_simulated_lidar_values(self, x):
        # shift of alpha so that both the robot and the simulation look in the same direction
        # ? - or + shift
        return [self.return_inter((x[2] + (alpha * 36)) % 360, x[0], x[1]) for alpha in range(0, 10)]

    # Return the values thymio lidar sensor
    def get_lidar_values(self):
        return self.get_simulated_lidar_values((.25, .25, 90))
        # return [self.scan_data[x] / 1000 for x in list(range(0, 360, 36))]

    # Return the nb_candidates best candidates
    def get_best_candidates(self, samples):
            # Contains a list of nb_samples lidar simlutation (each with 10 rays)
        lr_samples = [(self.get_simulated_lidar_values(x), x) for x in samples]

        DISTrr = self.get_lidar_values()

        candidates = [((self.calculate_distance(DISTrr, sample[0]), sample[1]))
                      for sample in lr_samples]

        # # sort by second index
        candidates.sort(key=lambda candidates: candidates[0])

        return candidates[: self.nb_candidates]

    def Localize(self):
        while True:

            # Move and Resample
            re_candidates = []
            for b in self.best_candidates:
                b[1][0] += self.x
                b[1][1] += self.y
                b[1][2] += self.angle
                # ? reset to zero as it should only be done once?
                self.set_xya(0, 0, 0)
                # Creates nb_candidates new subsample for each best candidate
                for _ in range(0, self.nb_candidates):
                    # Resample around a 1 centimer wide box.
                    x = b[1][0] + uniform(-0.03, 0.03)
                    y = b[1][1] + uniform(-0.03, 0.03)
                    a = (b[1][2] + randint(-10, 10)) % 360

                    # Keeps the resampling in the arena
                    if x > .96:
                        x = .96
                    elif x < -.96:
                        x = -.96

                    if y > .58:
                        y = .58
                    elif y < -.58:
                        y = -.58

                    re_candidates.append([x, y, a])

            self.best_candidates = self.get_best_candidates(re_candidates)
            # self.position = self.avg_xya(self.best_candidates)
            self.position = self.best_candidates[1]


if __name__ == '__main__':
    pf = ParticleFiltering()

    print('start particle filtering thread')
    thread = Thread(target=pf.Localize)
    thread.daemon = True
    thread.start()
    pf.set_xya(.25, .25, 90)
    try:
        while True:
            sleep(0.1)
            print(pf.position)

    except KeyboardInterrupt:
        sys.exit()

    # TODO use the color sensor afterward
