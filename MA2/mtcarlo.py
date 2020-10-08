from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean
import matplotlib.pyplot as plt
from math import floor
from random import *
import shapely

H = 1.18  # width of arena
W = 1.94  # height of arena

# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

nb_samples = 200
nb_candidates = 10


# return the average position of the robot on the map
def avg_xya(os):
    return (mean([x[1][0] for x in os]), mean([x[1][1]
                                               for x in os]), mean([x[1][2] for x in os]))


def get_robot_angle_step():
    return 20


# Fitness function
def calculate_distance(a, b):
    return sum(abs(subtract(a, b)))


# Return world intersection with a ray
def return_inter(alpha, x, y):
    global world
    ray = LineString([(x, y), (x+cos(alpha)*2*W, (y+sin(alpha)*2*H))])
    s = world.intersection(ray)
    return sqrt((s.x-x)**2+(s.y-y)**2)


# Get the lidar values for simulated samples
def get_simulated_lidar_values(x):
    # shift of alpha so that both the robot and the simulation look in the same direction
    # ? - or + shift
    return [return_inter((x[2] + (alpha * 36)) % 360, x[0], x[1]) for alpha in range(0, 10)]


# Return the values thymio lidar sensor
def get_lidar_values():
    #! Dummy values
    return [uniform(0.01, 1.94) for x in range(0, 10)]


# Return the nb_candidates best candidates
def get_best_candidates(samples):
    # Contains a list of nb_samples lidar simlutation (each with 10 rays)
    lr_samples = [(get_simulated_lidar_values(x), x) for x in samples]

    DISTrr = get_lidar_values()

    candidates = [((calculate_distance(DISTrr, sample[0]), sample[1]))
                  for sample in lr_samples]

    # # sort by second index
    candidates.sort(key=lambda candidates: candidates[0])

    return candidates[: nb_candidates]


# Create nb_samples samples
samples = [[uniform(-.96, .96), uniform(-0.58, .58), randint(0, 360)]
           for _ in range(0, nb_samples)]

best_candidates = get_best_candidates(samples)
[(plt.scatter(be[1][0], be[1][1], c='b')) for be in best_candidates]
iter = 0
while iter != 20:
    iter += 1

    # DISTrr = get_lidar_values()

    # Move the robot and the sample accordingly
    # By design the step function will be moving the robot 1cm ahead, the choice of the angle is not defined yet so dummy value
    for b in best_candidates:
        b[1][0] += 0.01  # need to move according to angle ;(
        b[1][1] += 0.01
        b[1][2] += get_robot_angle_step()

    # Resample
    re_candidates = []
    for b in best_candidates:
        # Creates nb_candidates new subsample for each best candidate
        for _ in range(0, nb_candidates):
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

    best_candidates = get_best_candidates(re_candidates)

print(avg_xya(best_candidates))
[(plt.scatter(be[1][0], be[1][1], c='r')) for be in best_candidates]
plt.show()
# TODO use the color sensor afterward
