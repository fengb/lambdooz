import functools
import pygame


class Game(object):
    def __init__(self, model):
        self.controllers = [Keyboard(model)]

    def update(self):
        for controller in self.controllers:
            controller.update()

        # Eat all the rest of the events
        pygame.event.get()


class Keyboard(object):
    def __init__(self, model):
        self._actions = {
            pygame.K_LEFT: functools.partial(model.move, 0, 'left'),
            pygame.K_RIGHT: functools.partial(model.move, 0, 'right'),
            pygame.K_UP: functools.partial(model.move, 0, 'up'),
            pygame.K_DOWN: functools.partial(model.move, 0, 'down'),
            pygame.K_SPACE: functools.partial(model.attack, 0),
        }

    def update(self):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key in self._actions:
                self._actions[event.key]()
