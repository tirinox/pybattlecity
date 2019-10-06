from spritesheet import SpriteSheet
from enum import Enum
from util import GameObject


class Tank(GameObject):
    class Color(Enum):
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

    MOVE_FRAMES = 2

    def get_sprite(self, color: Color, type: Type, direction: Direction, state):
        x = color.value[0] + direction.value + state
        y = color.value[1] + type.value
        return self.atlas.image_at(x, y, 2, 2)

    def __init__(self, atlas: SpriteSheet, color=Color.YELLOW, tank_type=Type.LEVEL_1):
        super().__init__()
        self.atlas = atlas
        self.direction = self.Direction.UP
        self.color = color
        self.tank_type = tank_type
        self.moving = False
        self.move_step = 0
        self.cnt = 0
        self.x = 0
        self.y = 0
        self.sprites = {(d, s): self.get_sprite(color, tank_type, d, s)
                        for d in self.Direction
                        for s in (0, 2)}

    def render(self, screen):
        sprite = self.sprites[(self.direction, self.move_step * 2)]

        # sprites for some tank types are not aligned wall, so we add ex and ey
        # so movement is smooth without jumps when you change the direction to the opposite one
        if self.direction in (self.Direction.LEFT, self.Direction.RIGHT):
            ex, ey = 0, 2
        else:
            ex, ey = 2, 0

        if self.tank_type in (self.Type.ENEMY_MIDDLE, self.Type.ENEMY_FAST, self.Type.ENEMY_SIMPLE):
            if self.direction == self.Direction.LEFT:
                ey -= 2

        if self.tank_type == self.Type.ENEMY_MIDDLE:
            if self.direction == self.Direction.DOWN:
                ex += 2

        screen.blit(sprite, (self.x + ex,
                             self.y + ey))

        # animate sprite when moving
        if self.moving:
            self.cnt += 1
            if self.cnt >= self.MOVE_FRAMES:
                self.cnt = 0
                self.move_step = 1 - self.move_step

    def gun_point(self):
        """
        Calculate the coordinates of the gun of the tank
        :return: (x, y) coordinates of gun tip point
        """
        x, y = self.x, self.y
        w = h = 2 * self.atlas.upsample * self.atlas.sprite_size
        xs = x + w // 2
        ys = y + h // 2
        shift = 2

        d = self.direction
        if d == self.Direction.UP:
            return xs, y - shift
        elif d == self.Direction.DOWN:
            return xs, y + h + shift
        elif d == self.Direction.LEFT:
            return x - shift, ys
        elif d == self.Direction.RIGHT:
            return x + w + shift, ys

    def center_point(self):
        x, y = self.x, self.y
        w = h = 2 * self.atlas.upsample * self.atlas.sprite_size
        xs = x + w // 2
        ys = y + h // 2
        return xs, ys