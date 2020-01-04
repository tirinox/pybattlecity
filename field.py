from util import GameObject, Direction, rect_intersection, point_in_rect_eq
from config import *
from enum import Enum, auto
import pygame
from projectile import Projectile
from discrete_map import DiscreteMap, OccupancyMap


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
        self.size = (self._step * self.width, self._step * self.height)

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
        candidates = set()
        for x, y in p.split_for_aim():
            cell = self.map.get_cell_by_coords(x, y)
            if cell is None:
                return True  # out of field - destroy
            elif cell.solid:
                col, row = self.map.col_row_from_coords(x, y)
                candidates.add((col, row, x, y))

        hit = False
        for col, row, px, py in candidates:
            cell = self.map.get_cell_by_col_row(col, row)  # type: CellType

            cx, cy = self.map.coord_by_col_and_row(col, row)
            abs_cell_rect = cell.calculate_rect(cx, cy, self._step)

            if point_in_rect_eq(px, py, abs_cell_rect):
                hit = True

                powerful = p.power == p.POWER_HIGH

                if cell == cell.BRICK:
                    if powerful:
                        new_cell = cell.FREE
                    else:
                        new_cell = {
                            Direction.LEFT: cell.BRICK_LEFT,
                            Direction.RIGHT: cell.BRICK_RIGHT,
                            Direction.UP: cell.BRICK_TOP,
                            Direction.DOWN: cell.BRICK_BOTTOM
                        }[p.direction]
                elif cell.is_half_brick:
                    new_cell = cell.FREE
                elif cell == cell.CONCRETE and powerful:
                    new_cell = cell.FREE
                else:
                    continue
                self.map.set_cell_col_row(col, row, new_cell)

        return hit

    @staticmethod
    def respawn_points(is_enemy):
        return [
            (1, 1),
            (13, 1),
            (25, 1)
        ] if is_enemy else [
            (10, 25),
            (16, 25)
        ]

    def is_free_location_to_place_tank(self, x, y):
        lx, ly = self.map.coord_by_col_and_row(x, y)
        bb = lx - self._step, ly - self._step, self._step * 2, self._step * 2
        return self.oc_map.test_rect(bb)
