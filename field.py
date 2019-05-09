import pygame
from spritesheet import SpriteSheet


class Field:
    def __init__(self, atlas: SpriteSheet, w=14, h=14):
        self.atlas = atlas
        self.w = w
        self.h = h

        # self.t1 = atlas.image_at(8, 8, 2, 2)



    def render(self, screen):

        # screen.blit(self.t1, (20, 20))
        ...
