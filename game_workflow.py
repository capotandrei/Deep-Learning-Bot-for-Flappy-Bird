import pygame
import os
import neat
from base import Base
from pipe import Pipe
from bird import Bird
from utils import BG_IMG, WIN_WIDTH, WIN_HEIGHT, STAT_FONT, SCORE_THRESHOLD

GEN = 0


def draw_window(win, birds, pipes, base, score):
    global GEN
    win.blit(BG_IMG, (0, 0))  # blit means draw

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    for pipe in pipes:
        pipe.draw(win)

    # score
    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(GEN - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


# eval genomes
def main(genomes, config):
    global GEN
    GEN += 1

    nets = []
    ge = []
    birds = [] # we want to have multiple birds playing in the same time

    for _, g in genomes:
        # Set up a neural network for our genome
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    flag = True
    while flag:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if you press X button
                # flag = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):  # end the game
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:  # end the game if it hits the floor
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > SCORE_THRESHOLD:
            flag = False

        base.move()
        draw_window(win, birds, pipes, base, score)


def run(config_file):
    # """
    # runs the NEAT algorithm to train a neural network to play flappy bird.
    # :param config_file: location of config file
    # :return: None
    # """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))  # give us some output to see detail statistics
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)  # (fitness function, no_generations)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
