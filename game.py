import pygame
from field import Field
from projectile import Projectile
from tank import Tank
from util import *
from explosion import Explosion
from my_base import MyBase
from bonus import Bonus, BonusType
from ai import AI
import random


class Game:
    def __init__(self):
        self.r = random.Random()

        self.scene = GameObject()

        # field --
        self.field = Field()
        self.field.load_from_file('data/level1.txt')
        self.scene.add_child(self.field)

        self.my_base = MyBase()
        self.my_base.position = self.field.map.coord_by_col_and_row(12, 24)
        self.scene.add_child(self.my_base)

        # tanks --
        self.tanks = GameObject()
        self.scene.add_child(self.tanks)

        tank = self.tank = Tank(Tank.Color.YELLOW, Tank.Type.LEVEL_1)
        tank.place(self.field.get_center_of_cell(10, 25))
        tank.activate_shield()
        self.tanks.add_child(tank)

        self.make_enemy()

        # projectiles --
        self.projectiles = GameObject()
        self.scene.add_child(self.projectiles)

        # else --
        self.font_debug = pygame.font.Font(None, 18)
        self._stop_moving = False

        # bonuses --
        self.bonues = GameObject()
        self.scene.add_child(self.bonues)
        self.make_bonus()

    def respawn_tank(self, t: Tank):
        my = t is self.tank
        pos = (10, 25) if my else (9, 1)
        # t.place(self.field.get_center_of_cell(*pos))

    def make_enemy(self):
        enemy_tank = Tank(Tank.Color.PLAIN, Tank.Type.LEVEL_1)
        enemy_tank.direction = Direction.DOWN
        enemy_tank.place(self.field.get_center_of_cell(9, 1))
        self.enemy_tank = enemy_tank
        self.tanks.add_child(enemy_tank)
        self.enemy_ai = AI(self.enemy_tank, enemies=[self.tank], field=self.field)

    def make_bonus(self):
        col = self.r.randint(0, self.field.width - 1)
        row = self.r.randint(0, self.field.height - 1)
        bonus = Bonus(BonusType.UPGRADE, *self.field.get_center_of_cell(col, row))
        self.bonues.add_child(bonus)

    def switch_my_tank(self):
        tank = self.tank
        t, d, p = tank.tank_type, tank.direction, tank.position
        tank.remove_from_parent()

        types = list(Tank.Type)
        current_index = types.index(t)
        next_type = types[(current_index + 1) % len(types)]
        tank = Tank(Tank.Color.PLAIN, next_type)
        tank.position = tank.old_position = p
        tank.direction = d
        tank.activate_shield()
        self.tanks.add_child(tank)
        self.tank = tank

    def make_explosion(self, x, y, short=False):
        self.scene.add_child(Explosion(x, y, short))

    def fire(self, tank=None):
        tank = self.tank if tank is None else tank
        if tank.try_fire():
            projectile = Projectile(*tank.gun_point, tank.direction, sender=tank)
            self.projectiles.add_child(projectile)

    def move_tank(self, direction: Direction, tank=None):
        tank = self.tank if tank is None else tank
        tank.remember_position()
        tank.move_tank(direction)

    def complete_moving(self):
        self._stop_moving = True

    def update_bonuses(self):
        for b in self.bonues:  # type: Bonus
            if b.intersects_rect(self.tank.bounding_rect):
                b.remove_from_parent()
                self.make_bonus()

    def update_tanks(self):
        for i, tank in enumerate(self.tanks, start=1):
            self.field.oc_map.fill_rect(tank.bounding_rect, i)


        if self._stop_moving:
            self._stop_moving = False
            self.tank.stop()
            self.tank.align()

        self.enemy_ai.update()
        if self.enemy_ai.want_to_fire:
            self.enemy_ai.want_to_fire = False
            self.fire(self.enemy_ai.tank)

        for i, tank in enumerate(self.tanks, start=1):
            bb = tank.bounding_rect
            if not self.field.oc_map.test_rect(bb, good_values=(0, i)):
                push_back = True
            else:
                push_back = self.field.intersect_rect(bb)

            if push_back:
                tank.undo_move()

    def update_projectiles(self):
        for p in self.projectiles:  # type: Projectile
            was_hit = False
            x, y = p.position
            if self.field.check_hit(p):
                was_hit = True
            elif self.my_base.check_hit(x, y):
                self.my_base.broken = True
                was_hit = True
            else:
                for t in self.tanks:  # type : Tank
                    if p.sender is not t and t.check_hit(x, y):
                        was_hit = True
                        self.respawn_tank(t)
                        break

            if was_hit:
                p.remove_from_parent()
                self.make_explosion(x, y, short=True)

    def update(self):
        self.field.oc_map.clear()

        self.update_tanks()
        self.update_bonuses()
        self.update_projectiles()


    # ---- render ----

    def render(self, screen):
        self.scene.visit(screen)

        # - 1 because the scene is not literally an object
        dbg_text = f'Objects: {self.scene.total_children - 1}'
        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))
        screen.blit(dbg_label, (5, 5))
