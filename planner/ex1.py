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
            'diam2' : (4,3,3),  }

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
            elif map[y][x] == BLOCK.GOAL:
                map[y][x] = BLOCK.GOAL
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

def robot_over_diam(agents ):
    ry, rx, _ =  agents['robot']
    target = (ry, rx, BLOCK.DIAM)
    diam = [ a for a in agents.items() if a[1] == target ]

    if len(diam) > 1:
        print("\n ERROR : robot on TWO diamons !!! \n This shouldn't happen")
        print(diam)
    return diam

def add_agent_to_map(agents, static_map):
    cur_map = deepcopy(static_map)
    # check if robot not above diamon
    if len(robot_over_diam(agents)) > 0:
        print("\n ERROR : robot on diamon !!! \n")
    for ag in agents.values():
        y, x, t = ag
        cur_map[y][x] = t
    # y, x, t = agents['robot']
    cur_map[y][x] = t

    return cur_map

def remove_robot_map(map):
    map = list(map)
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == BLOCK.ROBOT:
                map[y][x] = BLOCK.ROAD
    return map

def move_agent(dir, apos, map) ->  tuple:
    y, x, t = apos
    if dir == 'N':
        return ( y-1,x, t)

    elif dir == 'S':
        return ( y+1,x, t)

    elif dir == 'W':
        return ( y,x-1, t)

    elif dir == 'E':
        return ( y ,x+1, t)


def get_type(dir, rpos, map):
    y, x,  _ = rpos
    if dir == 'N':
        return map[y-1][x]

    elif dir == 'S':
        return map[y+1][x]

    elif dir == 'W':
        return map[y][x-1]

    elif dir == 'E':
        return map[y][x+1]


def not_hitting_wall(dir, rpos, map):
    return get_type(dir, rpos, map) == BLOCK.WALL

def going_back(new_agents, prev_states=PREVIOUS_STATES):
    # pprint("PREVIOUS_STATES")
    # pprint(PREVIOUS_STATES)
    # print("new_agents", new_agents)

    if new_agents in PREVIOUS_STATES:
        return True
    else:
        return False
   

def user_input(dirs):
    i = input('go:')
    i = i.replace('w', 'N').replace('a', 'W').replace('s', 'S').replace( 'd', 'E')
    i = i[0]
    if i in dirs:
        return [i]
    else:
        user_input(dirs)


def rec_tick(agents, path='', it=0):

    cur_map = add_agent_to_map(agents, STATIC_MAP)
    print_map.print_map(cur_map)

    if remove_robot_map(cur_map) == FINAL_MAP:
        return True

    else:
        it = it + 1
        dirs = ['N', 'W', 'S', 'E']
        dirs = user_input(dirs)

        for d in dirs:
            rpos = agents['robot']
            # print("agents", agents)

            if get_type(d, rpos, cur_map) != BLOCK.WALL:
                new_agents = deepcopy(agents)
                new_agents['robot'] = move_agent(d, agents['robot'], cur_map)

                if len(robot_over_diam(new_agents)) > 0:
                    diam_id = robot_over_diam(new_agents)[0][0]
                    print("diam_id", diam_id)
                    new_diam = move_agent(d, agents[diam_id], cur_map)
                    new_agents[diam_id] = new_diam

                if not going_back(new_agents):
                    path += d
                    PREVIOUS_STATES.append(new_agents)
                    # print("Going : ", d)
                    # print("Next rpos:", new_agents['robot'])
                    # input("continue?")
                    rec_tick(new_agents, path, it)


if __name__ == '__main__':
    from pprint import pprint
    FINAL_MAP   =  create_final(init_map)
    STATIC_MAP = create_static(init_map)
    cur_map = deepcopy(init_map)
    PREVIOUS_STATES.append(agents)
    if rec_tick(agents):
        print("Successfully finished iteration")


