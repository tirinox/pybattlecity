from spritesheet import SpriteSheet
from enum import Enum
from util import *


class Tank(GameObject):
    class Color(Enum):
        # the value is (x, y) location on the sprite sheet in 8px blocks
        YELLOW = (0, 0)
        GREEN = (0, 16)
        PURPLE = (16, 16)
        PLAIN = (16, 0)

    class Type(Enum):
        LEVEL_1 = 0
        LEVEL_2 = 2
        LEVEL_3 = 4
        LEVEL_4 = 6
        ENEMY_SIMPLE = 8
        ENEMY_FAST = 10
        ENEMY_MIDDLE = 12
        ENEMY_HEAVY = 14

    class Direction(Enum):
        UP = 0
        LEFT = 4
        DOWN = 8
        RIGHT = 12

        @property
        def vector(self):
            return {
                self.UP: (0, -1),
                self.DOWN: (0, 1),
                self.LEFT: (-1, 0),
                self.RIGHT: (1, 0)
            }[self]

    MOVE_FRAMES = 2
    POSSIBLE_MOVE_STATES = 0, 2

    def get_sprite_location(self, color: Color, type: Type, direction: Direction, state):
        # see: atlas.png to understand this code:
        x = color.value[0] + direction.value + state
        y = color.value[1] + type.value
        return x, y, 2, 2

    def __init__(self, atlas: SpriteSheet, color=Color.YELLOW, tank_type=Type.LEVEL_1):
        super().__init__()
        self.atlas = atlas

        self.direction = self.Direction.UP
        self.color = color
        self.tank_type = tank_type

        self.x = 0
        self.y = 0

        self.moving = False
        self.cnt = 0
        self.move_state = 0

        sprite_locations = {(d, s): self.get_sprite_location(color, tank_type, d, s)
                            for d in self.Direction
                            for s in self.POSSIBLE_MOVE_STATES}

        self.sprites = {key: self.atlas.image_at(*location, auto_crop=True)
                        for key, location in sprite_locations.items()}

    def place(self, x, y):
        self.x = x
        self.y = y

    @property
    def sprite_key(self):
        return self.direction, self.move_state

    def render(self, screen):
        sprite = self.sprites[self.sprite_key]
        cx = round(sprite.get_width() / 2)
        cy = round(sprite.get_height() / 2)

        screen.blit(sprite, (self.x - cx, self.y - cy))

        # animate sprite when moving
        if self.moving:
            self.cnt += 1
            if self.cnt >= self.MOVE_FRAMES:
                self.cnt = 0
                self.move_state = 2 - self.move_state

    @property
    def gun_point(self):
        """
        Calculate the coordinates of the gun of the tank
        :return: (x, y) coordinates of gun tip point
        """
        x, y = self.x, self.y
        _, _, w, h = self.bounding_rect
        half_w, half_h = round(w / 2), round(h / 2)

        d = self.direction
        if d == self.Direction.UP:
            return x, y - half_h
        elif d == self.Direction.DOWN:
            return x, y + half_h
        elif d == self.Direction.LEFT:
            return x - half_w, y
        elif d == self.Direction.RIGHT:
            return x + half_w, y

    @property
    def center_point(self):
        return self.x, self.y

    @property
    def bounding_rect(self):
        sprite = self.sprites[self.sprite_key]
        w, h = sprite.get_width(), sprite.get_height()
        return self.x - round(w / 2), self.y - round(h / 2), w, h
