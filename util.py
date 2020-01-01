import time
from collections import OrderedDict
from enum import Enum
from pygame import Surface
import random
import itertools


DEMO_COLORS = list(itertools.product(*([(0, 128, 255)] * 3)))[1:]

COLOR_BLACK_KEY = (0, 0, 1, 255)


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

    @classmethod
    def random(cls):
        return random.choice(list(cls))

    @classmethod
    def all(cls):
        return set(cls)


class Animator:
    def __init__(self, delay=0.1, max_states=5, once=False):
        self.max_states = max_states
        self.delay = delay
        self.state = 0
        self.once = once
        self.done = False
        self.last_time = time.monotonic()

    def __call__(self):
        if self.last_time + self.delay < time.monotonic():
            self.last_time = time.monotonic()
            self.state += 1
            if self.state >= self.max_states:
                if self.once:
                    self.done = True
                else:
                    self.state = 0
        return self.state

    @property
    def active(self):
        return not self.done


class Timer(Animator):
    def __init__(self, delay, paused=True):
        super().__init__(delay, 1, once=True)
        if paused:
            self.done = True

    def start(self):
        self.done = False
        self.state = 0
        self.last_time = time.monotonic()

    def tick(self):
        if not self.done:
            self()
        return self.done

    def stop(self):
        self.done = True


class ArmedTimer(Timer):
    def __init__(self, delay):
        super().__init__(delay, paused=False)


class GameObject:
    def __init__(self):
        self._parent = None
        self._children = OrderedDict()
        self._position = (0, 0)
        self.size = (0, 0)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, p):
        self._position = p

    def move(self, dx, dy):
        x, y = self.position
        self.position = x + dx, y + dy

    @property
    def bounding_rect(self):
        return (*self.position, *self.size)

    def intersects_rect(self, r):
        return rect_intersection(r, self.bounding_rect)

    def __hash__(self):
        return id(self)

    def __iter__(self):
        return iter(OrderedDict(self._children))

    def __getitem__(self, item):
        return self._children[item]

    def add_child(self, child: 'GameObject'):
        child._parent = self
        self._children[child] = 1

    def remove_child(self, child):
        del self._children[child]

    def remove_from_parent(self):
        if self._parent is not None:
            self._parent.remove_child(self)
            self._parent = None

    def visit(self, screen: Surface):
        self.render(screen)
        for child in list(self._children.keys()):
            child.visit(screen)

    def render(self, screen):
        ...

    @property
    def total_children(self):
        return 1 + sum(child.total_children for child in self._children)


def trim_rect(rect, amount):
    x, y, w, h = rect
    return x + amount, y + amount, w - amount * 2, h - amount * 2


def extend_rect(rect, amount):
    return trim_rect(rect, -amount)


def rect_intersection(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return ax < bx + bw and ax + aw > bx and \
           ay < by + bh and ay + ah > by


def rect_intersection_eq(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return ax <= bx + bw and ax + aw >= bx and \
           ay <= by + bh and ay + ah >= by


def point_in_rect(px, py, rect):
    x, y, w, h = rect
    return x < px < x + w and y < py < y + h


def point_in_rect_eq(px, py, rect):
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h
