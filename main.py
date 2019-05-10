import pygame
from pygame.locals import *
import spritesheet
import field
from tank import Tank

pygame.init()
screen = pygame.display.set_mode((640, 480))

atlas = spritesheet.SpriteSheet('atlas.png', upsample=2, sprite_size=8)
field = field.Field(atlas)

tank_id = 5
tank = Tank(atlas, Tank.Color.PURPLE, Tank.Type.ALL[tank_id])
tank.x = 100
tank.y = 100

SHIFT = 5

running = 1

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0
        elif event.type == KEYDOWN and event.key == K_SPACE:
            d, x, y = tank.direction, tank.x, tank.y
            tank_id += 1
            if tank_id >= len(Tank.Type.ALL):
                tank_id = 0
            tank = Tank(atlas, Tank.Color.PLAIN, Tank.Type.ALL[tank_id])
            tank.x, tank.y = x, y
            tank.direction = d


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

    field.render(screen)
    tank.render(screen)

    pygame.draw.circle(screen, (255, 0, 255), tank.gun_point(), 5)

    pygame.display.flip()

pygame.quit()
