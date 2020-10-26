import sys
 
import pygame
from pygame.locals import *
from dataclasses import dataclass


red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
white = (255,255, 255)
black = (0,0,0)
light_black = (130,130,130)
light_red = (255,130,130)
 
margin_w, margin_h = 50, 50
zoom = 4
arena_w, arena_h = 194*zoom, 118*zoom

screen_width, screen_height = arena_w + 2*margin_w, arena_h + 2*margin_h,

def rot_center(image, rect, angle):
    rot_img = pygame.transform.rotate(image, angle)
    rot_rect = rot_img.get_rect(center=rect.center)
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

def draw_robot(screen, pos, angle, virtual=False, size=(40,40)):
    if virtual:
        color = light_black
        bg_color = light_red
    else:
        # bg_color = black
        color = black
        bg_color = red
    image = pygame.Surface(size, pygame.SRCALPHA, 32)
    # image.fill(bg_color)
    rect = image.get_rect()
    rect.topleft = pos
    poly = ((0,0),(0,40),(10,40),(40,20),(10,0))
    pygame.draw.polygon(image, color, poly)
    img, rect = rot_center(image, rect, angle)
    screen.blit(img, rect)



def draw_arena(screen):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, white,(margin_w,margin_h,arena_w,arena_h))
    pygame.draw.circle(screen, blue,   (margin_w         ,margin_h), 20)
    pygame.draw.circle(screen, yellow, (arena_w+margin_w ,margin_h), 20)
    pygame.draw.circle(screen, green,  (margin_w         ,arena_h+margin_h), 20)
    pygame.draw.circle(screen, red,    (arena_w+margin_w ,arena_h+margin_h), 20)


def simulate(screen):
    robots = [((100, 100), 57), ((200,200), 180)]
    from time import sleep
    draw_arena(screen)
    for r in robots:
        draw_robot(screen, r[0], r[1], virtual=True)


# Game loop.
def game_loop():
    pygame.init()
    fps = 30
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((screen_width, screen_height))
    while True:
        simulate(screen)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip() # render drawing
        fpsClock.tick(fps)

if __name__ == "__main__":
    game_loop()
