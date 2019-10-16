from config import ATLAS
from util import GameObject
from projectile import Projectile


class MyBase(GameObject):
    def __init__(self):
        super().__init__()
        self._normal_img = ATLAS().image_at(38, 4, 2, 2)
        self._broken_img = ATLAS().image_at(40, 4, 2, 2)
        self.x = self.y = 0
        self.broken = False

    def render(self, screen):
        img = self._broken_img if self.broken else self._normal_img
        screen.blit(img, (self.x, self.y))

    @property
    def center_point(self):
        size = ATLAS().real_sprite_size
        return self.x + size, self.y + size

    def check_hit(self, p: Projectile):
        size = ATLAS().real_sprite_size * 2
        return self.x <= p.x <= self.x + size and self.y <= p.y <= self.y + size
