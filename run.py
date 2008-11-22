import sys
import pygame


import lambdooz


pygame.init()
screen = pygame.display.set_mode((800, 600))

clk = pygame.time.Clock()
fps = 60
model = lambdooz.models.Marathon(2 * fps, 10)
view = lambdooz.views.Game(screen)

while True:
    clk.tick(fps)
    model.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_LEFT:
                model.move(0, 'left')
            elif event.key == pygame.K_RIGHT:
                model.move(0, 'right')
            elif event.key == pygame.K_UP:
                model.move(0, 'up')
            elif event.key == pygame.K_DOWN:
                model.move(0, 'down')
            elif event.key == pygame.K_SPACE:
                model.attack(0)

    view.update(model.raw())
    pygame.display.flip()
