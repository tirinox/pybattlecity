import pygame
from pygame.locals import *
from config import *
import spritesheet
import field
from explosion import Explosion
from tank import Tank
from util import GameObject
from random import randint


class Game:
    def __init__(self):
        self.atlas = spritesheet.SpriteSheet(ATLAS, upsample=2, sprite_size=8)
        self.field = field.Field(self.atlas)

        self.scene = GameObject()

        tank = self.tank = Tank(self.atlas, Tank.Color.PURPLE, Tank.Type.ENEMY_FAST)
        tank.x = 100
        tank.y = 100
        self.scene.add_child(tank)

        tank2 = Tank(self.atlas, Tank.Color.GREEN, Tank.Type.LEVEL_4)
        tank2.x = 200
        tank2.y = 200
        self.scene.add_child(tank2)

        self.font_debug = pygame.font.Font(None, 18)

    def switch_my_tank(self):
        tank = self.tank
        tank.remove_from_parent()
        t, d, x, y = tank.tank_type, tank.direction, tank.x, tank.y
        types = list(Tank.Type)
        current_index = types.index(t)
        next_type = types[(current_index + 1) % len(types)]
        tank = Tank(self.atlas, Tank.Color.PLAIN, next_type)
        tank.x, tank.y = x, y
        tank.direction = d
        self.scene.add_child(tank)
        self.tank = tank

    def make_explosion(self):
        pt = self.tank.center_point()
        expl = Explosion(self.atlas, *pt)
        self.scene.add_child(expl)

    def render(self, screen):
        self.scene.visit(screen)

        # - 1 because the scene is not literally an object
        dbg_text = f'Objects: {self.scene.total_children - 1}'
        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))
        screen.blit(dbg_label, (5, 5))


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

    game = Game()

    SHIFT = 5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    game.switch_my_tank()
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_f:
                    game.make_explosion()

        keys = pygame.key.get_pressed()

        tank = game.tank
        tank.moving = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            tank.direction = tank.Direction.UP
            tank.y -= SHIFT
            tank.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            tank.direction = tank.Direction.DOWN
            tank.y += SHIFT
            tank.moving = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            tank.direction = tank.Direction.LEFT
            tank.x -= SHIFT
            tank.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            tank.direction = tank.Direction.RIGHT
            tank.x += SHIFT
            tank.moving = True

        screen.fill((0, 0, 0))

        game.render(screen)

        # pygame.draw.circle(screen, (255, 0, 255), game.tank.gun_point(), 5)

        pygame.display.flip()

    pygame.quit()




