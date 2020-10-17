import pytest
from mtcarlo2 import *


def test_fitness():
    for i in range(0, 360, 10):
        print(f'\n angle = {i}' )
        r1 = Robot(x=0, y=0, angle=0)
        l1 = r1.get_simulated_lidar_values()
        print("---\nl1", l1)
        r2 = Robot(x=0, y=0, angle=i)
        l2 = r2.get_simulated_lidar_values()
        print("---\nl2", l2)
        l1 = [round(x, 3) for x in l1]
        l2 = [round(x, 3) for x in l2]
        print(l1)
        print(l2)
        print(lidar_fitness(l1, l2))


def test_print_map():
    ax = plt.figure()
    x, y = ARENA.map.xy
    fig = plt.figure(1, figsize=(5,5), dpi=90)
    ax =  fig.add_subplot(111)
    ax.plot(x, y, color='#6699cc', alpha=0.7,
            linewidth=3, solid_capstyle='round', zorder=2)
    ax.set_title('')
    plt.show()


if __name__ == '__main__':
    # test_print_map()
    test_fitness()

