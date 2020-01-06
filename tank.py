from config import *
from util import *
from math import ceil, floor


class Tank(GameObject):
    SPEED_NORMAL = 2
    SPEED_FAST = 3

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

        @property
        def next_level(self):
            if self == self.LEVEL_1:
                return self.LEVEL_2
            elif self == self.LEVEL_2:
                return self.LEVEL_3
            elif self == self.LEVEL_3:
                return self.LEVEL_4
            else:
                return self.LEVEL_4

        @property
        def max_level(self):
            return self.LEVEL_4

        @property
        def can_crash_concrete(self):
            return self == self.max_level

    POSSIBLE_MOVE_STATES = 0, 2

    SHIELD_TIME = 10

    FRIEND = 'friend'
    ENEMY = 'enemy'

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
        self._update_sprites()

    def fire(self):
        self.want_to_fire = True

    def _update_sprites(self):
        atlas = ATLAS()
        sprite_locations = {(d, s): self.get_sprite_location(self.color, self.tank_type, d, s)
                            for d in Direction
                            for s in self.POSSIBLE_MOVE_STATES}

        self.sprites = {key: atlas.image_at(*location, auto_crop=True, square=False)
                        for key, location in sprite_locations.items()}

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._update_sprites()

    def __init__(self, fraction, color=Color.YELLOW, tank_type=Type.LEVEL_1, fire_delay=0.5):
        super().__init__()

        self.fraction = fraction
        self.speed = self.SPEED_NORMAL
        self._direction = Direction.UP
        self._tank_type = tank_type
        self._color = color
        self.is_spawning = False

        self._update_sprites()
        
        self.hit = False
        self.to_destroy = False

        self.is_bonus = False
        self._bonus_animator = Animator(delay=0.5, max_states=2)

        self.moving = False
        self.move_animator = Animator(delay=0.1, max_states=2)

        self.remember_position()

        self.want_to_fire = False

        atlas = ATLAS()

        sz = atlas.real_sprite_size * 2 - 2
        self.size = sz, sz

        if DEBUG:
            for k, v in self.sprites.items():
                w, h = v.get_width(), v.get_height()
                print(k, w, h)

        self._shielded = False
        self._shield_timer = Timer(self.SHIELD_TIME)
        self._shield_animator = Animator(delay=0.04, max_states=2)
        self._shield_sprites = (
            atlas.image_at(32, 18, 2, 2),
            atlas.image_at(34, 18, 2, 2)
        )

        self._spawn_sprites = [
            atlas.image_at(xi, 12, 2, 2) for xi in range(32, 40, 2)
        ]
        self._spawn_animator = Animator(delay=0.1, max_states=len(self._spawn_sprites))

        self.fire_timer = Timer(fire_delay, paused=True)

    @property
    def shielded(self):
        return self._shielded

    @shielded.setter
    def shielded(self, v):
        self._shielded = v
        if self._shielded:
            self._shield_timer = Timer(self.SHIELD_TIME)
            self._shield_timer.start()
        else:
            self._shield_timer.stop()

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

        x, y = self.position

        # tank sprite is trimmed (it is smaller than 2x2 sprite)
        ctx = sprite.get_width() // 2
        cty = sprite.get_height() // 2

        if not self.is_spawning:
            screen.blit(sprite, (x - ctx, y - cty))

        # animate sprite when moving
        if self.moving:
            self.move_animator()

        if self.is_bonus:
            state = self._bonus_animator()
            self.color = Tank.Color.PURPLE if state == 0 else Tank.Color.PLAIN

        # it is size of a half of full 2x2 sprite, effects have full size unlike tanks
        half_full_size = ATLAS().real_sprite_size

        if not self._shield_timer.tick():
            shield_sprite = self._shield_sprites[self._shield_animator()]
            screen.blit(shield_sprite, (x - half_full_size, y - half_full_size))
        else:
            self._shielded = False

        if self.is_spawning:
            spawn_sprite = self._spawn_sprites[self._spawn_animator()]
            screen.blit(spawn_sprite, (x - half_full_size, y - half_full_size))

    def activate_shield(self):
        self.shielded = self.SHIELD_TIME

    @property
    def gun_point(self):
        """
        Calculate the coordinates of the gun of the tank
        :return: (x, y) coordinates of gun tip point
        """
        return self.position
        # x, y = self.position
        # _, _, w, h = self.bounding_rect
        # half_w, half_h = round(w / 2), round(h / 2)
        #
        # d = self.direction
        # if d == Direction.UP:
        #     return x, y - half_h - 1
        # elif d == Direction.DOWN:
        #     return x, y + half_h + 1
        # elif d == Direction.LEFT:
        #     return x - half_w - 1, y
        # elif d == Direction.RIGHT:
        #     return x + half_w + 1, y

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
        self.remember_position()
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

    def upgrade(self, maximum=False):
        if self.fraction == self.FRIEND:
            if maximum:
                self.tank_type = self.tank_type.max_level
                self._update_sprites()
            elif self.tank_type != self.tank_type.next_level:
                self.tank_type = self.tank_type.next_level
                self._update_sprites()
