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

        # None type means use last type so set next type to something valid
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
                yield piece, Coord(x, y)

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
    # TODO: Rename self._planes to something less confusing
    # TODO: Consolidate variables
    def __init__(self, player_x, player_y, length_x, length_y, num_players, types):
        self._players = [Player(types[0])]
        self._player_positions = [Coord(0, 0)]
        self._player_directions = [LEFT]

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

        self._next = random.choice(self._planes.values())

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
        for player, int_pos, direction in zip(self._players,
                                              self._player_positions,
                                              self._player_directions):
            ext_pos = int_pos + self._player_origin_offset
            yield player, ext_pos, direction

        for direction in self._planes:
            for piece, int_pos in self._planes[direction]:
                ext_pos = self.offset(direction, int_pos)
                yield piece, ext_pos, direction

    def add(self):
        self._next.add()
        self._next = random.choice([plane for plane in self._planes.values() if plane != self._next])

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
    def __init__(self):
        self.score = 0
        self._board = Board(4, 4,
                            6, 4,
                            1, PIECE_TYPES)

    def __iter__(self):
        return iter(self._board)

    def move(self, *args, **kwargs):
        self._board(*args, **kwargs)


class Marathon(Game):
    small_bonus = 5000
    large_bonus = 10000


    def __init__(self, *args, **kwargs):
        Game.__init__(self, *args, **kwargs)
        self.level = 1
        self.clears = 0
        self.quota = 0
        self._update_quota()
        self._next_piece = self._delay

    def attack(self):
        pieces = self._board.attack()
        self.score += pieces * 100
        self.quota -= pieces

        if self.quota <= 0:
            self._update_quota(self)

    def update(self):
        if self._next_piece <= 0:
            try:
                self._board.add()
            except TooManyPieces:
                raise GameOver
            self._next_piece = self._delay
        else:
            self._next_piece -= 1

    @property
    def _delay(self):
        return 20 - self.level

    def _update_quota(self):
        self.quota += self.level * 10
