from tank import Tank, Direction
from field import Field
from util import ArmedTimer, GameObject
import random


class TankAI:
    SPAWNING_DELAY = 1.5
    FIRE_TIMER = 1.0

    @staticmethod
    def dir_delay():
        return random.uniform(0.3, 3.0)

    def pick_direction(self):
        c, r = self.field.map.col_row_from_coords(*self.tank.position)
        prohibited_dir = set()
        # prohibited_dir.add(self.tank.direction)

        if c <= 1:
            prohibited_dir.add(Direction.LEFT)
        if r <= 1:
            prohibited_dir.add(Direction.UP)
        if c >= self.field.map.width - 2:
            prohibited_dir.add(Direction.RIGHT)
        if r >= self.field.map.height - 2:
            prohibited_dir.add(Direction.DOWN)
        return random.choice(list(Direction.all() - prohibited_dir))

    def __init__(self, tank: Tank, field: Field):
        self.tank = tank
        self.field = field

        self.fire_timer = ArmedTimer(delay=self.FIRE_TIMER)
        self.dir_timer = ArmedTimer(delay=self.dir_delay())
        self.spawn_timer = ArmedTimer(delay=self.SPAWNING_DELAY)

    def update(self):
        if self.tank.is_spawning:
            if self.spawn_timer.tick():
                self.tank.is_spawning = False
                # if self.field.oc_map.test_rect(self.tank.bounding_rect):
                #     self.tank.is_spawning = False
                # else:
                #     return
            else:
                return

        if self.fire_timer.tick():
            self.tank.fire()
            self.fire_timer.start()

        if self.dir_timer.tick():
            self.tank.direction = self.pick_direction()
            self.dir_timer.delay = self.dir_delay()
            self.dir_timer.start()

        self.tank.move_tank(self.tank.direction)

    def reset(self):
        self.tank.direction = Direction.random()


class EnemyFractionAI:
    MAX_ENEMIES = 5

    RESPAWN_TIMER = 5.0

    def __init__(self, field: Field, tanks: GameObject):
        self.tanks = tanks
        self.field = field
        self.spawn_points = {
            (x, y): None for x, y in field.respawn_points(True)
        }
        self.spawn_timer = ArmedTimer(self.RESPAWN_TIMER)
        self.try_to_spawn_tank()

    @property
    def all_enemies(self):
        return [t for t in self.tanks if t.fraction == Tank.ENEMY]

    def get_next_enemy(self, pos):
        t_type = random.choice([
            Tank.Type.ENEMY_SIMPLE,
            Tank.Type.ENEMY_FAST,
            Tank.Type.ENEMY_HEAVY,
            Tank.Type.ENEMY_MIDDLE
        ])
        new_tank = Tank(Tank.ENEMY, Tank.Color.PLAIN, t_type)
        new_tank.is_spawning = True

        new_tank.ai = TankAI(new_tank, self.field)

        new_tank.place(self.field.get_center_of_cell(*pos))
        return new_tank

    def try_to_spawn_tank(self):
        free_locations = list()
        for loc, tank in self.spawn_points.items():
            if isinstance(tank, Tank):
                if not tank.is_spawning:
                    self.spawn_points[loc] = None
            else:
                free_locations.append(loc)

        if free_locations and len(self.all_enemies) < self.MAX_ENEMIES:
            pos = random.choice(free_locations)
            tank = self.get_next_enemy(pos)
            self.spawn_points[pos] = tank
            self.tanks.add_child(tank)

    def update(self):
        if self.spawn_timer.tick():
            self.spawn_timer.start()
            self.try_to_spawn_tank()

        for enemy_tank in self.all_enemies:
            enemy_tank.ai.update()
