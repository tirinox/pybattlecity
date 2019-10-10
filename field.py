from util import GameObject
from config import ATLAS
from enum import Enum, auto
import pygame
from math import floor
from projectile import Projectile
from explosion import Explosion


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
            return self in (
                self.FREE,
                self.SKATE,
                self.GREEN
            )

        @property
        def solid(self):
            return self in (
                self.BRICK,
                self.BRICK_TOP,
                self.BRICK_LEFT,
                self.BRICK_BOTTOM,
                self.BRICK_RIGHT,
                self.CONCRETE
            )

        @property
        def brick(self):
            return self in (
                self.BRICK,
                self.BRICK_TOP,
                self.BRICK_BOTTOM,
                self.BRICK_LEFT,
                self.BRICK_RIGHT
            )

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

    def __init__(self):
        super().__init__()

        self.origin = (40, 40)
        self.step = ATLAS().real_sprite_size

        # addressing: self.cells[x or column][y or row]
        self.cells = [
            [Field.CellType.FREE for _ in range(self.HEIGHT)]
            for _ in range(self.WIDTH)
        ]

        self.sprites = {
            t: ATLAS().image_at(*t.sprite_location, 1, 1, colorkey=None) for t in Field.CellType
        }

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        assert len(lines) >= self.HEIGHT, "incomplete level"
        for _, (y, line) in zip(range(self.HEIGHT), enumerate(lines)):
            assert len(line) >= self.WIDTH, "incomplete line"
            for _, (x, symbol) in zip(range(self.WIDTH), enumerate(line)):
                self.cells[x][y] = self.CellType.from_symbol(symbol)
                print(symbol, end='')
            print()

    def coord_by_col_and_row(self, col, row):
        xs, ys = self.origin
        x = xs + col * self.step
        y = ys + row * self.step
        return x, y

    def col_row_from_coords(self, x, y):
        xs, ys = self.origin
        col = floor((x - xs) / self.step)
        row = floor((y - ys) / self.step)
        return col, row

    def cell_by_coords(self, x, y):
        col, row = self.col_row_from_coords(x, y)
        if 0 <= col < self.WIDTH and 0 <= row < self.HEIGHT:
            return self.cells[col][row]
        else:
            return self.CellType.CONCRETE

    def set_cell_by_coord(self, x, y, cell: CellType):
        col, row = self.col_row_from_coords(x, y)
        if 0 <= col < self.WIDTH and 0 <= row < self.HEIGHT:
            self.cells[col][row] = cell

    @property
    def rect(self):
        return [*self.origin, self.step * self.WIDTH, self.step * self.HEIGHT]

    def point_in_field(self, x, y):
        fx, fy, fw, fh = self.rect
        return fx <= x <= fx + fw and fy <= y <= fy + fh

    def render(self, screen):
        pygame.draw.rect(screen, self.BACKGROUND_COLOR, self.rect)

        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                cell = self.cells[col][row]
                if cell != cell.FREE:
                    coords = self.coord_by_col_and_row(col, row)
                    screen.blit(self.sprites[cell], coords)

    def intersect_rect(self, rect):
        x1, y1, w, h = rect
        x2 = x1 + w - 1
        y2 = y1 + h - 1
        xc = x1 + w // 2
        yc = y1 + h // 2
        check_pts = (
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2),
            (xc, y1),
            (xc, y2),
            (x1, yc),
            (x2, yc)
        )
        return any(not self.cell_by_coords(*coords).can_tank_run_here for coords in check_pts)

    def get_center_of_cell(self, col, row):
        xs, ys = self.origin
        return xs + col * self.step, ys + row * self.step

    def _check_hit(self, x, y):
        cell = self.cell_by_coords(x, y)
        if cell.solid:
            if cell == cell.BRICK:
                self.set_cell_by_coord(x, y, cell.FREE)
            return True
        return False

    def check_hit(self, p: Projectile):
        (x1, y1), (x2, y2) = p.split_in_two_coords()
        r1 = self._check_hit(x1, y1)
        r2 = self._check_hit(x2, y2)
        if r1 or r2:
            p.remove_from_parent()
            expl = Explosion(p.x, p.y, short=True)
            self.add_child(expl)
