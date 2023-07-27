import pygame
import neat
import os
import random

pygame.font.init()


# Constants
WIN_HEIGHT = 800
WIN_WIDTH = 500
DRAW_LINES = True
GEN = 0

pygame.display.set_caption('Flappy Bird')


# Importing game textures
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load('imgs\\bird1.png')),
             pygame.transform.scale2x(pygame.image.load('imgs\\bird2.png')),
             pygame.transform.scale2x(pygame.image.load('imgs\\bird3.png')),
             ]
BASE_IMG = pygame.transform.scale2x(pygame.image.load('imgs\\base.png'))
BG_IMG = pygame.transform.scale2x(pygame.image.load('imgs\\bg1.png'))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load('imgs\\pipe.png'))


# Declaring font
STAT_FONT = pygame.font.SysFont('comicsans', 50)


# Class Bird
class Bird:
    ROTATION_VEL = 20
    MAX_ROTATION = 25
    ANIMATION_TIME = 5
    IMGS = BIRD_IMGS

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = self.y
        self.frame_count = 0
        self.tilt = 0
        self.vel = 0
        self.img_number = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 # negative velocity refers to jump upwards
        self.frame_count = 0 # reset frames
        self.height = self.y # reset height

    def move(self):
        self.frame_count += 1 # update frames when bird moves
        d = self.vel * self.frame_count + 1.5 * self.frame_count ** 2
        
        if d >= 16:
            d = 16
        if d< 0:
            d -=2 

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VEL

    def draw(self, win):
        self.img_number += 1

        if self.img_number < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_number < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_number < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_number < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_number < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_number = 0

        if self.tilt < -80:
            self.img = self.IMGS[1]
            self.img_number = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center= self.img.get_rect(topleft= (self.x, self.y)).center)
        win.blit(rotated_image, new_rect)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.BOTTOM_PIPE = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self): # randomly selects height for pipes
        self.height = random.randrange(50, 450)
        self.bottom = self.height + self.GAP
        self.top = self.height - self.TOP_PIPE.get_height()

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom))

    def collide(self, bird): # for checking collusion of the bird with the pipes
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_pipe_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        top_overlap = bird_mask.overlap(top_pipe_mask, top_offset)
        bottom_overlap = bird_mask.overlap(bottom_pipe_mask, bottom_offset)

        if top_overlap or bottom_overlap:
            return True
        return False
    

# Base class for displaying base
class Base:
    VEL = 5
    IMG = BASE_IMG
    WIDTH = BASE_IMG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 < -self.WIDTH:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 < -(self.WIDTH):
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# Main drawing function
def draw_window(win, birds, pipes, base, score, GEN, pipe_ind):
    global DRAW_LINES
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)

    for bird in birds:
        # draw lines from bird to pipes
        if DRAW_LINES == True:
            try:
                pygame.draw.lines(win, (255, 0 ,0),
                                  (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                  (pipes[pipe_ind].x + pipes[pipe_ind].TOP_PIPE.get_width() / 2, pipes[pipe_ind].height),
                                  5)
            except:
                pass

        bird.draw(win)
    
    text = STAT_FONT.render('Score : ' + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render('Gen : ' + str(GEN), 1, (255,255,255))
    win.blit(text, (10, 10))

    text = STAT_FONT.render('ALive : ' + str(len(birds)), 1, (255,255,255))
    win.blit(text, (10, 50))

    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    birds = []
    ge = []
    neural_network = []

    # Create new birds and neural networks everytime new generation comes
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config= config)
        neural_network.append(net)
        birds.append(Bird(230 ,350))
        g.fitness = 0
        ge.append(g)

    pipes = [Pipe(500)] # list of pipe objects
    base_object = Base(630)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0

    while run: # main running loop
        clock.tick(60) # fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():
                pipe_ind = 1
        
        else: # if all the birds are dead then exit the loop
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = neural_network[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        for pipe in pipes:
            for x, bird in enumerate(birds):
                # checking if the bird hit the ground, pipe, or the top boundary
                if pipe.collide(bird) or (bird.y + bird.img.get_height() >= 630 or bird.y < 0):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    ge.pop(x)
                    neural_network.pop(x)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    for g in ge:
                        g.fitness += 5
                    score += 1
                    pipes.append(Pipe(500))

            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                pipes.remove(pipe)
                
            pipe.move()
        base_object.move()
        draw_window(win, birds, pipes, base_object, score, GEN, pipe_ind)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 1200)
    print('\nBest genome:\n{!s}'.format(winner))




if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)