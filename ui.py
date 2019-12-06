from config import ATLAS, GAME_WIDTH, GAME_HEIGHT
from util import GameObject


class GameOverLabel(GameObject):
    def __init__(self):
        super().__init__()
        self._image = ATLAS().image_at(36, 23, 4, 2)
        size = ATLAS().real_sprite_size
        self.size = (size * 4, size * 2)
        self.position = GAME_WIDTH // 2 - self.size[0] // 2, GAME_HEIGHT // 2 - self.size[1] // 2

    def render(self, screen):
        screen.blit(self._image, self.position)
