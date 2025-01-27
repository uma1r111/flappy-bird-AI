import pygame
import neat
import time
import os
import random
pygame.font.init()

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
STAT_FONT= pygame.font.SysFont("comicsans", 50)


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

class Pipe:
    GAP=500
    VEL=5

    def __init__(self, x):
        self.x=x
        self.height=0

        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG, False, True) # pipes at top are inverted
        self.PIPE_BOTTOM=PIPE_IMG

        self.passed=False
        self.set_height()

    def set_height(self):
        self.height=random.randrange(50, 450)
        # what we are doing here is that the pipe at top is inverted so it will come 
        # all the way down
        self.top=self.height-self.PIPE_TOP.get_height()
        self.bottom=self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask=bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset=(self.x-bird.x, self.top-round(bird.y))
        bottom_offset=(self.x - bird.x, self.bottom-round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    VEL=5
    WIDTH=BASE_IMG.get_width()
    IMG=BASE_IMG

    def __init__(self, y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH

    # we use two base img (x1, x2). Both will travel towards left with equal velocity, once first img reaches end of screen
    # it will be moved behind the second img. Second img will then travel towards end and then gets placed behnd first img.
    # This will create infinite loop
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text=STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOWS_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

    
def main():
    bird=Bird(230,350)
    base=Base(730)
    pipes=[Pipe(600)]
    win=pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
    clock=pygame.time.Clock() # setting clock

    score=0

    run=True
    while run:
        clock.tick(30) #so that when game is launched, bird doesnt fall rapidly but takes a little bit time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
        
        #bird.move()
        add_pipe=False
        remove=[]
        for pipe in pipes:
            if pipe.collide(bird):
                pass

            if pipe.x+pipe.PIPE_TOP.get_width()<0:
                remove.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                 pipe.passed = True
                 add_pipe=True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in remove:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass

        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()


if __name__ == "__main__":
    main()