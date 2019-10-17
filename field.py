from util import GameObject, Direction, rect_intersection
from config import ATLAS
from enum import Enum, auto
import pygame
from math import floor
from projectile import Projectile


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

        @property
        def is_half_brick(self):
            return self.brick and self != self.BRICK

        @classmethod
        def from_symbol(cls, s):
            return {
                '_': cls.FREE,
                'B': cls.BRICK,
                'C': cls.CONCRETE,
                'S': cls.SKATE,
                'G': cls.GREEN,
                'l': cls.BRICK_LEFT,
                't': cls.BRICK_TOP,
                'b': cls.BRICK_BOTTOM,
                'r': cls.BRICK_RIGHT
            }[s]

        def calculate_rect(self, x, y, step):
            half = step // 2
            if self == self.BRICK_RIGHT:
                return x + half, y, half, step
            elif self == self.BRICK_LEFT:
                return x, y, half, step
            elif self == self.BRICK_BOTTOM:
                return x, y + half, step, half
            elif self == self.BRICK_TOP:
                return x, y, step, half
            else:
                return x, y, step, step

    HEIGHT = WIDTH = 13 * 2  # 13 full blocks by (2x2) cells each
    BACKGROUND_COLOR = (0, 0, 0)

    def __init__(self):
        super().__init__()

        self.origin = (40, 40)
        self._step = ATLAS().real_sprite_size

        # addressing: self.cells[x or column][y or row]
        self._cells = [
            [Field.CellType.FREE for _ in range(self.HEIGHT)]
            for _ in range(self.WIDTH)
        ]

        self._sprites = {
            t: ATLAS().image_at(*t.sprite_location, 1, 1, colorkey=None) for t in Field.CellType
        }

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        assert len(lines) >= self.HEIGHT, "incomplete level"
        for _, (y, line) in zip(range(self.HEIGHT), enumerate(lines)):
            assert len(line) >= self.WIDTH, "incomplete line"
            for _, (x, symbol) in zip(range(self.WIDTH), enumerate(line)):
                self._cells[x][y] = self.CellType.from_symbol(symbol)
                print(symbol, end='')
            print()

    def coord_by_col_and_row(self, col, row):
        xs, ys = self.origin
        x = xs + col * self._step
        y = ys + row * self._step
        return x, y

    def col_row_from_coords(self, x, y):
        xs, ys = self.origin
        col = floor((x - xs) / self._step)
        row = floor((y - ys) / self._step)
        return col, row

    def inside_field_col_row(self, col, row):
        return 0 <= col < self.WIDTH and 0 <= row < self.HEIGHT

    def cell_by_coords(self, x, y):
        col, row = self.col_row_from_coords(x, y)
        if self.inside_field_col_row(col, row):
            return self._cells[col][row]
        else:
            return self.CellType.CONCRETE

    def set_cell_by_coord(self, x, y, cell: CellType):
        col, row = self.col_row_from_coords(x, y)
        if self.inside_field_col_row(col, row):
            self._cells[col][row] = cell

    @property
    def rect(self):
        return [*self.origin, self._step * self.WIDTH, self._step * self.HEIGHT]

    def point_in_field(self, x, y):
        fx, fy, fw, fh = self.rect
        return fx <= x <= fx + fw and fy <= y <= fy + fh

    def render(self, screen):
        pygame.draw.rect(screen, self.BACKGROUND_COLOR, self.rect)

        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                cell = self._cells[col][row]
                if cell != cell.FREE:
                    coords = self.coord_by_col_and_row(col, row)
                    screen.blit(self._sprites[cell], coords)

    def intersect_rect(self, test_rect):
        x1, y1, w, h = test_rect
        x2 = x1 + w
        y2 = y1 + h

        check_pts = (
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2)
        )

        rmax = cmax = -1
        rmin, cmin = self.HEIGHT, self.WIDTH

        for x, y in check_pts:
            col, row = self.col_row_from_coords(x, y)
            rmax = max(rmax, row)
            rmin = min(rmin, row)
            cmax = max(cmax, col)
            cmin = min(cmin, col)

        for c in range(cmin, cmax + 1):
            for r in range(rmin, rmax + 1):
                if not self.inside_field_col_row(c, r):
                    return True

                cell = self._cells[c][r]

                if not cell.can_tank_run_here:
                    x, y = self.coord_by_col_and_row(c, r)
                    abs_cell_rect = cell.calculate_rect(x, y, self._step)
                    if rect_intersection(test_rect, abs_cell_rect):
                        return True

        return False


    def get_center_of_cell(self, col, row):
        xs, ys = self.origin
        return xs + col * self._step, ys + row * self._step

    def _check_hit(self, x, y, d: Direction):
        cell = self.cell_by_coords(x, y)
        if cell.solid:
            if cell == cell.BRICK:
                self.set_cell_by_coord(x, y, {
                    Direction.LEFT: cell.BRICK_LEFT,
                    Direction.RIGHT: cell.BRICK_RIGHT,
                    Direction.UP: cell.BRICK_TOP,
                    Direction.DOWN: cell.BRICK_BOTTOM
                }[d])
            elif cell.is_half_brick:
                self.set_cell_by_coord(x, y, cell.FREE)
            return True
        return False

    def check_hit(self, p: Projectile):
        p_group = p.split_for_aim()
        # can't put it just into "any" because "any" is curcuit-cut operation,
        # though we need for all "_check_hit" to be run!
        p_results = [self._check_hit(x, y, p.direction) for x, y in p_group]
        return any(p_results)

