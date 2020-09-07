
class BLOCK():
    ROAD = 0
    WALL = 1
    DIAM = 3
    ROBOT = 4
    GOAL = 5
    DIAM_ON_GOAL = 6 


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def blue(text):
    return bcolors.OKBLUE + text + bcolors.ENDC


def red(text):
    return bcolors.WARNING + text + bcolors.ENDC


def green(text):
    return bcolors.OKGREEN + text + bcolors.ENDC



def print_map(map):
    for col in map:
        for x in col:
            if x == BLOCK.WALL:
                print(red('⬛'), end='')
            elif x == BLOCK.ROBOT:
                print('🤖', end='')
            elif x == BLOCK.DIAM:
                print('💎', end='')
            elif x == BLOCK.DIAM_ON_GOAL:
                print('🏁', end='')
            elif x == BLOCK.GOAL:
                print(green('⬛'), end='')
            elif x == BLOCK.ROAD:
                print('  ', end='')
            else:
                print('  ', end='')
        print('')

def test_print_map():
    init_map   =  [[1,1,1,1,1,1,1,1,1],
                   [1,4,0,0,0,0,0,0,1],
                   [1,5,1,3,1,0,1,0,1],
                   [1,0,0,0,0,0,0,0,1],
                   [1,0,1,3,1,0,1,0,1],
                   [1,0,0,0,0,5,0,0,1],
                   [1,0,1,0,1,0,1,0,1],
                   [1,6,0,0,0,0,0,0,1],
                   [1,1,1,1,1,1,1,1,1]]

    print_map(init_map)

