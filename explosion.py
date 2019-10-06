from spritesheet import SpriteSheet
from util import *


class Explosion(GameObject):
    SPRITE_DESCRIPTORS = (
        (32, 16, 2, 2),
        (34, 16, 2, 2),
        (36, 16, 2, 2),
        (38, 16, 4, 4),
        (42, 16, 4, 4)
    )

    N_STATES = len(SPRITE_DESCRIPTORS)

    def __init__(self, atlas: SpriteSheet, x, y):
        super().__init__()
        self.atlas = atlas
        self.x = x
        self.y = y
        self.animator = Animator(0.08, self.N_STATES, once=True)
        self.sprites = [atlas.image_at(x, y, sx, sy) for
                        x, y, sx, sy in self.SPRITE_DESCRIPTORS]

    def render(self, screen):
        state = self.animator()

        if self.animator.done:
            self.remove_from_parent()
        else:
            _, _, w, h = self.SPRITE_DESCRIPTORS[state]
            w_pix = w * self.atlas.sprite_size
            h_pix = h * self.atlas.sprite_size
            x, y = self.x - w_pix, self.y - h_pix
            sprite = self.sprites[state]
            screen.blit(sprite, (x, y))
