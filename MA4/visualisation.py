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


# def draw_point(screen, p):
#     print("\n")
#     print("\n")
#     print(p)
#     pygame.draw.circle(screen, blue, p, 0.5)
#     print("\n")
#     print("\n")


def simulate(screen, state=STATE):
    from time import sleep
    draw_arena(screen)
    print(state)
    r = state['rpos']
    x, y = scale(r['x'], r['y'])
    draw_robot(screen, (x, y), r['a'], virtual=True)
    for point in state['spos']:
        pygame.draw.circle(screen, blue, scale(point[0], point[1]), 5)
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
    points = obj['spos']
    draw_arena(screen)
    draw_robot(screen, (r[0], r[1]), r[2], virtual=True)
    # for p in points:
    #     draw_point(screen, p)

# Game loop.


def game_loop(init_state):
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


W = 1.94  # width of arena
H = 1.18  # height of arena
states = []

with open('trajectory.json', 'r') as f:
    lines = f.readlines()

for l in lines:
    r = json.loads(l)
    # print(r)
    print(r['rpos']['x'])
    states.append(r)

# print(robots_coor)
game_loop(init_state=states)
