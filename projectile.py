from util import *
from config import *
from spritesheet import SpriteSheet


class Projectile(GameObject):
    CENTRAL_SHIFT_X = -8
    CENTRAL_SHIFT_Y = -14
    SPEED = 8

    def __init__(self, atlas: SpriteSheet, x, y, vx, vy, power):
        super().__init__()

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.power = power

        self.sprite = {
            (0, -1): atlas.image_at(40, 12, 1, 2),
            (-1, 0): atlas.image_at(41, 12, 1, 2),
            (0, 1): atlas.image_at(42, 12, 1, 2),
            (1, 0): atlas.image_at(43, 12, 1, 2)
        }[(vx, vy)]

    def render(self, screen):
        screen.blit(self.sprite, (self.x + self.CENTRAL_SHIFT_X,
                                  self.y + self.CENTRAL_SHIFT_Y))
        self.x += self.vx * self.SPEED
        self.y += self.vy * self.SPEED

        if not (0 < self.x < GAME_WIDTH and 0 < self.y < GAME_HEIGHT):
            self.remove_from_parent()

