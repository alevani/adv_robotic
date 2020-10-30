from numpy import sqrt


class State:
    def __init__(self):
        super().__init__()


class Action:
    ''' In our case, actions are motos actions'''

    def __init__(self, left, right):
        self.left = left
        self.right = right


class Position:
    def __init__(self, x, y, a):
        self.x = x
        self.y = y
        self.a = a


def distance(s, x, y):
    try:
        return sqrt((s.x-x)**2+(s.y-y)**2)
    except:
        # print(s)
        # print(y)
        # print(x)
        return 0
