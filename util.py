import time
from collections import OrderedDict
import pygame


COLOR_BLACK_KEY = (0, 0, 1, 255)


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


class GameObject:
    def __init__(self):
        self._parent = None
        self._children = OrderedDict()
        self.position = (0, 0)

    def __hash__(self):
        return id(self)

    def add_child(self, child: 'GameObject'):
        child._parent = self
        self._children[child] = 1

    def remove_child(self, child):
        del self._children[child]

    def remove_from_parent(self):
        if self._parent is not None:
            self._parent.remove_child(self)
            self._parent = None

    def visit(self, screen):
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
