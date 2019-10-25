from config import *
from util import *
from projectile import Projectile


class Tank(GameObject):
    class Color(Enum):
        # the value is (x, y) location on the sprite sheet in 8px blocks
        YELLOW = (0, 0)
        GREEN = (0, 16)
        PURPLE = (16, 16)
        PLAIN = (16, 0)

    class Type(Enum):
        LEVEL_1 = 0
        LEVEL_2 = 2
        LEVEL_3 = 4
        LEVEL_4 = 6
        ENEMY_SIMPLE = 8
        ENEMY_FAST = 10
        ENEMY_MIDDLE = 12
        ENEMY_HEAVY = 14

    POSSIBLE_MOVE_STATES = 0, 2

    def get_sprite_location(self, color: Color, type: Type, direction: Direction, state):
        # see: atlas.png to understand this code:
        x = color.value[0] + direction.value + state
        y = color.value[1] + type.value
        return x, y, 2, 2

    def __init__(self, color=Color.YELLOW, tank_type=Type.LEVEL_1, fire_delay=0.5):
        super().__init__()

        self.direction = Direction.UP
        self.color = color
        self.tank_type = tank_type

        self.moving = False
        self.move_animator = Animator(delay=0.1, max_states=2)

        atlas = ATLAS()

        sprite_locations = {(d, s): self.get_sprite_location(color, tank_type, d, s)
                            for d in Direction
                            for s in self.POSSIBLE_MOVE_STATES}

        self.sprites = {key: atlas.image_at(*location, auto_crop=True)
                        for key, location in sprite_locations.items()}

        self.shield_timer = Timer(5)
        self.shield_animator = Animator(delay=0.04, max_states=2)
        self.shield_sprites = (
            atlas.image_at(32, 18, 2, 2),
            atlas.image_at(34, 18, 2, 2)
        )

        self.fire_timer = Timer(fire_delay, paused=True)

    def try_fire(self):
        if self.fire_timer():
            self.fire_timer.start()
            return True
        return False

    @property
    def sprite_key(self):
        return self.direction, self.POSSIBLE_MOVE_STATES[self.move_animator.state]

    def render(self, screen):
        sprite = self.sprites[self.sprite_key]
        cx = round(sprite.get_width() / 2)
        cy = round(sprite.get_height() / 2)

        x, y = self.position
        screen.blit(sprite, (x - cx, y - cy))

        # animate sprite when moving
        if self.moving:
            self.move_animator()

        if not self.shield_timer.tick():
            shield_sprite = self.shield_sprites[self.shield_animator()]
            cx, cy = self.center_point
            sz = ATLAS().real_sprite_size
            screen.blit(shield_sprite, (cx - sz, cy - sz))

    def activate_shield(self):
        self.shield_timer.start()

    @property
    def gun_point(self):
        """
        Calculate the coordinates of the gun of the tank
        :return: (x, y) coordinates of gun tip point
        """
        x, y = self.position
        _, _, w, h = self.bounding_rect
        half_w, half_h = round(w / 2), round(h / 2)

        d = self.direction
        if d == Direction.UP:
            return x, y - half_h - 1
        elif d == Direction.DOWN:
            return x, y + half_h + 1
        elif d == Direction.LEFT:
            return x - half_w - 1, y
        elif d == Direction.RIGHT:
            return x + half_w + 1, y

    @property
    def center_point(self):
        return self.position

    @property
    def bounding_rect(self):
        sprite = self.sprites[self.sprite_key]
        w, h = sprite.get_width(), sprite.get_height()
        x, y = self.position
        return x - round(w / 2), y - round(h / 2), w, h

    def check_hit(self, p: Projectile):
        return point_in_rect(*p.position, self.bounding_rect)
