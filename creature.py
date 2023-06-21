import pygame as pg
import numpy as np
import os
from constants import *
import math


class Creature(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.energy_max = 150
        self.energy = 100
        self.fatigue = 0.5

        self.health_max = 100
        self.health_curr = self.health_max
        self.armor = 10
        self.type = None

        self.strength = 10


        self.asexual = False

        self.fitness = 0
        self.speed = 20
        self.size = 1
        self.dead = False

        self.imgs = list()
        self.img = None  # current image
        self.position = pg.math.Vector2(
            np.random.random() * 700 + 50, np.random.random() * 500 + 50
        )

        self.animation_tick = 200
        self.animation_last = 0
        self.animation_frame = 0
        self.rect = pg.Rect(self.position.xy, (16,16))

        self.angle = 0

    def setup(self):
        self.animation_tick -= self.speed*2

    def kill(self):
        self.dead = True


    def update(self, dt):
        if self.dead:
            return
        self.rect.center = self.position.xy
        if pg.time.get_ticks() > self.animation_last + self.animation_tick:
            self.animation_frame += 1
            self.animation_last = pg.time.get_ticks()
            self.img = pg.transform.scale_by(
                self.imgs[self.animation_frame % len(self.imgs)], self.size
            )

        if self.energy <= 0:
            self.kill()
        self.energy -= self.fatigue * dt

    def draw(self, screen, debug=False):
        img = pg.transform.rotate(self.img, self.angle - 90)
        screen.blit(
            img,
            (
                self.position.x - img.get_width() / 2,
                self.position.y - img.get_height() / 2,
            ),
        )
        if debug:
            pg.draw.rect(screen, (0,0,255), self.rect, 1)

    def move_forward(self, dt, sprint=0):
        if sprint:
            self.position += (
                pg.math.Vector2(
                    math.cos(-self.angle * math.pi / 180),
                    math.sin(-self.angle * math.pi / 180),
                )
                * self.speed * 2
                * dt
            )
            self.energy -= self.fatigue * dt * 3.5
        else:
            self.position += (
                pg.math.Vector2(
                    math.cos(-self.angle * math.pi / 180),
                    math.sin(-self.angle * math.pi / 180),
                )
                * self.speed
                * dt
            )
            self.energy -= self.fatigue * dt * 2

    def rotate(self, amount):
        self.angle += amount

    def eat(self, amount):
        self.energy += amount

        if self.energy > self.energy_max:
            self.kill()


    def have_child(self):
        if self.energy > 50:
            self.eat(-50)


class Sprinter(Creature):
    def __init__(self, group):
        super().__init__(group)
        self.fatigue *= 1.5
        self.speed *= 2
        self.size *= 1

        self.type = SPRINTER
        self.imgs = [
            pg.image.load(
                os.path.join("assets", "creatures", f"sprinter_{i}.png")
            ).convert_alpha()
            for i in range(6)
        ]
        self.img = pg.image.load(
            os.path.join("assets", "creatures", "sprinter_0.png")
        ).convert_alpha()
        self.img = pg.transform.rotozoom(self.img, 90, 1)
        self.setup()

class Heavy(Creature):
    def __init__(self, group):
        super().__init__(group)
        self.speed *= 0.8
        self.imgs = [
            pg.image.load(
                os.path.join("assets", "creatures", f"heavy_{i}.png")
            ).convert_alpha()
            for i in range(4)
        ]
        self.img = pg.image.load(
            os.path.join("assets", "creatures", "heavy_0.png")
        ).convert_alpha()
        self.img = pg.transform.rotozoom(self.img, 90, 1)
        self.setup()

