import random
from enum import Enum

from pygame import Surface

from config import ATLAS
from util import GameObject


class BonusType(Enum):
    # value is sprite sheet location
    CASK = (32, 14)
    TIMER = (34, 14)
    STIFF_BASE = (36, 14)
    UPGRADE = (38, 14)
    DESTRUCTION = (40, 14)
    TOP_TANK = (42, 14)
    GUN = (44, 14)

    @classmethod
    def random(cls):
        return random.choice(list(cls))


class Bonus(GameObject):
    def __init__(self, bonus_type: BonusType, x, y):
        super().__init__()
        self.type = bonus_type
        self.sprite = ATLAS().image_at(*bonus_type.value, 2, 2)

        sz = ATLAS().real_sprite_size
        self.position = x - sz, y - sz

        self.size = (sz * 2, sz * 2)

    def render(self, screen: Surface):
        screen.blit(self.sprite, self.position)
