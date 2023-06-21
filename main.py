import pygame as pg
from creature import Sprinter
from constants import *
from enviroment import Food, Parasite
import neat
import os
import math
from numpy.random import random
import pickle

screen = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
clock = pg.time.Clock()

generation = 0
debug = True
show_info = True


def label(text: str, position) -> None:
    screen.blit(FONT.render(str(text), 1, (0, 0, 0)), position)


def distance(a, b):
    return math.hypot((a.position.x - b.position.x), (a.position.y - b.position.y))


def sprite_collision(sprite1, sprite2, dt, repel_strengh=10):
    if pg.sprite.collide_rect(sprite1, sprite2):
        overlap_x = (sprite1.rect.width + sprite2.rect.width) / 2 - abs(
            sprite1.rect.centerx - sprite2.rect.centerx
        )
        overlap_y = (sprite1.rect.height + sprite2.rect.height) / 2 - abs(
            sprite1.rect.centery - sprite2.rect.centery
        )

        if overlap_x > overlap_y:
            if sprite1.rect.centerx < sprite2.rect.centerx:
                sprite1.position.x -= overlap_x * dt * repel_strengh
            else:
                sprite1.position.x += overlap_x * dt * repel_strengh
        else:
            if sprite1.rect.centery < sprite2.rect.centery:
                sprite1.position.y -= overlap_y * dt * repel_strengh
            else:
                sprite1.position.y += overlap_y * dt * repel_strengh


def eval_genomes(genomes, config):
    global screen, generation, creature, debug, show_info, genome_path
    generation += 1
    
    

    
    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    creatures = pg.sprite.Group()
    # [creature.Sprinter(creatures) for _ in range(20)]
    foods = pg.sprite.Group()
    [
        Food(foods, 1, (random() * DISPLAY_WIDTH, random() * DISPLAY_HEIGHT))
        for _ in range(80)
    ]
    parasites = pg.sprite.Group()
    # [
    #     Parasite(parasites, 1, (random() * DISPLAY_WIDTH, random() * DISPLAY_HEIGHT))
    #     for _ in range(5)
    # ]
    ge = []

    best_genome = None
    for genome_id, genome in genomes:
        if genome.fitness and (not best_genome or genome.fitness > best_genome.fitness):
            best_genome = genome

        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        creatures.add(Sprinter(creatures))
        ge.append(genome)
    
    if best_genome:
        with open(genome_path, "wb") as f:
            pickle.dump(best_genome, f)
            f.close()

    pause = False
    food_timer = 2000
    food_last = 0
    parasite_timer = 1300
    parasite_last = 0
    execution_speed = 5
    while len(creatures) > 0:
        if len(creatures) < 16:
            execution_speed = 20
        tick = pg.time.get_ticks()
        dt = clock.tick() / 1000
        dt *= execution_speed
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    pause = True
                elif event.key == pg.K_F1:
                    debug = not debug
                elif event.key == pg.K_F2:
                    show_info = not show_info
                elif event.key == pg.K_ESCAPE:
                    for creature in creatures.sprites():
                        creature.kill()
                elif event.key == pg.K_UP:
                    execution_speed += 1
                elif event.key == pg.K_DOWN:
                    execution_speed -= 1
            elif event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    pause = False
            

        screen.fill((220, 220, 220))

        if tick > food_last + (food_timer/execution_speed):
            Food(foods, 1, (random() * DISPLAY_WIDTH, random() * DISPLAY_HEIGHT))
            food_last = tick
        # if tick > parasite_last + (parasite_timer/execution_speed):
        #     Parasite(parasites, 1, (random() * DISPLAY_WIDTH, random() * DISPLAY_HEIGHT))
        #     parasite_last = tick
          
        
        for idx, creature in enumerate(creatures):
            closest = (math.inf, None)
            if not pause:
                creature.update(dt)

            for creature2 in creatures:
                if creature != creature2:
                    dist = distance(creature, creature2)
                    if dist < closest[0]:
                        closest = (dist, creature2)
                    sprite_collision(creature, creature2, dt)
            if closest[1] and debug:
                pg.draw.line(
                    screen, (255, 0, 255), creature.position.xy, closest[1].position.xy
                )

            if len(foods) > 0:
                closest_food = (math.inf, None)
                for food in foods.sprites():
                    food.draw(screen)
                    dist = distance(creature, food)
                    if dist < closest_food[0]:
                        closest_food = (dist, food)
                        

                    creatures_to_eat = pg.sprite.spritecollide(food, creatures, False)
                    if creatures_to_eat:
                        for to_eat in creatures_to_eat:
                            to_eat.eat(food.size * 10)
                            ge[creatures.sprites().index(to_eat)].fitness += 5
                        food.kill()
                closest_food_angle = 0
                closest_food_angle = math.atan2(
                    closest_food[1].position.y - creature.position.y,
                    closest_food[1].position.x - creature.position.x,
                ) * 180/math.pi
                if debug:
                    pg.draw.line(
                        screen,
                        (0, 255, 0),
                        creature.position.xy,
                        closest_food[1].rect.center,
                    )

            if len(parasites) > 0:
                closest_parasite = (math.inf, None)
                for parasite in parasites.sprites():
                    parasite.draw(screen)
                    dist = distance(creature, parasite)
                    if dist < closest_parasite[0]:
                        closest_parasite = (dist, parasite)
                    creatures_to_eat = pg.sprite.spritecollide(parasite, creatures, False)
                    if creatures_to_eat:
                        for to_eat in creatures_to_eat:
                            to_eat.eat(-parasite.size * 10)
                            ge[creatures.sprites().index(to_eat)].fitness -= 5
                        parasite.kill()
                  
                closest_parasite_angle = math.atan2(
                    closest_parasite[1].position.x - creature.position.x,
                    closest_parasite[1].position.y - creature.position.y,
                ) * 180 / math.pi
                if debug:
                    pg.draw.line(
                        screen,
                        (255,0,0),
                        creature.position.xy,
                        closest_parasite[1].rect.center
                    )
            creature.draw(screen, debug)

            if creature.position.x > DISPLAY_WIDTH + DISPLAY_MARGIN:
                creature.position.x = 0 - DISPLAY_MARGIN
            elif creature.position.x < 0 - DISPLAY_MARGIN:
                creature.position.x = DISPLAY_WIDTH + DISPLAY_MARGIN

            if creature.position.y > DISPLAY_HEIGHT + DISPLAY_MARGIN:
                creature.position.y = 0 - DISPLAY_MARGIN
            elif creature.position.y < 0 - DISPLAY_MARGIN:
                creature.position.y = DISPLAY_HEIGHT + DISPLAY_MARGIN

            ge[idx].fitness += 0.1 * dt
            if closest[1]:
                closest_creature_angle = math.atan2(
                    closest[1].position.y - creature.position.y,
                    closest[1].position.x - creature.position.x,
                )* 180/math.pi
            else:
                closest_creature_angle = 0

            output = nets[idx].activate(
                (
                    creature.energy,
                    creature.angle,
                    closest_creature_angle,
                    closest[0],  # distance
                    closest_food_angle,
                    closest_food[0],
                    # closest_parasite_angle,
                    # closest_parasite[0],
                )
            )

            sprint = False
            if output[1] > 0:  # sprint
                sprint = True

            if output[0] > 0:  # go forward
                creature.move_forward(dt, sprint)

            if output[2] > 0:
                creature.rotate(abs(output[2]) % 360)
            elif output[2] < 0:
                creature.rotate(abs(output[2]) % -360)

            # if output[3] > 0:
            #     creature.have_child()
            #     ge[creatures.sprites().index(creature)].fitness += 10




        if show_info:
            label(f"fps:         {round(clock.get_fps(),3)}", (10, 10))
            label(f"generation:  {str(generation).rjust(3, '0')}", (10, 28))
            label(f"count:       {str(len(creatures)).rjust(3, '0')}", (10, 46))
            label(f"exe speeed:  {str(execution_speed).rjust(2)}", (10, 64))
            if len(creatures) > 0:
                label(
                      f"[0] energy:  {round(creatures.sprites()[0].energy, 2)}", (10, 82)
                )
                label(f"[0] x, y:    {str(round(creatures.sprites()[0].position.x, 1)).rjust(4)}, {str(round(creatures.sprites()[0].position.y, 1)).rjust(4)}", (10, 100))
                label(f"[0] fitness: {round(ge[creatures.sprites().index(creature)].fitness, 3)}", (10, 118))
            


        for idx, creature in enumerate(creatures):
            if creature.dead:
                ge[creatures.sprites().index(creature)].fitness -= 1
                nets.pop(creatures.sprites().index(creature))
                ge.pop(creatures.sprites().index(creature))
                creatures.remove(creature)


        pg.display.flip()


def run(config_path, genome_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    best_genome = None
    if os.path.exists(genome_path):
        with open(genome_path, "rb") as f:
            best_genome = pickle.load(f)
            f.close()
    p.best_genome = best_genome

    winner = p.run(eval_genomes, 50000)

    with open(genome_path, "wb") as f:
        pickle.dump(winner, f)
        f.close()

    print(f"\nBest genome:\n{winner}")


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    genome_path = os.path.join(local_dir, "winner.pkl")
    run(config_path, genome_path)
