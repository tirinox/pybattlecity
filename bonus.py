from util import GameObject, rect_intersection
from pygame import Surface
from enum import Enum
from config import ATLAS


class BonusType(Enum):
    # value is sprite sheet location
    CASK = (32, 14)
    TIMER = (34, 14)
    STIFF_BASE = (36, 14)
    UPGRADE = (38, 14)
    DESTRUCTION = (40, 14)
    TOP_TANK = (42, 14)
    GUN = (44, 14)


class Bonus(GameObject):
    def __init__(self, bonus_type: BonusType, x, y):
        super().__init__()
        self.type = bonus_type
        self.sprite = ATLAS().image_at(*bonus_type.value, 2, 2)
        self.position = x, y
        sz = ATLAS().real_sprite_size * 2
        self.size = (sz, sz)

    def render(self, screen: Surface):
        screen.blit(self.sprite, self.position)
