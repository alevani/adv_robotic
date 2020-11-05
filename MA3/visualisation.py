import sys

import pygame
from time import sleep
import math
import json
from pygame.locals import *
from dataclasses import dataclass


red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)
light_black = (130, 130, 130)
light_red = (255, 130, 130)

STATE = {}

ROBOT_SIZE = 40
margin_w, margin_h = 50, 50
zoom = 4
arena_w, arena_h = 194*zoom, 118*zoom

screen_width, screen_height = arena_w + 2*margin_w, arena_h + 2*margin_h,


def rot_center(image, rect, angle):
    rot_img = pygame.transform.rotate(image, angle)
    rot_rect = rot_img.get_rect(center=rect.center)
    # rot_rect = rot_img.get_rect()
    return rot_img, rot_rect


# class Robot(pygame.sprite.Sprite):
#     # https://stackoverflow.com/questions/62708039/drawing-polygons-onto-a-sprites-surface-as-its-image-in-pygame
#     def __init__(self, screen, pos, angle=0, size=(40,40)):
#         pygame.sprite.Sprite.__init__(self)
#         self.screen = screen
#         self.image = pygame.Surface(size, pygame.SRCALPHA, 32)
#         self.image.fill(black)
#         self.rect = self.image.get_rect()
#         self.rect.topleft = pos
#         self.angle = angle
#         self.pos = pos

#         # Draw a random polygon into the image
#         poly = ((0,0),(0,40),(30,40),(40,20),(30,0))
#         pygame.draw.polygon( self.image, red, poly )

#         # Create the collision mask (anything not transparent)
#         # self.mask = pygame.mask.from_surface( self.image )
#     def draw(self, screen):
#         img, rect = rot_center(self.image, self.rect, self.angle)
#         screen.blit(img, rect)

#     def rotate(self, angle):
#         self.angle = angle

def draw_robot(screen, pos, angle, virtual=False, size=ROBOT_SIZE):
    if virtual:
        color = light_black
        bg_color = light_red
    else:
        # bg_color = black
        color = black
        bg_color = red
    image = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # image.fill(bg_color)
    rect = image.get_rect()
    x, y = pos
    rect.topleft = (x-size/2, y-size/2)
    poly = ((0, 0), (0, size), (size//2, size), (size, size//2), (size//2, 0))
    pygame.draw.polygon(image, color, poly)

    a = math.degrees(angle)
    img, rect = rot_center(image, rect, a)
    screen.blit(img, rect)


def draw_arena(screen):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, white, (margin_w, margin_h, arena_w, arena_h))
    pygame.draw.circle(screen, blue,   (margin_w, margin_h), 20)
    pygame.draw.circle(screen, yellow, (arena_w+margin_w, margin_h), 20)
    pygame.draw.circle(screen, green,  (margin_w, arena_h+margin_h), 20)
    pygame.draw.circle(
        screen, red,    (arena_w+margin_w, arena_h+margin_h), 20)


def draw_ray(screen, start, end):
    pygame.draw.line(screen, red, start, end)


def draw_ray(screen, start, end):
    pygame.draw.line(screen, red, start, end)


def simulate(screen, state=STATE):
    from time import sleep
    draw_arena(screen)
    print(state)
    r = state['rpos']
    x, y = scale(r['x'], r['y'])
    draw_robot(screen, (x, y), r['a'], virtual=True)
    for ray in state['spos']:
        x, y = scale(ray[0][0], ray[0][1])
        xx, yy = scale(ray[1][0], ray[1][1])
        draw_ray(screen, (x, y), (xx, yy))
    for point in state['bpos']:
        print(point)
        pygame.draw.circle(screen, red, scale(point[0], point[1]), 5)


def scale(x, y):
    '''
    transpose from particule filter coordinate system
    to pygame coordinate system
    '''
    tresh = 20
    nx = arena_w/2 + x*100*zoom + margin_w - ROBOT_SIZE/2 + tresh
    ny = arena_h/2 + y*100*zoom * -1 + margin_h - ROBOT_SIZE/2+tresh
    return nx, ny


def draw_from_json(screen, json_str):
    obj = json.loads(json_str)
    rbt = obj['rpos']
    robot = (rbt['x'], rbt['y'], rbt['a'])
    rays = obj['spos']
    draw_arena(screen)
    draw_robot(screen, (r[0], r[1]), r[2], virtual=True)
    for ray in rays:
        draw_ray(screen, ray[0], ray[1])

# Game loop.


def game_loop(robots_coor, init_state):
    pygame.init()
    fps = 30
    pause = False
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((screen_width, screen_height))
    # while True:
    for state in init_state:
        simulate(screen, state)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = True
                    sleep(5)
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()  # render drawing
        fpsClock.tick(fps)


def read_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = [x.split(',') for x in lines]  # x,y,a in radians
    return lines


if __name__ == "__main__":
    robots_coor = read_file('trajectory.dat')
    W = 1.94  # width of arena
    H = 1.18  # height of arena
    # rj = '{"rpos": {"x": 2.504402704257438e-17, "y": 0.40900000000026826, "a": 1.5707963267948966}, "spos": [[[-0.049999999999999975, 0.46900000000026826], [-2.5440159255837727, 2.2768648857610563]], [[-0.024999999999999977, 0.48400000000026827], [-1.2561420668517567, 2.7220438262868987]], [[2.504402704257438e-17, 0.48680000000026824], [2.6262550607716093e-16, 2.8468000000002682]], [[0.025000000000000026, 0.4340000000002683], [1.2561420668517573, 2.672043826286899]], [[0.05000000000000003, 0.46900000000026826], [2.5440159255837727, 2.2768648857610563]]]}'
    # rj = '{"rpos": {"x": 3.582091887503807e-17, "y": 0.5849999999999724, "a": 1.5707963267948966}, "spos": [[[3.582091887503807e-17, 0.5849999999999724], [-2.494015925583773, 2.39286488576076]], [[3.582091887503807e-17, 0.5849999999999724], [-1.2311420668517568, 2.823043826286603]], [[3.582091887503807e-17, 0.5849999999999724], [2.7340239790962463e-16, 2.9449999999999723]], [[3.582091887503807e-17, 0.5849999999999724], [1.2311420668517572, 2.823043826286603]], [[3.582091887503807e-17, 0.5849999999999724], [2.494015925583773, 2.39286488576076]]]}'
    # rj = '{"rpos": {"x": 0.3, "y": 0.5, "a": 0.7853981633974483}, "spos": [[[0.3, 0.5], [0.6381642818609136, 2.8510194874965196]], [[0.3, 0.5], [2.0312475148660587, 2.612045093380779]], [[0.3, 0.5], [3.0435743110038045, 2.1687720036002522]], [[0.3, 0.5], [3.7723453230158572, 1.5530268389391486]], [[0.3, 0.5], [4.165235428595973, 0.7056875528844733]]]}'
    # state = json.loads(rj)
    states = []

    with open('trajectory.json', 'r') as f:
        lines = f.readlines()

    for l in lines:
        r = json.loads(l)
        # print(r)
        print(r['rpos']['x'])
        states.append(r)

    # print(robots_coor)
    game_loop(robots_coor, init_state=states)
