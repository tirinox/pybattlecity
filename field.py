from util import GameObject
from spritesheet import SpriteSheet


class Field(GameObject):

    HEIGHT = WIDTH = 13 * 4  # full blocks divisible by 4 cells

    def __init__(self, atlas: SpriteSheet, w=14, h=14):
        super().__init__()
        self.atlas = atlas
        self.w = w
        self.h = h

        # self.t1 = atlas.image_at(8, 8, 2, 2)

    def render(self, screen):

        # screen.blit(self.t1, (20, 20))
        ...
