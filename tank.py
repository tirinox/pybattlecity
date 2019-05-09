import pygame
from spritesheet import SpriteSheet


class Tank:
    class Color:
        YELLOW = (0, 0)
        GREEN = (0, 16)
        PURPLE = (16, 16)
        PLAIN = (16, 0)

    class Type:
        LEVEL_1 = 0
        LEVEL_2 = 2
        LEVEL_3 = 4
        LEVEL_4 = 6
        ENEMY_SIMPLE = 8
        ENEMY_FAST = 10
        ENEMY_MIDDLE = 12
        ENEMY_HEAVE = 14

    class Direction:
        UP = 0
        LEFT = 4
        DOWN = 8
        RIGHT = 12
        ALL = UP, LEFT, DOWN, RIGHT

    MOVE_FRAMES = 2

    def get_sprite(self, color, type, direction, state):
        x = color[0] + direction + state
        y = color[1] + type
        return self.atlas.image_at(x, y, 2, 2)

    def __init__(self, atlas: SpriteSheet, color=Color.YELLOW, tank_type=Type.LEVEL_1):
        self.atlas = atlas
        self.direction = self.Direction.UP
        self.color = color
        self.type = tank_type
        self.moving = True
        self.move_step = 0
        self.cnt = 0
        self.x = 0
        self.y = 0
        self.sprites = {(d, s): self.get_sprite(color, tank_type, d, s)
                        for d in self.Direction.ALL
                        for s in (0, 2)}

    def render(self, screen):
        sprite = self.sprites[(self.direction, self.move_step * 2)]
        ey = 4 if self.type >= self.Type.ENEMY_SIMPLE and self.direction == self.Direction.RIGHT else 0
        screen.blit(sprite, (self.x, self.y + ey))

        if self.moving:
            self.cnt += 1
            if self.cnt >= self.MOVE_FRAMES:
                self.cnt = 0
                self.move_step = 1 - self.move_step
