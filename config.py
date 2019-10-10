from spritesheet import SpriteSheet

GAME_WIDTH = 540
GAME_HEIGHT = 480

ATLAS_FILE = 'data/atlas.png'

_altas = None


def get_atlas() -> SpriteSheet:
    global _altas
    if _altas is None:
        _altas = SpriteSheet(ATLAS_FILE, upsample=2, sprite_size=8)
    return _altas

ATLAS = get_atlas

