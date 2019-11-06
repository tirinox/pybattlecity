from tank import Tank, Direction
from field import Field
from util import ArmedTimer
import random


class AI:
    def __init__(self, tank: Tank, enemies: [Tank], field: Field):
        self.tank = tank
        self.field = field
        self.enemies = enemies

        self.fire_timer = ArmedTimer(delay=1.0)
        self.dir_timer = ArmedTimer(delay=2.0)

        self.want_to_fire = False

    def fire(self):
        self.want_to_fire = True

    def update(self):
        if self.fire_timer.tick():
            self.fire()
            self.fire_timer.start()

        if self.dir_timer.tick():
            self.tank.direction = Direction.random()
            self.dir_timer.delay = random.uniform(0.3, 3.0)
            self.dir_timer.start()

        self.tank.remember_position()
        self.tank.move_tank(self.tank.direction)
