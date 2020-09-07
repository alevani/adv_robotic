#! /usr/bin/env python3
from copy import copy, deepcopy
from pprint import pprint
import print_map

PREVIOUS_STATES = []

class BLOCK():
    ROAD = 0
    WALL = 1
    DIAM = 3
    ROBOT = 4
    GOAL = 5
    DIAM_ON_GOAL = 6 

agents = {  'robot' : (1,1,4),
            'diam1' : (2,3,3),
            'diam2' : (4,3,3),
            'goal1' : (2,1,5),
            'goal2' : (5,5,5) }

init_map   =  [[1,1,1,1,1,1,1,1,1],
               [1,4,0,0,0,0,0,0,1],
               [1,5,1,3,1,0,1,0,1],
               [1,0,0,0,0,0,0,0,1],
               [1,0,1,3,1,0,1,0,1],
               [1,0,0,0,0,5,0,0,1],
               [1,0,1,0,1,0,1,0,1],
               [1,6,0,0,0,0,0,0,1],
               [1,1,1,1,1,1,1,1,1]]


def create_static(imap):
    map = deepcopy(imap)
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == BLOCK.ROBOT:
                map[y][x] = BLOCK.ROAD
            elif map[y][x] == BLOCK.DIAM:
                map[y][x] = BLOCK.ROAD
    return map

def create_final(imap: list):
    map = deepcopy(imap)
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == BLOCK.ROBOT:
                map[y][x] = BLOCK.ROAD
            elif map[y][x] == BLOCK.GOAL:
                map[y][x] = BLOCK.DIAM_ON_GOAL
            elif map[y][x] == BLOCK.DIAM:
                map[y][x] = BLOCK.ROAD
    return map


def add_agent_to_map(agents, static_map):
    cur_map = deepcopy(static_map)
    # for ag in agents.values():
    #     x, y, t = ag
    #     cur_map[y][x] = t
    y, x, t = agents['robot']
    cur_map[y][x] = t

    return cur_map

def remove_robot_map(map):
    map = list(map)
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == BLOCK.ROBOT:
                map[y][x] = BLOCK.ROAD
    return map

def move_robot(dir, rpos, map):
    y, x, t = rpos
    if dir == 'N':
        return ( y-1,x, t)

    elif dir == 'S':
        return ( y+1,x, t)

    elif dir == 'W':
        return ( y,x+1, t)

    elif dir == 'E':
        return ( y ,x-1, t)

def get_type(dir, rpos, map):
    y, x,  _ = rpos
    if dir == 'N':
        return map[y-1][x]

    elif dir == 'S':
        return map[y+1][x]

    elif dir == 'W':
        return map[y][x+1]

    elif dir == 'E':
        return map[y][x-1]


def is_allowed(dir, rpos, map):
    t = get_type(dir, rpos, map)
    print("dir", dir)
    print("t", t)
    return t != BLOCK.WALL

def going_back(new_agents, prev_states=PREVIOUS_STATES):
    # pprint("PREVIOUS_STATES")
    # pprint(PREVIOUS_STATES)
    # print("new_agents", new_agents)

    if new_agents in PREVIOUS_STATES:
        return True
    else:
        return False
   


def rec_tick(agents, path='', it=0):

    cur_map = add_agent_to_map(agents, STATIC_MAP)
    print_map.print_map(cur_map)

    if cur_map == FINAL_MAP:
        return True

    else:
        it = it +1
        dirs = [ 'N', 'W', 'S', 'E']
        for d in dirs:
            rpos = agents['robot']
            # print("agents", agents)

            if is_allowed(d, rpos, cur_map):
                new_agents = deepcopy(agents)
                new_agents['robot'] = move_robot(d, agents['robot'], cur_map)
                if not going_back(new_agents):
                    path += d
                    PREVIOUS_STATES.append(new_agents)
                    # print("Going : ", d)
                    # print("Next rpos:", new_agents['robot'])
                    input("continue?")
                    rec_tick(new_agents, path, it)


if __name__ == '__main__':
    from pprint import pprint
    FINAL_MAP   =  create_final(init_map)
    STATIC_MAP = create_static(init_map)
    cur_map = deepcopy(init_map)
    PREVIOUS_STATES.append(agents)
    if rec_tick(agents):
        print("Successfully finished iteration")


