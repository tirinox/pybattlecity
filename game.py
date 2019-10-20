import pygame
from field import Field
from projectile import Projectile
from tank import Tank
from util import *
from explosion import Explosion
from my_base import MyBase
from math import floor, ceil
from config import *


class Game:
    TANK_SPEED = 4

    def __init__(self):
        self.scene = GameObject()

        # field --
        self.field = Field()
        self.field.load_from_file('data/level1.txt')
        self.scene.add_child(self.field)

        self.my_base = base = MyBase()
        base.x, base.y = self.field.coord_by_col_and_row(12, 24)
        self.scene.add_child(base)

        # tanks --
        self.tanks = GameObject()
        self.scene.add_child(self.tanks)

        tank = self.tank = Tank(Tank.Color.YELLOW, Tank.Type.LEVEL_1)
        tank.place(*self.field.get_center_of_cell(10, 25))
        tank.activate_shield()
        self.tanks.add_child(tank)

        enemy_tank = Tank(Tank.Color.PLAIN, Tank.Type.LEVEL_1)
        enemy_tank.direction = Direction.DOWN
        enemy_tank.place(*self.field.get_center_of_cell(9, 1))
        self.enemy_tank = enemy_tank
        self.tanks.add_child(enemy_tank)

        self.enemy_fire_timer = Timer(delay=1, paused=False)

        # projectiles --
        self.projectiles = GameObject()
        self.scene.add_child(self.projectiles)

        # else --
        self.font_debug = pygame.font.Font(None, 18)

    def switch_my_tank(self):
        tank = self.tank
        tank.remove_from_parent()
        t, d, x, y = tank.tank_type, tank.direction, tank.x, tank.y
        types = list(Tank.Type)
        current_index = types.index(t)
        next_type = types[(current_index + 1) % len(types)]
        tank = Tank(Tank.Color.PLAIN, next_type)
        tank.x, tank.y = x, y
        tank.direction = d
        tank.activate_shield()
        self.scene.add_child(tank)
        self.tank = tank

    def make_explosion(self, x, y, short=False):
        expl = Explosion(x, y, short)
        self.scene.add_child(expl)

    def render(self, screen):
        self.scene.visit(screen)

        # - 1 because the scene is not literally an object
        dbg_text = f'Objects: {self.scene.total_children - 1}'
        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))
        screen.blit(dbg_label, (5, 5))

        if self.enemy_fire_timer.tick():
            self.fire(self.enemy_tank)
            self.enemy_fire_timer.start()

        for p in self.projectiles:  # type: Projectile
            if self.field.check_hit(p):
                p.remove_from_parent()
                self.make_explosion(p.x, p.y, short=True)
                continue

            if self.my_base.check_hit(p):
                self.my_base.broken = True
                p.remove_from_parent()
                self.make_explosion(*self.my_base.center_point)
                continue

            for t in self.tanks:  # type: Tank
                if t.check_hit(p):
                    self.make_explosion(p.x, p.y)
                    p.remove_from_parent()
                    continue

    def fire(self, tank=None):
        tank = self.tank if tank is None else tank
        if tank.try_fire():
            projectile = Projectile(*tank.gun_point, tank.direction, 1)
            self.projectiles.add_child(projectile)

    def move_tank(self, direction: Direction, tank=None):
        tank = self.tank if tank is None else tank
        tank.moving = True
        tank.direction = direction
        vx, vy = direction.vector
        vx *= self.TANK_SPEED
        vy *= self.TANK_SPEED
        tank.x += vx
        tank.y += vy

        push_back = self.field.intersect_rect(tank.bounding_rect)

        if not push_back:
            my_bb = tank.bounding_rect
            for other_tank in self.tanks:  # type: Tank
                if tank is not other_tank:
                    if rect_intersection(my_bb, other_tank.bounding_rect):
                        push_back = True
                        break

        if push_back:
            # undo movement
            tank.x -= vx
            tank.y -= vy

    def complete_moving(self):
        tank = self.tank
        discrete_step = ATLAS().real_sprite_size // 2
        if self.tank.moving:
            vx, vy = self.tank.direction.vector
            if vx != 0:
                f = floor if vx < 0 else ceil
                tank.x = f(tank.x / discrete_step) * discrete_step
            if vy != 0:
                f = floor if vy < 0 else ceil
                tank.y = f(tank.y / discrete_step) * discrete_step

        self.tank.moving = False
