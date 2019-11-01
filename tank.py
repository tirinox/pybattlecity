from config import *
from util import *
from math import ceil, floor


class Tank(GameObject):
    SPEED_NORMAL = 4
    SPEED_FAST = 6

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

    @staticmethod
    def get_sprite_location(color: Color, type: Type, direction: Direction, state):
        # see: atlas.png to understand this code:
        x = color.value[0] + direction.value + state
        y = color.value[1] + type.value
        return x, y, 2, 2

    @property
    def tank_type(self):
        return self._tank_type

    @tank_type.setter
    def tank_type(self, t: Type):
        self._tank_type = t
        if t == t.ENEMY_FAST:
            self.speed = self.SPEED_FAST
        else:
            self.speed = self.SPEED_NORMAL

    def __init__(self, color=Color.YELLOW, tank_type=Type.LEVEL_1, fire_delay=0.5):
        super().__init__()

        self._direction = Direction.UP
        self.color = color
        self.tank_type = tank_type

        self.moving = False
        self.move_animator = Animator(delay=0.1, max_states=2)

        self.remember_position()

        atlas = ATLAS()

        sz = atlas.real_sprite_size * 2 - 2
        self.size = sz, sz

        sprite_locations = {(d, s): self.get_sprite_location(color, tank_type, d, s)
                            for d in Direction
                            for s in self.POSSIBLE_MOVE_STATES}

        self.sprites = {key: atlas.image_at(*location, auto_crop=True, square=False)
                        for key, location in sprite_locations.items()}

        self.shield_timer = Timer(5)
        self.shield_animator = Animator(delay=0.04, max_states=2)
        self.shield_sprites = (
            atlas.image_at(32, 18, 2, 2),
            atlas.image_at(34, 18, 2, 2)
        )

        self.fire_timer = Timer(fire_delay, paused=True)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_dir: Direction):
        self._direction = new_dir

        discrete_step = ATLAS().real_sprite_size // 2
        x, y = self.position
        vx, vy = self._direction.vector
        if vx != 0:
            f = floor if vx < 0 else ceil
            x = f(x / discrete_step) * discrete_step
        if vy != 0:
            f = floor if vy < 0 else ceil
            y = f(y / discrete_step) * discrete_step
        self.finish_position = x, y

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
        w, h = self.size
        x, y = self.position
        return x - round(w / 2), y - round(h / 2), w, h

    def check_hit(self, x, y):
        return point_in_rect(x, y, self.bounding_rect)

    def place(self, position):
        self.position = tuple(position)
        self.remember_position()

    def move_tank(self, direction: Direction):
        self.moving = True
        self.direction = direction
        vx, vy = direction.vector
        self.move(vx * self.speed, vy * self.speed)

    def remember_position(self):
        self.old_position = tuple(self.position)

    def undo_move(self):
        self.position = tuple(self.old_position)

    def stop(self):
        self.moving = False

    def align(self):
        discrete_step = ATLAS().real_sprite_size // 2
        x, y = self.position
        vx, vy = self.direction.vector
        if vx != 0:
            f = floor if vx < 0 else ceil
            x = f(x / discrete_step) * discrete_step
        if vy != 0:
            f = floor if vy < 0 else ceil
            y = f(y / discrete_step) * discrete_step
        self.position = (x, y)
