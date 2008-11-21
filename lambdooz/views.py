import pygame


from .common import Coord
from . import models
from .models import LEFT, RIGHT, UP, DOWN


def load(file_name):
    return pygame.image.load(file_name).convert_alpha()


def load_all(file_name):
    left_image = load(file_name)
    return {
        LEFT: left_image,
        RIGHT: pygame.transform.rotate(left_image, 180),
        UP: pygame.transform.rotate(left_image, 270),
        DOWN: pygame.transform.rotate(left_image, 90),
    }


class Game(object):
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model

        self.background = load('data/background.png')
        self.player_images = dict((type, load_all('data/player%s.png' % type))
                                      for type in models.PIECE_TYPES)
        self.piece_images = dict((type, load_all('data/piece%s.png' % type))
                                     for type in models.PIECE_TYPES)

    def update(self):
        self.screen.blit(self.background, (0, 0))
        for (piece, position, direction) in self.model:
            if isinstance(piece, models.Player):
                image = self.player_images[piece.type][direction]
            else:
                image = self.piece_images[piece.type][direction]
            position = (Coord(0, 11) + position.reflect_y()) * 50
            self.screen.blit(image, (position.x, position.y))
