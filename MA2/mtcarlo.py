import shapely
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, subtract, std, mean
from random import *
from math import floor

W = 1.18  # width of arena
H = 1.94  # height of arena
# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

nb_candidates = 14


def calculate_distance(a, b):
    return sum(abs(subtract(a, b)))


def return_inter(alpha, x, y):
    global world

    ray = LineString([(x, y + 0.0778), (x+cos(alpha)*2*W, (y+sin(alpha)*2*H))])
    print("------")
    print(ray)
    print(x, y)
    s = world.intersection(ray)
    print(s)
    return sqrt((s.x-x)**2+(s.y-y)**2)


def get_simulated_lidar_values(x):
    # shift of alpha so that both the robot and the simulation look in the same direction
    return [return_inter((x[2] + (alpha * 36)) % 360, x[0], x[1]) for alpha in range(0, 10)]


def get_lidar_values():
    #! Dummy values
    return [uniform(0.01, 1.94) for x in range(0, 10)]


def get_best_candidates(samples):
    # Contains a list of 100 lidar simlutation (each with 360 rays)
    lr_samples = [(get_simulated_lidar_values(x), x) for x in samples]

    DISTrr = get_lidar_values()

    candidates = [((calculate_distance(DISTrr, sample[0]), sample[1]))
                  for sample in lr_samples]

    # # sort by second index
    candidates.sort(key=lambda candidates: candidates[0])

    return candidates[:floor(len(candidates)/2)]


# samples = [(uniform(-0.58, .58), uniform(-.96, .96), randint(0, 360))
# Create 100 samples
samples = [(uniform(-0.58, .58), uniform(-.96, .96), randint(0, 360))
           for _ in range(0, nb_candidates)]

best_candidates = get_best_candidates(samples)

# Preferably needs to become while not converged
while True:
    #! [NTA] move the samples accordingly the fuck?
    DISTrr = get_lidar_values()

    sigma = std([(b[1][0], b[1][1]) for b in best_candidates])
    re_candidates = []
    for b in best_candidates:
        m = .5  # ! how??
        for _ in range(0, 3):
            re_candidates.append(
                (gauss(m, sigma), gauss(m, sigma), randint(0, 360)))

    best_candidates = get_best_candidates(re_candidates)
    print(best_candidates)
