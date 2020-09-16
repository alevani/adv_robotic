#! /usr/bin/env python3
from copy import copy, deepcopy
from pprint import pprint
import print_map
import MAPS
from MAPS import BLOCK
import map_parser
from collections import defaultdict


PREVIOUS_STATES = []
SOLUTIONS = []
AGENTS = {}
GOALS = []
DIRS = ['N', 'W', 'S', 'E']
MAP = MAPS.claire
SHORTEST_PATH_TO_STATE = defaultdict(list)
DEBUG=True

def debug(*args):
    if DEBUG:
        print(*args)


def move_agent(dir, apos) ->  tuple:
    y, x, t = apos
    if dir == 'N':
        return ( y-1,x, t)

    elif dir == 'S':
        return ( y+1,x, t)

    elif dir == 'W':
        return ( y,x-1, t)

    elif dir == 'E':
        return ( y ,x+1, t)


def is_robot_over_diam(agents) -> bool:
    ry, rx, _ =  agents['robot'][0]
    target = (ry, rx, BLOCK.DIAM)
    diam = [ a for a in agents['diams'] if a == target ]

    if len(diam) > 1:
        print("\n ERROR : robot on TWO diamons !!! \n This shouldn't happen")
        print(diam)
    elif len(diam) <1:
        False
    else:
        return True



def push_diams(dir, diam, agents):
    next_diam = move_agent(dir, diam)
    over_lapping_diams = [ a for a in agents['diams'] if a == next_diam ]

    if len(over_lapping_diams) == 1:
        return push_diams(dir, next_diam, agents)
    elif len(over_lapping_diams) < 1:
        return next_diam
    elif len(over_lapping_diams) > 1:
        raise Exception("\n ERROR :Two diams at the same spot.")
        print(over_lapping_diams, next_diam)




def try_move_agent(dir, apos, cur_map) ->  tuple:
    y, x, t = apos
    next_ = get_type_surrounding(dir, apos, cur_map)

    if next_ == BLOCK.ROAD or next_ == BLOCK.GOAL:
        return (move_agent(dir, apos), True)

    elif next_ == BLOCK.WALL:
        return (apos, False)

    elif next_ == BLOCK.DIAM or next_ == BLOCK.DIAM_ON_GOAL:
        diam_pos = move_agent(dir, apos)
        next_diam_pos, _ = try_move_agent(dir,  diam_pos, cur_map)
        if next_diam_pos == diam_pos:
            return (apos, False)
        else:
            return (move_agent(dir, apos), True)

        
    elif next_ == BLOCK.ROBOT:
        raise Exception("Impossible move")

def get_type_surrounding(dir, rpos, map):
    y, x,  _ = rpos
    if dir == 'N':
        return map[y-1][x]

    elif dir == 'S':
        return map[y+1][x]

    elif dir == 'W':
        return map[y][x-1]

    elif dir == 'E':
        return map[y][x+1]

   


def next_state(dir, agents):
    rpos = agents['robot'][0]
    cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)

    new_rpos, _ = try_move_agent(dir, rpos , cur_map)
    if new_rpos == rpos:
        return (agents, False)
    else:
        new_agents = deepcopy(agents)
        new_agents['robot'][0] = new_rpos
        if is_robot_over_diam(new_agents):
            y, x, _ = new_rpos
            diam = (y, x, BLOCK.DIAM)
            new_diam = push_diams(dir, diam, agents)

            new_agents['diams'].remove(diam)
            new_agents['diams'].append(new_diam)

        return (new_agents, True)

def diam_on_corner(cur_map) -> bool:
    H = len(cur_map)
    W = len(cur_map[0])
    cs = []
    cs.append((1, 1))
    cs.append((1, W-2))
    cs.append((H-2, 1))
    cs.append((H-2, W-2))
    for c in cs:
        t = cur_map[c[0]][c[1]]
        if t == BLOCK.DIAM:
            return True
        elif t == BLOCK.DIAM_ON_GOAL:
            surr = []
            surr.append(cur_map[c[0]-1][c[1]])
            surr.append(cur_map[c[0]+1][c[1]])
            surr.append(cur_map[c[0]][c[1]-1])
            surr.append(cur_map[c[0]][c[1]+1])
            if BLOCK.DIAM in surr:
                return True

    return False

def diam_on_empty_edge(cur_map) -> bool:
    H = len(cur_map)
    W = len(cur_map[0])
    es = []
    es.append(cur_map[1])
    es.append(cur_map[H-2])
    es.append([ line[1] for line in cur_map])
    es.append([ line[W-2] for line in cur_map])
    for e in es:
        # print('edge : ', es)
        if BLOCK.DIAM in e and not BLOCK.GOAL in e:
            return True

    return False

def heuristic(agents):
    nb_ok  = 0
    for d in agents['diams']:
        y, x, _ = d
        if STATIC_MAP[y][x] == BLOCK.GOAL:
            nb_ok += 1

    return nb_ok


def calc_manhattan( p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def remaining_diams(diams, map):
    return [ d for d in diams if map[d[0]][d[1]] != BLOCK.GOAL ]

def heuristic2(agents, goals=GOALS):
    debug(goals)
    diams_pos = agents['diams']
    targets = goals
    targets_left = len(targets)
    total = 0
    total_robot = 0
    debug(targets)
    for ind, (y,x,t) in enumerate(diams_pos):
        print("diams_pos", diams_pos)
        print("targets", targets)

        total += calc_manhattan((y,x), targets[ind])
        if (y,x) in targets:
            targets_left -= 1

    for (y, x, t) in remaining_diams(agents['diams'], STATIC_MAP):
        total_robot += calc_manhattan((y,x), agents['robot'][0])

    return total * targets_left + total_robot*0.1

def hash_agent(agents):
    r1 = tuple(agents['robot'])
    r2 = tuple(agents['diams'])
    return hash((*r1, *r2))

visited = [] # List to keep track of visited nodes.
queue = []     #Initialize a queue

def bfs( agents):
    visited.append(agents)
    queue.append((agents, ''))

    while queue:
        agents, path = queue.pop(0)
        cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)
        debug(print_map.render_map(cur_map))
        debug(agents)
        if map_parser.remove_robot_map(cur_map) == FINAL_MAP:
            SOLUTIONS.append(agents)
            debug(SOLUTIONS)
            debug(SHORTEST_PATH_TO_STATE[hash_agent(agents)])
            return 
            # input("enter to continue")
        elif diam_on_corner(cur_map):
            continue
        elif diam_on_empty_edge(cur_map):
            continue
        # if nb diam on edge > nb goal
        else:
            neighbours = []
            for d in DIRS:
                 new_agents, has_changed = next_state(d, agents)
                 if has_changed:
                   new_path = path + d
                   neighbours.append((new_agents, new_path))
            # sort by heuristic here
            for neighbour, path in neighbours:
                if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append((neighbour, path))
                    SHORTEST_PATH_TO_STATE[hash_agent(neighbour)].append(path)

    debug("*** FINISHED ***")
    for agents in SOLUTIONS:
        debug("---")
        paths = SHORTEST_PATH_TO_STATE[hash_agent(agents)]
        sols =  sorted(paths, key=lambda x: len(x))
        sols.reverse()
        debug(sols)



# Driver Code
def rec_tick(agents, path='', it=0):
    cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)
    print(it, path)
    print(print_map.render_map(cur_map))

    # if len(SOLUTIONS) > 0:
    #     return True

    if map_parser.remove_robot_map(cur_map) == FINAL_MAP:
        SOLUTIONS.append(min(SHORTEST_PATH_TO_STATE[hash_agent(agents)]))
        debug(SHORTEST_PATH_TO_STATE[hash_agent(agents)])
        debug(len(SHORTEST_PATH_TO_STATE[hash_agent(agents)]))
        debug(len(SHORTEST_PATH_TO_STATE[hash_agent(agents)][0]))
        input("enter to continue")
        return True
    elif diam_on_corner(cur_map):
        pass
    elif diam_on_empty_edge(cur_map):
        pass
    else:
        it = it + 1
        candidats =[]
        for d in DIRS:
            new_path = path + d
            new_agents, _ = next_state(d, agents)

            SHORTEST_PATH_TO_STATE[hash_agent(new_agents)].append(new_path)

            if not new_agents in PREVIOUS_STATES:
                PREVIOUS_STATES.append(new_agents)
                # input('continue?')
                candidats.append((new_agents, new_path, it))
                sorted_candidats = sorted(candidats, key= lambda x: heuristic2(x[0], GOALS))
                for candidat in sorted_candidats:
                    rec_tick(*candidat)


def curse(agents):
    import sys,os
    import curses

    def draw_menu(stdscr, agents):
        k = 0

        # Clear and refresh the screen for a blank canvas

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        stdscr.clear()
        cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)
        map = print_map.render_map(cur_map, False)
        stdscr.addstr(0, 0, map, curses.color_pair(1))
        stdscr.refresh()

        # Loop where k is the last character pressed
        while (k != ord('q')):

            # Initialization
            stdscr.clear()
            # height, width = stdscr.getmaxyx()
            dir = ''

            if k == curses.KEY_DOWN:
                dir = 'S'
            elif k == curses.KEY_UP:
                dir = 'N'
            elif k == curses.KEY_RIGHT:
                dir = 'E'
            elif k == curses.KEY_LEFT:
                dir = 'W'
            elif k == ord('p'):
                m1 = map_parser.remove_robot_map(cur_map)
                m2 =  FINAL_MAP
                stdscr.addstr(0, 0, print_map.render_map(m1, False), curses.color_pair(2))
                dir = None

            else:
                dir = None

            if dir:
                new_agents, _ = next_state(dir, agents)
                agents = deepcopy(new_agents)
            cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)

            map = print_map.render_map(cur_map, False)
            stdscr.addstr(1, 0, map, curses.color_pair(1))
            if map_parser.remove_robot_map(cur_map) == FINAL_MAP:
                stdscr.addstr(0, 0, "SUCCESS", curses.color_pair(2))

            # Rendering some text

            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

    curses.wrapper(draw_menu, agents)


def user_input(dirs):
    i = input('go:')
    i = i.replace('w', 'N').replace('a', 'W').replace('s', 'S').replace('d', 'E')
    return i


def step(agents):
    cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)
    print(print_map.render_map(cur_map))

    scenario = ''

    while map_parser.remove_robot_map(cur_map) != FINAL_MAP:
        cur_map = map_parser.add_agent_to_map(agents, STATIC_MAP)
        print('heur', heuristic2(agents, GOALS))
        print(print_map.render_map(cur_map))
        if len(scenario) < 1:
            scenario = user_input(DIRS)
            print("scenario", scenario)
        dir = scenario[0]
        scenario = scenario[1:]
        new_agents, _ = next_state(dir, agents)
        agents = deepcopy(new_agents)
        input('continue?\n\n')





if __name__ == '__main__':
    from pprint import pprint
    import sys
    MAP = map_parser.parse_from_text_file('./compet.txt')
    # MAP = MAPS.init
    print(MAP)
    print_map.render_map(MAP)
    FINAL_MAP   =  map_parser.create_final(MAP)
    STATIC_MAP, AGENTS, GOALS = map_parser.parse_map(MAP)
    cur_map = deepcopy(MAP)
    PREVIOUS_STATES.append(AGENTS)
    if sys.argv[1] == 'step':
        step(AGENTS)

    elif sys.argv[1] == 'bfs':
        sys.setrecursionlimit(10**6)
        bfs(AGENTS)

    elif sys.argv[1] == 'ia':
        sys.setrecursionlimit(10**6)

        # from ia import split_map
        # splited_maps = split_map(STATIC_MAP, GOALS)
        # for diam in AGENTS['diams']:
        #     agents = deepcopy(AGENTS)
        #     agents['diams'] = [diam]
        #     for m in splited_maps:
        #         STATIC_MAP = m
        #         rec_tick(agents)
        #     print('SOLS : ', sorted(SOLUTIONS, key=lambda x: len(x)))

        if rec_tick(AGENTS):
            print("Successfully finished iteration")
        print(sorted(SOLUTIONS, key=lambda x: len(x)))
    else:
        curse(AGENTS)


