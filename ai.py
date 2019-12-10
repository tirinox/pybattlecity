from tank import Tank, Direction
from field import Field
from util import ArmedTimer, GameObject
import random


class TankAI:
    def __init__(self, tank: Tank, field: Field):
        self.tank = tank
        self.field = field

        self.fire_timer = ArmedTimer(delay=1.0)
        self.dir_timer = ArmedTimer(delay=2.0)

    def update(self):
        if self.tank.is_spawning:
            return

        if self.fire_timer.tick():
            self.tank.fire()
            self.fire_timer.start()

        if self.dir_timer.tick():
            self.tank.direction = Direction.random()
            self.dir_timer.delay = random.uniform(0.3, 3.0)
            self.dir_timer.start()

        self.tank.move_tank(self.tank.direction)

    def reset(self):
        self.tank.direction = Direction.random()


class EnemyFractionAI:
    MAX_ENEMIES = 5

    def __init__(self, field: Field, tanks: GameObject):
        self.tanks = tanks
        self.field = field
        self.ais = {}
        self.spawn_points = {
            (x, y): False for x, y in field.respawn_points(True)
        }
        self.spawn_timer = ArmedTimer(5.0)

    @property
    def all_enemies(self):
        return [t for t in self.tanks if t.fraction == Tank.ENEMY]

    def get_next_enemy(self):
        t_type = random.choice([
            Tank.Type.ENEMY_SIMPLE,
            Tank.Type.ENEMY_FAST,
            Tank.Type.ENEMY_HEAVY,
            Tank.Type.ENEMY_MIDDLE
        ])
        new_tank = Tank(Tank.ENEMY, Tank.Color.PLAIN, t_type)
        # new_tank.is_spawning = True
        pos = random.choice(self.field.respawn_points(True))
        new_tank.place(self.field.get_center_of_cell(*pos))
        return new_tank

    def update(self):
        if self.spawn_timer.tick():
            self.spawn_timer.start()
            if len(self.all_enemies) < self.MAX_ENEMIES:
                tank = self.get_next_enemy()
                self.tanks.add_child(tank)

        for enemy_tank in self.all_enemies:
            if not hasattr(enemy_tank, 'ai'):
                enemy_tank.ai = TankAI(enemy_tank, self.field)
            enemy_tank.ai.update()






