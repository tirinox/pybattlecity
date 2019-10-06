from util import GameObject
from spritesheet import SpriteSheet
from enum import Enum, auto
import pygame


class Field(GameObject):
    class CellType(Enum):
        FREE = auto()
        BRICK = auto()
        BRICK_RIGHT = auto()
        BRICK_BOTTOM = auto()
        BRICK_LEFT = auto()
        BRICK_TOP = auto()
        CONCRETE = auto()
        GREEN = auto()
        SKATE = auto()

        @property
        def sprite_location(self):
            return {
                self.FREE: (32, 13),
                self.BRICK: (32, 0),
                self.BRICK_RIGHT: (33, 8),
                self.BRICK_BOTTOM: (34, 8),
                self.BRICK_LEFT: (35, 8),
                self.BRICK_TOP: (36, 8),
                self.CONCRETE: (32, 2),
                self.GREEN: (34, 4),
                self.SKATE: (36, 4)
            }[self]

        @property
        def is_draw_over(self):
            return self == self.GREEN

        @property
        def can_tank_run_here(self):
            return self in [
                self.FREE,
                self.SKATE,
                self.GREEN
            ]

        @classmethod
        def from_symbol(cls, s):
            return {
                '_': cls.FREE,
                'B': cls.BRICK,
                'C': cls.CONCRETE,
                'S': cls.SKATE,
                'G': cls.GREEN,
            }[s]

    HEIGHT = WIDTH = 13 * 2  # 13 full blocks by (2x2) cells each
    BACKGROUND_COLOR = (0, 0, 0)

    def __init__(self, atlas: SpriteSheet):
        super().__init__()
        self.atlas = atlas

        # addressing: self.cells[x or column][y or row]
        self.cells = [
            [Field.CellType.FREE for _ in range(self.HEIGHT)]
            for _ in range(self.WIDTH)
        ]

        self.sprites = {
            t: self.atlas.image_at(*t.sprite_location, 1, 1, colorkey=None) for t in Field.CellType
        }

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        assert len(lines) >= self.HEIGHT, "incomplete level"
        for _, (y, line) in zip(range(self.HEIGHT), enumerate(lines)):
            assert len(line) >= self.WIDTH
            for _, (x, symbol) in zip(range(self.WIDTH), enumerate(line)):
                self.cells[x][y] = self.CellType.from_symbol(symbol)
                print(symbol, end='')
            print()

    def render(self, screen):
        step = self.atlas.sprite_size * 2
        xs, ys = 40, 40

        pygame.draw.rect(screen, self.BACKGROUND_COLOR, [xs, ys, step * self.WIDTH, step * self.HEIGHT])

        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                x = xs + col * step
                y = ys + row * step
                cell = self.cells[col][row]
                if cell != cell.FREE:
                    screen.blit(self.sprites[cell], (x, y))


