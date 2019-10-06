import pygame
from functools import lru_cache
from util import COLOR_BLACK_KEY


class SpriteSheet:
    def __init__(self, filename, sprite_size=8, upsample=1):
        self.sprite_size = sprite_size
        self.upsample = upsample
        self.sheet = pygame.image.load(filename).convert()

    @lru_cache(maxsize=None)
    def image_at(self, x, y, w=1, h=1, colorkey=COLOR_BLACK_KEY):
        # print(f'get sprite {x}, {y}, {w}, {h}, {colorkey}')
        s = self.sprite_size
        rect = pygame.Rect(x * s, y * s, w * s, h * s)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)

        new_size = s * self.upsample

        if self.upsample != 1:
            image = pygame.transform.scale(image, (w * new_size, h * new_size))

        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    @property
    def real_sprite_size(self):
        return self.sprite_size * self.upsample
