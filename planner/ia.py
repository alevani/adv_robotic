from MAPS import BLOCK
from copy import deepcopy

def split_map(static_map, goals):
    # remplace goals with wall
    only_wall_map = deepcopy(static_map)
    splited_maps = []
    for (y, x) in goals:
        only_wall_map[y][x] = BLOCK.WALL
    for (y, x) in goals:
        m = deepcopy(only_wall_map)
        m[y][x] = BLOCK.GOAL
        splited_maps.append(m)

    return splited_maps

