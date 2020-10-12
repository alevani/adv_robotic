from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean
import matplotlib.pyplot as plt
from math import floor
from random import *
import shapely


class ParticleFiltering:
    def __init__(self):
        self.H = 1.18  # width of arena
        self.W = 1.94  # height of arena

        # the world is a rectangular arena with width W and height H
        self.world = LinearRing(
            [(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

        self.nb_samples = 200
        self.nb_candidates = 10

        # Create nb_samples samples
        self.samples = [[uniform(-.96, .96), uniform(-0.58, .58), randint(0, 360)]
                        for _ in range(0, nb_samples)]

        self.best_candidates = self.get_best_candidates(self.samples)
        # [(plt.scatter(be[1][0], be[1][1], c='b')) for be in best_candidates]

    # return the average position of the robot on the map
    def avg_xya(self, os):
        return (mean([x[1][0] for x in os]), mean([x[1][1]
                                                   for x in os]), mean([x[1][2] for x in os]))

    def get_robot_angle_step(self):
        return 20

    # Fitness function
    def calculate_distance(self, a, b):
        return sum(abs(subtract(a, b)))

    # Return world intersection with a ray
    def return_inter(self, alpha, x, y):
        ray = LineString([(x, y), (x+cos(alpha)*2*W, (y+sin(alpha)*2*H))])
        s = self.world.intersection(ray)
        return sqrt((s.x-x)**2+(s.y-y)**2)

    # Get the lidar values for simulated samples
    def get_simulated_lidar_values(self, x):
        # shift of alpha so that both the robot and the simulation look in the same direction
        # ? - or + shift
        return [return_inter((x[2] + (alpha * 36)) % 360, x[0], x[1]) for alpha in range(0, 10)]

    # Return the values thymio lidar sensor
    def get_lidar_values(self):
        #! Dummy values
        x_start = 0.0
        y_start = 0.0
        a_start = 0.0
        plt.scatter(x_start, y_start, c='g')

        # Set the robot position at 0 to see if it works
        return get_simulated_lidar_values([x_start, y_start, a_start])
        # return [uniform(0.01, 1.94) for x in range(0, 10)]

    # Return the nb_candidates best candidates
    def get_best_candidates(self, samples):
        # Contains a list of nb_samples lidar simlutation (each with 10 rays)
        lr_samples = [(get_simulated_lidar_values(x), x) for x in samples]

        DISTrr = self.get_lidar_values()

        candidates = [((calculate_distance(DISTrr, sample[0]), sample[1]))
                      for sample in lr_samples]

        # # sort by second index
        candidates.sort(key=lambda candidates: candidates[0])

        return candidates[: nb_candidates]

    def get_x_y_alpha(self):
        iter = 0
        while iter != 10:
            iter += 1

            #! wait for step()?
            # Move and Resample
            re_candidates = []
            for b in self.best_candidates:
                # b[1][0] += 0.01  # need to move according to angle ;(
                # b[1][1] += 0.01
                # b[1][2] += get_robot_angle_step()
                b[1][0] += 0.0  # need to move according to angle ;(
                b[1][1] += 0.0
                b[1][2] += 0

                # Creates nb_candidates new subsample for each best candidate
                for _ in range(0, self.nb_candidates):
                    # Resample around a 1 centimer wide box.
                    x = b[1][0] + uniform(-0.01, 0.01)
                    y = b[1][1] + uniform(-0.01, 0.01)

                    # Keeps the resampling in the box
                    if x > .96:
                        x = .96
                    elif x < -.96:
                        x = -.96

                    if y > .58:
                        y = .58
                    elif y < -.58:
                        y = -.58

                    re_candidates.append([x, y, randint(0, 360)])

            self.best_candidates = self.get_best_candidates(re_candidates)
        return self.avg_xya(self.best_candidates)


# iter = 0
# while iter != 10:
#     iter += 1

#     # Move and Resample
#     re_candidates = []
#     for b in best_candidates:
#         # b[1][0] += 0.01  # need to move according to angle ;(
#         # b[1][1] += 0.01
#         # b[1][2] += get_robot_angle_step()
#         b[1][0] += 0.0  # need to move according to angle ;(
#         b[1][1] += 0.0
#         b[1][2] += 0

#         # Creates nb_candidates new subsample for each best candidate
#         for _ in range(0, nb_candidates):
#             # Resample around a 1 centimer wide box.
#             x = b[1][0] + uniform(-0.01, 0.01)
#             y = b[1][1] + uniform(-0.01, 0.01)

#             # Keeps the resampling in the box
#             if x > .96:
#                 x = .96
#             elif x < -.96:
#                 x = -.96

#             if y > .58:
#                 y = .58
#             elif y < -.58:
#                 y = -.58

#             re_candidates.append([x, y, randint(0, 360)])

#     best_candidates = get_best_candidates(re_candidates)
    # [(plt.scatter(be[1][0], be[1][1], c='r')) for be in best_candidates]


# print(avg_xya(best_candidates))
# [(plt.scatter(be[1][0], be[1][1], c='r')) for be in best_candidates]
# plt.show()

# TODO use the color sensor afterward
