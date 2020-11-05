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

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.a)


def distance(s, x, y):
    return sqrt((s.x-x)**2+(s.y-y)**2)
