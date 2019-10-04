import pygame
from pygame.locals import *
from config import *
import spritesheet
import field
from explosion import Explosion
from tank import Tank
from random import randint


pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

atlas = spritesheet.SpriteSheet(ATLAS, upsample=2, sprite_size=8)
field = field.Field(atlas)

tank_id = 5
tank = Tank(atlas, Tank.Color.PURPLE, Tank.Type.ENEMY_FAST)
tank.x = 100
tank.y = 100

SHIFT = 5

objects = [tank, field]

def make_explosion(x, y):
    expl = Explosion(atlas, x, y)
    objects.append(expl)


running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                d, x, y = tank.direction, tank.x, tank.y
                tank_id += 1
                if tank_id >= len(Tank.Type):
                    tank_id = 0
                tank = Tank(atlas, Tank.Color.PLAIN, list(Tank.Type)[tank_id])
                tank.x, tank.y = x, y
                tank.direction = d
                objects[0] = tank

            elif event.key == K_ESCAPE:
                running = False
            elif event.key == K_f:
                make_explosion(*tank.center_point())

    keys = pygame.key.get_pressed()

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

    for obj in objects:
        obj.render(screen)

    pygame.draw.circle(screen, (255, 0, 255), tank.gun_point(), 5)

    pygame.display.flip()

pygame.quit()
