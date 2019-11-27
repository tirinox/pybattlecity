from util import GameObject, Direction, rect_intersection, DEMO_COLORS
from config import *
from enum import Enum, auto
import pygame
from math import floor
from projectile import Projectile



class DiscreteMap:
    def __init__(self, position, cell_size, cells_width=FIELD_WIDTH, cells_height=FIELD_HEIGHT, default_value=None):
        self.width = cells_width
        self.height = cells_height
        self.position = position
        self.default_value = default_value
        self.step = cell_size
        self._cells = []
        self.clear()

    def clear(self):
        dv = self.default_value
        self._cells = [[dv] * self.height for _ in range(self.width)]

    def coord_by_col_and_row(self, col, row):
        xs, ys = self.position
        x = xs + col * self.step
        y = ys + row * self.step
        return x, y

    def col_row_from_coords(self, x, y):
        xs, ys = self.position
        col = floor((x - xs) / self.step)
        row = floor((y - ys) / self.step)
        return col, row

    def inside_col_row(self, col, row):
        return 0 <= col < self.width and 0 <= row < self.height

    # addressing: self.cells[x or column][y or row]
    def get_cell_by_col_row(self, col, row):
        if self.inside_col_row(col, row):
            return self._cells[col][row]
        else:
            return None

    def get_cell_by_coords(self, x, y):
        return self.get_cell_by_col_row(*self.col_row_from_coords(x, y))

    def set_cell_col_row(self, col, row, cell):
        if self.inside_col_row(col, row):
            self._cells[col][row] = cell

    def set_cell_by_coord(self, x, y, cell):
        self.set_cell_col_row(*self.col_row_from_coords(x, y), cell)

    def render(self, screen):
        step = self.step
        for col in range(self.width):
            for row in range(self.height):
                occupied = self.get_cell_by_col_row(col, row)
                if occupied is not None:
                    x, y = self.coord_by_col_and_row(col, row)
                    color = DEMO_COLORS[id(occupied) % len(DEMO_COLORS)]
                    pygame.draw.rect(screen, color, (x, y, step, step))


class OccupancyMap(DiscreteMap):
    def find_col_row_of_rect(self, r):
        x, y, w, h = r
        assert w >= 0 and h >= 0

        c1, r1 = self.col_row_from_coords(x, y)
        c2, r2 = self.col_row_from_coords(x + w, y + h)
        min_c = min(c1, c2, self.width - 1)
        max_c = max(c1, c2, 0)
        min_r = min(r1, r2, self.height - 1)
        max_r = max(r1, r2, 0)

        for col in range(min_c, max_c + 1):
            for row in range(min_r, max_r + 1):
                yield col, row

    def fill_rect(self, rect, v=1, only_if_empty=False):
        for col, row in self.find_col_row_of_rect(rect):
            if not only_if_empty or self.get_cell_by_col_row(col, row) is None:
                self.set_cell_col_row(col, row, v)

    def test_rect(self, rect, good_values=(0, 1)):
        return all(self.get_cell_by_col_row(c, r) in good_values for c, r in self.find_col_row_of_rect(rect))


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


class Field(GameObject):
    BACKGROUND_COLOR = (0, 0, 0)

    @GameObject.position.setter
    def position(self, p):
        GameObject.position.fset(self, p)
        self.map.position = p
        self.oc_map.position = p

    def __init__(self, cells_width=FIELD_WIDTH, cells_height=FIELD_HEIGHT):
        super().__init__()

        self.width = cells_width
        self.height = cells_height

        self._step = ATLAS().real_sprite_size

        self.map = DiscreteMap(self.position, self._step, cells_width, cells_height)
        self.oc_map = OccupancyMap(self.position, self._step // 2, cells_width * 2, cells_height * 2)

        self.position = (40, 40)

        self._sprites = {
            t: ATLAS().image_at(*t.sprite_location, 1, 1, colorkey=None) for t in CellType
        }

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        assert len(lines) >= self.height, "incomplete level"
        for _, (y, line) in zip(range(self.height), enumerate(lines)):
            assert len(line) >= self.width, "incomplete line"
            for _, (x, symbol) in zip(range(self.width), enumerate(line)):
                self.map.set_cell_col_row(x, y, CellType.from_symbol(symbol))
                if FIELD_DEBUG:
                    print(symbol, end='')
            if FIELD_DEBUG:
                print()  # new line


    @property
    def rect(self):
        return [*self.position, self._step * self.width, self._step * self.height]

    def render(self, screen):
        pygame.draw.rect(screen, self.BACKGROUND_COLOR, self.rect)

        for col in range(self.width):
            for row in range(self.height):
                cell = self.map.get_cell_by_col_row(col, row)
                if cell != cell.FREE:
                    coords = self.map.coord_by_col_and_row(col, row)
                    screen.blit(self._sprites[cell], coords)

        if FIELD_DEBUG:
            self.oc_map.render(screen)

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
        rmin, cmin = self.height, self.width

        for x, y in check_pts:
            col, row = self.map.col_row_from_coords(x, y)
            rmax = max(rmax, row)
            rmin = min(rmin, row)
            cmax = max(cmax, col)
            cmin = min(cmin, col)

        for c in range(cmin, cmax + 1):
            for r in range(rmin, rmax + 1):
                if not self.map.inside_col_row(c, r):
                    return True

                cell = self.map.get_cell_by_col_row(c, r)

                if not cell.can_tank_run_here:
                    x, y = self.map.coord_by_col_and_row(c, r)
                    abs_cell_rect = cell.calculate_rect(x, y, self._step)
                    if rect_intersection(test_rect, abs_cell_rect):
                        return True

        return False

    def get_center_of_cell(self, col, row):
        xs, ys = self.position
        return xs + col * self._step, ys + row * self._step

    def check_hit(self, p: Projectile):
        # todo: if a half brick - let it fly further
        candidates = set()
        for x, y in p.split_for_aim():
            cell = self.map.get_cell_by_coords(x, y)
            if cell is None:
                return True  # out of field - destroy
            elif cell.solid:
                col, row = self.map.col_row_from_coords(x, y)
                candidates.add((col, row))

        for col, row in candidates:
            cell = self.map.get_cell_by_col_row(col, row)  # type: CellType
            if cell == cell.BRICK:
                new_cell = {
                    Direction.LEFT: cell.BRICK_LEFT,
                    Direction.RIGHT: cell.BRICK_RIGHT,
                    Direction.UP: cell.BRICK_TOP,
                    Direction.DOWN: cell.BRICK_BOTTOM
                }[p.direction]
            elif cell.is_half_brick:
                new_cell = cell.FREE
            else:
                continue
            self.map.set_cell_col_row(col, row, new_cell)

        return bool(candidates)
