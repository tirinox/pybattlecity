from util import GameObject, ArmedTimer
from config import *
import pygame
from collections import namedtuple


ScoreNode = namedtuple('ScoreNode', ('x', 'y', 'sprite', 'timer'))


class ScoreLayer(GameObject):
    SCORE_STAY_TIME = 1.0

    def __init__(self):
        super().__init__()
        self._entities = []

        a = ATLAS()

        self._dx = a.real_sprite_size

        def score_sprite(x, y):
            return a.image_at(x, y, 2, 2)

        self._sprites = {
            100: score_sprite(36, 20),
            200: score_sprite(38, 20),
            300: score_sprite(40, 20),
            400: score_sprite(42, 20),
            500: score_sprite(44, 20),
        }

    def add(self, x, y, score):
        if score not in self._sprites:
            print(f"I can't show this score: {score}")
            return

        x -= self._dx
        y += self._dx

        self._entities.append(ScoreNode(
            x, y,
            self._sprites[score],
            ArmedTimer(self.SCORE_STAY_TIME)
        ))

    def render(self, screen: pygame.Surface):
        for x, y, sprite, _ in self._entities:
            screen.blit(sprite, (x, y))

    def update(self):
        def _still_ticking(e: ScoreNode):
            e.timer.tick()
            return not e.timer.done
        self._entities = [e for e in self._entities if _still_ticking(e)]
