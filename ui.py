from config import ATLAS, GAME_WIDTH, GAME_HEIGHT
from util import GameObject


class GameOverLabel(GameObject):
    def __init__(self):
        super().__init__()
        self._image = ATLAS().image_at(36, 23, 4, 2)
        size = ATLAS().real_sprite_size
        self.size = (size * 4, size * 2)

    def place_at_center(self, go: GameObject):
        x, y = go.position
        w, h = go.size
        self.position = x + (w - self.size[0]) // 2, y + (h - self.size[1]) // 2 + 2

    def render(self, screen):
        screen.blit(self._image, self.position)
