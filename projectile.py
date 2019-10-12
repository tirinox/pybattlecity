from util import *
from config import *
import pygame


class Projectile(GameObject):
    CENTRAL_SHIFT_X = -8
    CENTRAL_SHIFT_Y = -15
    SPEED = 8

    def __init__(self, x, y, d: Direction, power):
        super().__init__()

        self.x = x
        self.y = y
        self.direction = d
        self.power = power

        self.sprite = {
            (0, -1): ATLAS().image_at(40, 12, 1, 2),
            (-1, 0): ATLAS().image_at(41, 12, 1, 2),
            (0, 1): ATLAS().image_at(42, 12, 1, 2),
            (1, 0): ATLAS().image_at(43, 12, 1, 2)
        }[d.vector]

    @property
    def on_screen(self):
        return 0 < self.x < GAME_WIDTH and 0 < self.y < GAME_HEIGHT

    def render(self, screen):
        screen.blit(self.sprite, (self.x + self.CENTRAL_SHIFT_X,
                                  self.y + self.CENTRAL_SHIFT_Y))
        vx, vy = self.direction.vector
        self.x += vx * self.SPEED
        self.y += vy * self.SPEED

        if DEBUG:
            ps = self.split_for_aim()
            for p in ps:
                pygame.draw.circle(screen, (255, 0, 255), p, 2)

        if not self.on_screen:
            self.remove_from_parent()

    def split_for_aim(self):
        x, y = self.x, self.y
        distance = ATLAS().real_sprite_size // 2
        vx, vy = self.direction.vector
        px, py = (vy * distance), (-vx * distance)

        return (
            # (x - vx * distance, y - vy * distance),
            (x + px, y + py),
            (x - px, y - py)
        )
