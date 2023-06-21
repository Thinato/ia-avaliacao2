import pygame as pg
from constants import *
import os

class Food(pg.sprite.Sprite):
    def __init__(self, group, size, position):
        super().__init__(group)
        self.size = size
        self.position = pg.math.Vector2(position)
        self.rect = pg.Rect(self.position.xy, (16,16))
        self.img = pg.image.load(
            os.path.join("assets", "food.png")
        ).convert_alpha()
        

    def draw(self, screen):
        screen.blit(self.img, self.position)
    
class Parasite(pg.sprite.Sprite):
    def __init__(self, group, size, position):
        super().__init__(group)
        self.size = size
        self.position = pg.math.Vector2(position)
        self.rect = pg.Rect(self.position.xy, (16,16))
        self.img = pg.image.load(
            os.path.join("assets", "parasite.png")
        ).convert_alpha()
        

    def draw(self, screen):
        screen.blit(self.img, self.position)
    
class Egg(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.size = 1
