import neat.config
import pygame
import neat
import time
import os
import random
pygame.font.init()

pygame.init()

WINDOWS_WIDTH=500
WINDOWS_HEIGHT=800
GEN=0

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
    GAP = 200  # Reduce gap for better challenge
    VEL = 5
    Y_VEL = 2  # Speed for up-down movement

    def __init__(self, x):
        self.x=x
        self.height=0

        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG, False, True) # pipes at top are inverted
        self.PIPE_BOTTOM=PIPE_IMG

        self.passed=False
        self.set_height()
        self.direction = 1  # 1 for moving down, -1 for moving up

    def set_height(self):
        self.height=random.randrange(150, 450)
        # what we are doing here is that the pipe at top is inverted so it will come 
        # all the way down
        self.top=self.height-self.PIPE_TOP.get_height()
        self.bottom=self.height + self.GAP

    def move(self):
        self.x -= self.VEL

        # Make pipes move up and down
        if self.height <= 150:
            self.direction = 1  # Move down if too high
        elif self.height >= 400:
            self.direction = -1  # Move up if too low

        self.height += self.Y_VEL * self.direction  # Move pipe up or down
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

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
    # it will be moved behind the second img. Second img will then travel towards end and then gets placed behind first img.
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

def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text=STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOWS_WIDTH - 10 - text.get_width(), 10))

    text=STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10,10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

# since all the data is here, this main func will become our fitness function as well which is being passed in the winner func    
def main(genomes, config):
    # to keep track of neural networks for birds, each position(nets, ge, birds) will correspond to same bird
    global GEN
    GEN += 1
    nets=[]
    ge=[]
    birds=[]

    # creating neural network
    for _, g in genomes:
        net=neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(g)
        g.fitness=0


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
                pygame.quit()
                
        
        # if bird passes first pipe then convert it to second pipe
        pipe_ind = 0
        if len(birds)>0:
            if len(birds) == 0:
                run = False
                break

        
        # to not allow bird to fly all the way up or down, just enough to make it survive
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1        

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
           
            # output neuron is list
            if output[0]>0.5:
                bird.jump()

        add_pipe=False
        remove=[]
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird): # every pipe collides with every bird
                    ge[x].fitness -= 1
                    # if birds collide they will be popped from the list
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < birds[0].x: #if birds have passed pipe
                    pipe.passed = True
                    add_pipe=True

            if pipe.x+pipe.PIPE_TOP.get_width()<0:
                remove.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            #incrementing fitness for birds that passed a pipe without colliding
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
             if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)

def run(config_path): # define all the different sub-headings we used in config file
    config=neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                              config_path)

    p=neat.Population(config) # setting population

    p.add_reporter(neat.StdOutReporter(True)) # results for statistics for the population
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)

    winner= p.run(main, 50)

if __name__ == "__main__":
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)