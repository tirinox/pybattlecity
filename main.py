import pygame
from pygame.locals import *
from game import Game
from config import *
from util import Direction


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_t:
                    game.switch_my_tank()
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    game.fire()

        keys = pygame.key.get_pressed()

        tank = game.tank
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            game.move_tank(Direction.UP)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            game.move_tank(Direction.DOWN)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game.move_tank(Direction.LEFT)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game.move_tank(Direction.RIGHT)
        else:
            game.complete_moving()

        screen.fill((128, 128, 128))

        game.render(screen)

        if DEBUG:
            pygame.draw.circle(screen, (0, 255, 255), game.tank.gun_point, 4, 1)
            # pygame.draw.rect(screen, (255, 255, 0), game.tank.bounding_rect, 1)
            # pygame.draw.circle(screen, (0, 0, 255), game.tank.center_point, 4, 1)

        pygame.display.flip()

    pygame.quit()
