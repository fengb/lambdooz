import os

import pygame

from .mvc import observer


from . import models


class Image(object):
    def __init__(self, file_name):
        self.raw = pygame.image.load(file_name).convert_alpha()
        self._rotations = {}

    @classmethod
    def from_directory(cls, dir_name):
        images = {}
        for file_name in os.listdir(dir_name):
            if file_name.endswith('.png'):
                images[file_name.rstrip('.png')] = cls('%s/%s' % (dir_name, file_name))
        return images

    def rotate(self, degrees):
        if degrees not in self._rotations:
            self._rotations[degrees] = pygame.transform.rotate(self.raw, degrees)
        return self._rotations[degrees]

    @property
    def left(self):
        return self.raw

    @property
    def right(self):
        return self.rotate(180)

    @property
    def up(self):
        return self.rotate(270)

    @property
    def down(self):
        return self.rotate(90)


class Game(object):
    @observer
    def __init__(self, model, surface):
        self.model = model
        self.surface = surface

        self._images = Image.from_directory('data')
        self._font = pygame.font.Font('data/ocr_a.ttf', 40)

        self.update()

    def render_text(self, text):
        return self._font.render(str(text), 1, (255, 255, 255))

    def draw_upper_left(self, surface):
        x, y = self.surface.get_rect().topleft
        self.surface.blit(surface, (x, y))

    def draw_lower_left(self, surface):
        h = surface.get_rect().h
        x, y = self.surface.get_rect().bottomleft
        self.surface.blit(surface, (x, y - h))

    def draw_upper_right(self, surface):
        w = surface.get_rect().w
        x, y = self.surface.get_rect().topright
        self.surface.blit(surface, (x - w, y))

    def draw_lower_right(self, surface):
        w, h = surface.get_rect().size
        x, y = self.surface.get_rect().bottomright
        self.surface.blit(surface, (x - w, y - h))

    def draw_pieces(self, pieces):
        for id, type, position, direction in pieces:
            image = getattr(self._images[type], direction)
            position = (position[0] * 50, (11 - position[1]) * 50)
            self.surface.blit(image, position)

    def synchronize(self, duration):
        pass


class Marathon(Game):
    def update(self):
        self.surface.blit(self._images['background'].raw, (0, 0))

        self.draw_pieces(self.model.pieces)
        self.draw_upper_left(self.render_text('%010d' % self.model.score))
        self.draw_upper_right(self.render_text(self.model.quota))
        self.draw_lower_right(self.render_text(self.model.level))


class Timed(Game):
    def update(self):
        self.surface.blit(self._images['background'].raw, (0, 0))

        self.draw_pieces(self.model.pieces)
        self.draw_upper_left(self.render_text('%010d' % self.model.score))
        self.draw_lower_right(self.render_text(self.model.time_left))
