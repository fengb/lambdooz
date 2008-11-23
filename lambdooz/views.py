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


def render_text(text):
    font = pygame.font.SysFont('Courier New', 50, True)
    return font.render(text, 1, (255, 255, 255))


class Game(object):
    def __init__(self, surface):
        self.surface = surface

        self.background = load('data/background.png')
        self.piece_images = {}
        for type in models.PIECE_TYPES:
            for direction, image in load_all('data/player%s.png' % type).items():
                self.piece_images[True, type, direction] = image
            for direction, image in load_all('data/piece%s.png' % type).items():
                self.piece_images[False, type, direction] = image

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

    def update(self, model):
        self.surface.blit(self.background, (0, 0))
        for piece in model['pieces']:
            image = self.piece_images[piece['player'], piece['type'], piece['direction']]
            model_position = piece['position']
            position = (model_position[0] * 50, (11 - model_position[1]) * 50)
            self.surface.blit(image, position)

        self.draw_upper_left(render_text(str(model['score'])))
        self.draw_upper_right(render_text(str(model['quota'])))
        self.draw_lower_right(render_text(str(model['level'])))
