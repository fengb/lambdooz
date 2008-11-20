from __future__ import with_statement

import random
import itertools
import os

from .common import Coord


LEFT = Coord(-1, 0)
RIGHT = Coord(1, 0)
UP = Coord(0, 1)
DOWN = Coord(0, -1)


class TooManyPieces(Exception):
    """Too many pieces have been added."""
class GameOver(Exception):
    """Game over, man! Game over!"""


PIECE_TYPES = ['norm1', 'norm2', 'norm3', 'norm4']


class Piece(object):
    """Piece on the game board."""
    def __init__(self, type):
        self.type = type


class Player(Piece):
    """Special type of Piece."""
    def __init__(self, type):
        self.type = type

    def attack(self, piece):
        if self.type == piece.type:
            return True
        else:
            self.type, piece.type = piece.type, self.type
            return False


class Line(object):
    """As piece generation is weighted per line, easiest representation is
    to have a new object per line.
    """
    def __init__(self, max, types):
        self._pieces = []
        self._max = max
        self._types = types

        # None type means use last type so set last type to something valid
        self._previous = random.choice([t for t in self._types])

    def __len__(self):
        return len(self._pieces)

    def __iter__(self):
        return iter(self._pieces)

    def add(self):
        if len(self) >= self._max:
            raise TooManyPieces

        # Chooses last type if random returns None
        self._previous = random.choice(self._types) or self._previous
        piece = Piece(self._previous)
        self._pieces.append(piece)
        return piece

    def intersect(self, player):
        removed = 0
        while self._pieces and player.attack(self._pieces[-1]):
            self._pieces.pop()
            removed += 1
        return removed


class Plane(object):
    """
    +-------+-------+
    | (0,2) X (1,2) |
    +-------X-------+
    | (0,1) X (1,1) | length
    +-------X-------+
    | (0,0) X (1,0) |
    +XXXXXXXXXXXXXXX+
          width
    """
    def __init__(self, width, length, types):
        """
        width - number of lines
        length - max pieces per line
        """
        self._lines = [Line(length, types) for x in range(width)]

    def __len__(self):
        return sum(len(line) for line in self._lines)

    def __iter__(self):
        for x, line in enumerate(self._lines):
            for y, piece in enumerate(line):
                yield Coord(x, y), piece

    def add(self):
        random.choice(self._lines).add()

    def intersect(self, num, player):
        return self._lines[num].intersect(player)


class Board(object):
    """
    External coordinates:
    +-------+-------+            +-------+-------+            +-------+-------+
    | (0,5) | (1,5) |            | (2,5) | (3,5) |            | (4,5) | (5,5) |
    +-------+-------+            +-------+-------+ length_y   +-------+-------+
    | (0,4) | (1,4) |            | (2,4) | (3,4) |            | (4,4) | (5,4) |
    +-------+-------+            +-------+-------+            +-------+-------+


    +-------+-------+            +-------+-------+            +-------+-------+
    | (0,3) | (1,3) |            | (2,3) | (3,3) |            | (4,3) | (5,3) |
    +-------+-------+            +-------+-------+ player_y   +-------+-------+
    | (0,2) | (1,2) |            | (2,2) | (3,2) |            | (4,2) | (5,2) |
    +-------+-------+            +-------+-------+            +-------+-------+
         length_x                     player_x

    +-------+-------+            +-------+-------+            +-------+-------+
    | (0,1) | (1,1) |            | (2,1) | (3,1) |            | (4,1) | (5,1) |
    +-------+-------+            +-------+-------+            +-------+-------+
    | (0,0) | (1,0) |            | (2,0) | (3,0) |            | (4,0) | (5,0) |
    +-------+-------+            +-------+-------+            +-------+-------+


    Internal coordinates:
                                 +XXXXXXXXXXXXXXX+
                                 | (0,0) X (1,0) |
                                 +-------X-------+ length_y
                                 | (0,1) X (1,1) |
                                 +-------+-------+


    +-------+-------+            +-------+-------+            +-------+-------+
    X (1,0) | (1,1) |            | (0,1) | (1,1) |            | (1,1) | (1,0) X
    XXXXXXXXXXXXXXXX+            +-------+-------+ player_y   +XXXXXXXXXXXXXXXX
    X (0,0) | (0,1) |            | (0,0) | (1,0) |            | (0,1) | (0,0) X
    +-------+-------+            +-------+-------+            +-------+-------+
         length_x                    player_x

                                 +-------+-------+
                                 | (0,1) X (1,1) |
                                 +-------X-------+
                                 | (0,0) X (1,0) |
                                 +XXXXXXXXXXXXXXX+
    """
    def __init__(self, player_x, player_y, length_x, length_y, num_players, types):
        self._players = []
        self._player_positions = []
        self._player_directions = []

        self._player_max = Coord(player_x, player_y)
        self._player_origin_offset = Coord(length_x, length_y)
        self._length_x = length_x
        self._length_y = length_y
        self._player_x = player_x
        self._player_y = player_y

        self._planes = {
            LEFT: Plane(player_y, length_x, types),
            RIGHT: Plane(player_y, length_x, types),
            UP: Plane(player_x, length_y, types),
            DOWN: Plane(player_x, length_y, types),
        }

        self._next = random.choice(types)

    def _left_offset(self, internal_position):
        return internal_position.transpose() + Coord(0, self._length_y)

    def _right_offset(self, internal_position):
        return internal_position.transpose().reflect_x() + Coord(2*self._length_x + self._player_x - 1, self._length_y)

    def _up_offset(self, internal_position):
        return internal_position.reflect_y() + Coord(self._length_x, 2*self._length_y + self._player_y - 1)

    def _down_offset(self, internal_position):
        return internal_position + Coord(self._length_x, 0)

    def offset(self, direction, internal_position):
        offset_funcs = {
            LEFT: self._left_offset,
            RIGHT: self._right_offset,
            UP: self._up_offset,
            DOWN: self._down_offset,
        }
        return offset_funcs[direction](internal_position)

    def __len__(self):
        return sum(len(plane) for plane in self._planes)

    def __iter__(self):
        for int_pos, direction, player in zip(self._player_positions,
                                        self._player_directions,
                                        self._players):
            ext_pos = int_pos + self._player_origin_offset
            yield ext_pos, direction, player

        for direction in self._planes:
            for int_pos, piece in self._planes[direction]:
                ext_pos = self.offset(direction, int_pos)
                yield ext_pos, direction, piece

    def add(self):
        self._next.add()
        self._next = random.choice([type for type in self._types if type != self._next])

    def move(self, player_num, direction):
        try:
            position = self._player_positions[num]
            direction = self._player_directions[num]
        except IndexError:
            raise PlayerNotFound(num)
        target = position + direction

        if self.inside_player_area(target):
            self._positions[number] = target
            return True
        else:
            return False

    def inside_player_area(self, position):
        return position.x >= 0 and position.x < self._player_max.x and \
               position.y >= 0 and position.y < self._player_max.y

    def attack(self, num):
        player = self._players[num]
        position = self._player_positions[num]
        direction = self._player_directions[num]

        plane = self._planes[direction]
        self._player_directions[num] *= -1

        # Direction should have either X or Y but not both
        if direction.x:
            return plane.intersect(position.x, player)
        else:
            return plane.intersect(position.y, player)


class Game(object):
    def __init__(self, lines_per_plane, width, height):
        self.width = width
        self.height = height
        self.horizontal = self.width / 2
        self.vertical = self.height / 2
        self._board = Plane.as_board(lines_per_plane, self.horizontal, self.vertical)
        self._player = Player(Coord(self.horizontal, self.vertical))
        self.score = 0

    def attack(self):
        self._board.attack()


class Marathon(Game):
    small_bonus = 5000
    large_bonus = 10000

    def __init__(self, *args, **kwargs):
        Game.__init__(self, *args, **kwargs)
        self.level = 1
        self.clears = 0
        self.quota = 0
        self._set_quota()
        self._set_timeleft()

    def _set_quota(self):
        self.quota += self.level * 10

    def _set_timeleft(self):
        self._timeleft = 100 - self.level * 10


'''
class HighScore(object):
    def __init__(self, file_name=os.path.expanduser('~/.lambdooz_score')):
        self.file_name = file_name

    def __getitem__(self, game_name):
        self.load()
        return self._data[game_name]

    def _set_defaults(self):
        self._data = {}
        for game_name in GAME_TYPES:
            self._data[game_name] = [['0', 'None'] for x in range(5)]

    def _sort(self):
        for game_name in GAME_TYPES:
            self._sort_game(game_name)

    def _sort_game(self, game_name):
        def first_element(list):
            return list[0]
        self._data[game_name].sort(key=first_element, reverse=True)

    def load(self):
        """Most methods should call this. The slight performance hit is worth
        the more accurate data.
        """
        try:
            with open(self.file_name, 'r') as file:
                self._data = yaml.safe_load(file)
            self._sort()
        except Exception:
            if not hasattr(self, '_data'):
                self._set_defaults()
                self._sort()

    def save(self):
        with open(self.file_name, 'w') as file:
            yaml.safe_dump(self._data, file)

    def append(self, game_name, score):
        self.load()
        self._data[game_name].append(score)
        self._sort_game(game_name)
        self._data[game_name].pop()
        self.save()
'''
