from spritesheet import SpriteSheet
import sys

FIELD_DEBUG = '--field-debug' in sys.argv
DEBUG = '--debug' in sys.argv
PROJECTILE_DEBUG = '--projectile-debug' in sys.argv

GAME_WIDTH = 540
GAME_HEIGHT = 480

FIELD_HEIGHT = FIELD_WIDTH = 13 * 2  # 13 full blocks by (2x2) cells each

ATLAS_FILE = 'data/atlas.png'

_altas = None

def get_atlas() -> SpriteSheet:
    global _altas
    if _altas is None:
        _altas = SpriteSheet(ATLAS_FILE, upsample=2, sprite_size=8)
    return _altas

ATLAS = get_atlas
