import pygame
import neat
import time
import os
import random

pygame.init()

WINDOWS_WIDTH=500
WINDOWS_HEIGHT=800

# 2x for scaling and visibility
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG= pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG= pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG= pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

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
        self.tick_count += 1 # tick happened and a frame went by
        d=self.vel*self.tick_count + 1.5*self.tick_count**2
        # displacement= -10.5 * 1 + 1.5(1)**2 = -10.5 + 1.5 = -9

        if d>=16:
            d=16 # moving down so move down with no addition down movement
        
        if d<0:
            d -= 2 # move updwards so move a up a little bit more (fine-tuning)
       
        self.y=self.y + d   

        # check if bird position is above initial postition so now it is moving up but doesnt fall down yet
        # when the bird passes that point so now make it tilt downwards    
        if d < 0 or self.y<self.height + 50:
            if self.tilt < self.MAX_POSITION: # MAX_ROTATIONS =25
                self.tilt=self.MAX_POSITION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL # as the bird falls it will seem as it is nose-diving to the ground

    def draw(self, win):
        self.img_count += 1

        # wings flapping up and down based on animation time
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count=0

        # no flapping wings while nose-diving
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image=pygame.transform.rotate(self.img, self.tilt)
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center) # no idea how this works but gets the job done
        win.blit(rotated_image, new_rect.topleft) # blit=draw

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

def draw_window(win, bird):
    win.blit(BG_IMG, (0,0))
    bird.draw(win)
    pygame.display.update()

    
def main():
    bird=Bird(200,200)
    win=pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
    clock=pygame.time.Clock()

    run=True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
        
        bird.move()
        draw_window(win, bird)

    pygame.quit()


if __name__ == "__main__":
    main()