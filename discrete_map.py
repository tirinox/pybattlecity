from math import floor
from config import *
from util import DEMO_COLORS
import pygame


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
        cells_to_test = self.find_col_row_of_rect(rect)
        return self.test_cells(cells_to_test, good_values)

    def test_cells(self, cols_rows, good_values=(0,)):
        return all(self.get_cell_by_col_row(c, r) in good_values for c, r in cols_rows)
