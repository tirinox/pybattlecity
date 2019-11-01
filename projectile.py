from util import *
from config import *
import pygame


class Projectile(GameObject):
    CENTRAL_SHIFT_X = -8
    CENTRAL_SHIFT_Y = -15
    SPEED = 8

    def __init__(self, x, y, d: Direction, power=1, sender=None):
        super().__init__()

        self.sender = sender
        self.position = x, y
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
        x, y = self.position
        return 0 < x < GAME_WIDTH and 0 < y < GAME_HEIGHT

    @property
    def bounding_rect(self):
        x, y = self.position
        w, h = self.CENTRAL_SHIFT_X, self.CENTRAL_SHIFT_Y
        if self.direction in (Direction.UP, Direction.DOWN):
            w, h = h, w
        return x - w, y - h, w * 2, h * 2

    def render(self, screen: pygame.Surface):
        x, y = self.position
        screen.blit(self.sprite, (x + self.CENTRAL_SHIFT_X,
                                  y + self.CENTRAL_SHIFT_Y))
        vx, vy = self.direction.vector
        self.move(vx * self.SPEED, vy * self.SPEED)

        if DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), self.bounding_rect)
            for x, y in self.split_for_aim():
                pygame.draw.circle(screen, (0, 100, 0), (x, y), 5)

        if not self.on_screen:
            self.remove_from_parent()

    def split_for_aim(self):
        x, y = self.position
        distance = int(ATLAS().real_sprite_size / 1.4)
        vx, vy = self.direction.vector
        px, py = (vy * distance), (-vx * distance)

        return (
            (x, y),
            (x + px, y + py),
            (x - px, y - py)
        )
