from util import *
from config import *
import pygame


class Projectile(GameObject):
    CENTRAL_SHIFT_X = -8
    CENTRAL_SHIFT_Y = -15
    SPEED = 8

    SHIFT_BACK = -2

    POWER_NORMAL = 1
    POWER_HIGH = 2

    def __init__(self, x, y, d: Direction, power=POWER_NORMAL, sender=None):
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
        w, h = abs(self.CENTRAL_SHIFT_X), abs(self.CENTRAL_SHIFT_Y)
        if self.direction in (Direction.UP, Direction.DOWN):
            w, h = h, w
        return x - w, y - h, w * 2, h * 2

    def render(self, screen: pygame.Surface):
        x, y = self.position
        sbx, sby = self.direction.vector
        sbx *= self.SHIFT_BACK
        sby *= self.SHIFT_BACK
        screen.blit(self.sprite, (x + self.CENTRAL_SHIFT_X - sbx,
                                  y + self.CENTRAL_SHIFT_Y - sby))

        if PROJECTILE_DEBUG:
            # pygame.draw.rect(screen, (255, 0, 0), self.bounding_rect)
            # for x, y in self.split_for_aim():
            #     pygame.draw.circle(screen, (0, 100, 0), (x, y), 5)
            pygame.draw.circle(screen, (0, 200, 0), (x, y), 4)

        if not self.on_screen:
            self.remove_from_parent()

    def update(self):
        vx, vy = self.direction.vector
        self.move(vx * self.SPEED, vy * self.SPEED)

    def split_for_aim(self):
        """разбивает снаряд на 3 виртуальных для равномерности разрушения"""
        x, y = self.position
        distance = int(ATLAS().real_sprite_size / 1.4)
        vx, vy = self.direction.vector
        px, py = (vy * distance), (-vx * distance)

        return (
            (x, y),
            (x + px, y + py),
            (x - px, y - py)
        )

    def __hash__(self):
        return id(self)
