from config import ATLAS
from util import GameObject, point_in_rect


class MyBase(GameObject):
    def __init__(self):
        super().__init__()
        self._normal_img = ATLAS().image_at(38, 4, 2, 2)
        self._broken_img = ATLAS().image_at(40, 4, 2, 2)
        self.broken = False
        size = ATLAS().real_sprite_size * 2 - 1
        self.size = (size, size)

    def render(self, screen):
        img = self._broken_img if self.broken else self._normal_img
        screen.blit(img, self.position)

    @property
    def center_point(self):
        x, y = self.position
        w, h = self.size
        return x + w // 2, y + h // 2

    def check_hit(self, x, y):
        return point_in_rect(x, y, self.bounding_rect)
