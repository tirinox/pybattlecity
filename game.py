import pygame
from field import Field
from projectile import Projectile
from tank import Tank
from util import *
from ui import *
from explosion import Explosion
from my_base import MyBase
from bonus import Bonus, BonusType
from ai import EnemyFractionAI
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

        self.make_my_tank()
        self.make_enemy()

        # projectiles --
        self.projectiles = GameObject()
        self.scene.add_child(self.projectiles)

        # bonuses --
        self.bonues = GameObject()
        self.scene.add_child(self.bonues)
        self.make_bonus()

        # else --
        self.font_debug = pygame.font.Font(None, 18)

    def respawn_tank(self, t: Tank):
        pos = random.choice(self.field.respawn_points(not self.is_friend(t)))
        t.place(self.field.get_center_of_cell(*pos))

    def make_my_tank(self):
        self.my_tank = Tank(Tank.FRIEND, Tank.Color.YELLOW, Tank.Type.LEVEL_1)
        self.respawn_tank(self.my_tank)
        self.my_tank.activate_shield()
        self.tanks.add_child(self.my_tank)
        self.my_tank_move_to_direction = None

    def make_enemy(self):
        self.ai = EnemyFractionAI(self.field, self.tanks)

        enemy_tank = Tank(Tank.ENEMY, Tank.Color.PLAIN, Tank.Type.LEVEL_1)
        enemy_tank.direction = Direction.DOWN
        self.respawn_tank(enemy_tank)
        self.enemy_tank = enemy_tank
        self.tanks.add_child(enemy_tank)

    def make_bonus(self):
        col = self.r.randint(0, self.field.width - 1)
        row = self.r.randint(0, self.field.height - 1)
        bonus = Bonus(BonusType.UPGRADE, *self.field.get_center_of_cell(col, row))
        self.bonues.add_child(bonus)

    def switch_my_tank(self):
        tank = self.my_tank
        t, d, p = tank.tank_type, tank.direction, tank.position
        tank.remove_from_parent()

        types = list(Tank.Type)
        current_index = types.index(t)
        next_type = types[(current_index + 1) % len(types)]
        tank = Tank(Tank.Color.PLAIN, next_type)
        tank.position = tank.old_position = p
        tank.direction = d
        tank.shielded = True
        tank.activate_shield()
        self.tanks.add_child(tank)
        self.my_tank = tank

    def make_explosion(self, x, y, expl_type):
        self.scene.add_child(Explosion(x, y, expl_type))

    def is_friend(self, tank):
        return tank.fraction == tank.FRIEND

    def fire(self, tank=None):
        tank = self.my_tank if tank is None else tank
        tank.want_to_fire = False

        if self.is_game_over and self.is_friend(tank):
            return

        if tank.try_fire():
            projectile = Projectile(*tank.gun_point, tank.direction, sender=tank)
            self.projectiles.add_child(projectile)

    def move_tank(self, direction: Direction, tank=None):
        tank = self.my_tank if tank is None else tank
        tank.remember_position()
        tank.move_tank(direction)

    def update_bonuses(self):
        for b in self.bonues:  # type: Bonus
            if b.intersects_rect(self.my_tank.bounding_rect):
                b.remove_from_parent()
                self.my_tank.shielded = True
                self.make_bonus()

    @property
    def all_mature_tanks(self):
        return (t for t in self.tanks if not t.is_spawning)

    @property
    def is_game_over(self):
        return self.my_base.broken

    def update_tanks(self):
        for tank in self.all_mature_tanks:
            self.field.oc_map.fill_rect(tank.bounding_rect, tank, only_if_empty=True)

        if not self.is_game_over:
            if self.my_tank_move_to_direction is None:
                self.my_tank.stop()
                self.my_tank.align()
            else:
                self.move_tank(self.my_tank_move_to_direction, self.my_tank)

        self.ai.update()

        for tank in self.all_mature_tanks:
            if tank.want_to_fire:
                self.fire(tank)

            bb = tank.bounding_rect
            if not self.field.oc_map.test_rect(bb, good_values=(None, tank)):
                push_back = True
            else:
                push_back = self.field.intersect_rect(bb)

            if push_back:
                tank.undo_move()

    def is_player_tank(self, t: Tank):
        return t is self.my_tank

    def kill_tank(self, t: Tank):
        self.respawn_tank(t)

    def make_game_over(self):
        self.my_base.broken = True
        go = GameOverLabel()
        self.scene.add_child(go)
        
    def update_projectiles(self):
        for p in self.projectiles:  # type: Projectile
            r = extend_rect((*p.position, 0, 0), 2)
            self.field.oc_map.fill_rect(r, p)

        remove_projectiles_waitlist = set()

        for p in self.projectiles:  # type: Projectile
            p.update()

            something = self.field.oc_map.get_cell_by_coords(*p.position)
            if something and something is not p and isinstance(something, Projectile):
                remove_projectiles_waitlist.add(p)
                remove_projectiles_waitlist.add(something)

            was_hit = None
            x, y = p.position
            if self.field.check_hit(p):
                was_hit = self.field
            elif self.my_base.check_hit(x, y):
                self.make_game_over()
                was_hit = self.my_base
            else:
                for t in self.all_mature_tanks:  # type : Tank
                    if p.sender is not t and t.check_hit(x, y):
                        was_hit = t
                        if not t.shielded:
                            self.kill_tank(t)
                        break

            if was_hit:
                remove_projectiles_waitlist.add(p)
                hit_tank = isinstance(was_hit, Tank)
                if hit_tank and not was_hit.shielded:
                    self.make_explosion(x, y, Explosion.TYPE_FULL)
                elif not hit_tank:
                    self.make_explosion(x, y, Explosion.TYPE_SUPER_SHORT)

        for p in remove_projectiles_waitlist:
            p.remove_from_parent()

    def update(self):
        self.field.oc_map.clear()
        self.field.oc_map.fill_rect(self.my_base.bounding_rect, self.my_base)

        self.update_tanks()
        self.update_bonuses()
        self.update_projectiles()

    # ---- render ----

    def render(self, screen):
        self.scene.visit(screen)

        # - 1 because the scene is not literally an object
        dbg_text = f'Objects: {self.scene.total_children - 1}'
        if self.is_game_over:
            dbg_text = 'Press R to restart! ' + dbg_text

        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))
        screen.blit(dbg_label, (5, 5))

    # --- test ---

    def testus(self):
        self.respawn_tank(self.my_tank)
