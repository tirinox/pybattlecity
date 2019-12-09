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
    def __init__(self, field: Field, tanks: GameObject):
        self.tanks = tanks
        self.field = field
        self.ais = {}

    @property
    def all_enemies(self):
        return [t for t in self.tanks if t.fraction == Tank.ENEMY]

    def update(self):
        for t in self.all_enemies:
            if not hasattr(t, 'ai'):
                t.ai = TankAI(t, self.field)
            t.ai.update()
