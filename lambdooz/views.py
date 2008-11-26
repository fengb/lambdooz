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
    font = pygame.font.Font('data/ocr_a.ttf', 40)
    return font.render(text, 1, (255, 255, 255))


class Game(object):
    def __init__(self, surface, model):
        self.surface = surface
        self.model = model

        self.background = load('data/background.png')
        self._piece_images = {}

    def piece(self, name, direction):
        if not name in self._piece_images:
            self._piece_images[name] = load_all('data/%s.png' % name)
        return self._piece_images[name][direction]

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
            image = self.piece(type, direction)
            position = (position[0] * 50, (11 - position[1]) * 50)
            self.surface.blit(image, position)


class Marathon(Game):
    def update(self):
        self.surface.blit(self.background, (0, 0))

        self.draw_pieces(self.model.pieces)
        self.draw_upper_left(render_text('%010d' % self.model.score))
        self.draw_upper_right(render_text(str(self.model.quota)))
        self.draw_lower_right(render_text(str(self.model.level)))
