import sys
import pygame
import functools


import lambdooz


pygame.init()
screen = pygame.display.set_mode((800, 600))

clk = pygame.time.Clock()
fps = 60
model = lambdooz.models.Marathon(2 * fps, 10)
controller = lambdooz.controllers.Game(model)
view = lambdooz.views.Marathon(screen, model)

while True:
    clk.tick(fps)
    model.update()
    controller.update()
    view.update()
    pygame.display.flip()
