from util import *
from config import *
import pygame


class Projectile(GameObject):
    CENTRAL_SHIFT_X = -8
    CENTRAL_SHIFT_Y = -15
    SPEED = 8

    def __init__(self, x, y, vx, vy, power):
        super().__init__()

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.power = power

        self.sprite = {
            (0, -1): ATLAS().image_at(40, 12, 1, 2),
            (-1, 0): ATLAS().image_at(41, 12, 1, 2),
            (0, 1): ATLAS().image_at(42, 12, 1, 2),
            (1, 0): ATLAS().image_at(43, 12, 1, 2)
        }[(vx, vy)]

    @property
    def on_screen(self):
        return 0 < self.x < GAME_WIDTH and 0 < self.y < GAME_HEIGHT

    def render(self, screen):
        screen.blit(self.sprite, (self.x + self.CENTRAL_SHIFT_X,
                                  self.y + self.CENTRAL_SHIFT_Y))
        self.x += self.vx * self.SPEED
        self.y += self.vy * self.SPEED

        # p1, p2 = self.split_in_two_coords()
        # pygame.draw.circle(screen, (255, 0, 255), p1, 2)
        # pygame.draw.circle(screen, (255, 0, 255), p2, 2)

        if not self.on_screen:
            self.remove_from_parent()

    def split_in_two_coords(self):
        x, y = self.x, self.y
        distance = ATLAS().real_sprite_size // 2
        px, py = self.vy * distance, -self.vx * distance

        return (
            (x + px, y + py),
            (x - px, y - py)
        )
