
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



def render_map(map, with_color=True):
    res = ""
    for col in map:
        for x in col:
            if x == BLOCK.WALL:
                if with_color:
                    res += red('🔥')
                else:
                    res += '🔥'
            elif x == BLOCK.ROBOT:
                res += '🤖'
            elif x == BLOCK.DIAM:
                res += '💎'
            elif x == BLOCK.DIAM_ON_GOAL:
                res += '✅'
            elif x == BLOCK.GOAL:
                if with_color:
                    res += green('🏁')
                else:
                    res += '🏁'
            elif x == BLOCK.ROAD:
                res += '  '
            else:
                res += '??'
        res += '\n'
    return res

def test_render_map():
    init_map   =  [[1,1,1,1,1,1,1,1,1],
                   [1,4,0,0,0,0,0,0,1],
                   [1,5,1,3,1,0,1,0,1],
                   [1,0,0,0,0,0,0,0,1],
                   [1,0,1,3,1,0,1,0,1],
                   [1,0,0,0,0,5,0,0,1],
                   [1,0,1,0,1,0,1,0,1],
                   [1,6,0,0,0,0,0,0,1],
                   [1,1,1,1,1,1,1,1,1]]

    render_map(init_map)

