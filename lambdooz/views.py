import pygame


from . import models


def load(file_name):
    return pygame.image.load(file_name).convert_alpha()


def load_all(file_name):
    left_image = load(file_name)
    return {
        'left': left_image,
        'right': pygame.transform.rotate(left_image, 180),
        'up': pygame.transform.rotate(left_image, 270),
        'down': pygame.transform.rotate(left_image, 90),
    }


class Game(object):
    def __init__(self, screen):
        self.screen = screen

        self.background = load('data/background.png')
        self.piece_images = {}
        for type in models.PIECE_TYPES:
            for direction, image in load_all('data/player%s.png' % type).items():
                self.piece_images[True, type, direction] = image
            for direction, image in load_all('data/piece%s.png' % type).items():
                self.piece_images[False, type, direction] = image

    def update(self, model):
        self.screen.blit(self.background, (0, 0))
        for piece in model:
            image = self.piece_images[piece['player'], piece['type'], piece['direction']]
            model_position = piece['position']
            position = (model_position[0] * 50, (11 - model_position[1]) * 50)
            self.screen.blit(image, position)
