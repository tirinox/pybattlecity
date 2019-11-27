from config import *
from util import *


class Explosion(GameObject):
    SPRITE_DESCRIPTORS = (
        (32, 16, 2, 2),
        (34, 16, 2, 2),
        (36, 16, 2, 2),
        (38, 16, 4, 4),
        (42, 16, 4, 4)
    )

    TYPE_SUPER_SHORT = 'super_short'
    TYPE_SHORT = 'short'
    TYPE_FULL = 'full'

    _n_states = {
        TYPE_FULL: len(SPRITE_DESCRIPTORS),
        TYPE_SHORT: 3,
        TYPE_SUPER_SHORT: 2
    }

    def __init__(self, x, y, type=TYPE_FULL):
        super().__init__()

        self.position = x, y
        n = self._n_states[type]
        self.animator = Animator(0.08, n, once=True)
        self.sprites = [ATLAS().image_at(x, y, sx, sy) for
                        x, y, sx, sy in self.SPRITE_DESCRIPTORS]

    def render(self, screen):
        state = self.animator()

        if self.animator.done:
            self.remove_from_parent()
        else:
            _, _, w, h = self.SPRITE_DESCRIPTORS[state]
            half_sprite_size = ATLAS().real_sprite_size // 2
            w_pix = w * half_sprite_size
            h_pix = h * half_sprite_size
            x, y = self.position
            x -= w_pix
            y -= h_pix
            sprite = self.sprites[state]
            screen.blit(sprite, (x, y))
