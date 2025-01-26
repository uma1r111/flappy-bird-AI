import pygame
import neat
import time
import os
import random

WINDOWS_WIDTH=600
WINDOWS_HEIGHT=800

# 2x for scaling and visibility
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG= [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))]
BASE_IMG= [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))]
BG_IMG= [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))]

class Bird:
    IMGS=BIRD_IMG
    MAX_POSITION=25 # How much bird is going to tilt. When bird is moving up it will tilt upwards and vice versa for down movements
    ROT_VEL=20 # How much bird will rotate on each frame everytime the bird moves
    ANIMATION_TIME=5 # How long the bird animation will be shown (more time will slow down wing flapping and vice versa for less time)

    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.tilt=0 # image is tilted, initially it will be flat
        self.tick_count=0 # physics of how will the bird go up and down
        self.vel=0 # initial velocity
        self.height=self.y # another height for tilting
        self.img_count=0 # which image is currently showing the bird (for tracking purposes)
        self.img=self.IMGS[0] # references class -> BIRD_IMG will will point towards BIRD_IMG(scalibility and visibility)

    def jump(self):
         self.vel=-10.5 # coordinate (0,0) is top left corner in pygame so velocity for moving up will be ngative and moving down will be positive
         self.tick_count=0 # to track when we last jumped
         self.height = self.y # where the bird jumped from

    def move(self):
        self.tick_count=0