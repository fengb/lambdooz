from py.test import raises

from lambdooz import models

class TestCoord(object):
    def setup_method(self, method):
        self.x = 123
        self.y = 456
        self.coord = models.Coord(self.x, self.y)

    def test_accessors(self):
        assert self.coord.x == self.x
        assert self.coord.y == self.y

    def test_equality(self):
        assert self.coord == models.Coord(self.x, self.y)
        assert hash(self.coord) == hash(models.Coord(self.x, self.y))

    def test_inequality(self):
        assert self.coord != 0
        assert self.coord != (self.x, self.y)
        assert self.coord != models.Coord(self.x + 1, self.y)

    def test_add_subtract(self):
        x = 518
        y = -297
        coord = models.Coord(x, y)

        assert self.coord + coord == models.Coord(self.x + x, self.y + y)
        assert self.coord - coord == models.Coord(self.x - x, self.y - y)
        assert coord - self.coord == models.Coord(x - self.x, y - self.y)

    def test_multiply(self):
        s = 1.2

        assert self.coord * s == models.Coord(self.x * s, self.y * s)

    def test_negate(self):
        assert -self.coord == models.Coord(-self.x, -self.y)

    def test_transpose(self):
        assert self.coord.transpose() == models.Coord(self.y, self.x)

    def test_reflection(self):
        assert self.coord.reflect_x() == models.Coord(-self.x, self.y)
        assert self.coord.reflect_y() == models.Coord(self.x, -self.y)

    def test_tuple(self):
        assert tuple(self.coord) == (self.x, self.y)


class TestPlayer(object):
    def setup_method(self, method):
        self.type = 'test type'
        self.player = models.Player(self.type)

    def test_attack_same_type_is_true(self):
        piece = models.Piece(self.type)
        assert self.player.attack(piece)

    def test_attack_different_type_is_false_and_swaps_types(self):
        type = 'not the same type'
        piece = models.Piece(type)
        assert not self.player.attack(piece)
        assert self.player.type == type
        assert piece.type == self.type


class TestLine(object):
    def setup_method(self, method):
        types = ['arthur', 'lancelot', 'galahad']
        max = 50
        self.special_type = 'bedivere'
        self.test_types = [str(x) for x in range(max)]
        self.line = models.Line(max, types)

    def test_fill(self):
        self.line.fill()
        assert len(self.line) == self.line.max

    def test_too_many_pieces_added(self):
        self.line.fill()
        raises(models.TooManyPieces, 'self.line.add()')

    def test_only_add_listed_types(self):
        self.line.fill()
        for piece in self.line:
            assert piece.type in self.line.types

    def test_add_new_types_to_front(self):
        for type in self.test_types:
            self.line.add(type)

        assert [piece.type for piece in self.line] == list(reversed(self.test_types))

    def test_add_previous(self):
        for type in self.test_types:
            line = models.Line(max, [None])
            line.add(type)
            assert [piece.type for piece in line] == [type]

            line.add()
            assert [piece.type for piece in line] == [type, type]

    def test_add_piece_if_no_previous(self):
        base_types = [None] * 100
        for type in self.test_types:
            line = models.Line(max, base_types + [type])
            line.add()
            assert [piece.type for piece in line] == [type]

    def test_intersect_returns_number_of_pieces_removed(self):
        self.line.fill()
        player = models.Player(self.line.types[0])

        assert self.line.intersect(player) + len(self.line) == self.line.max

    def test_intersect_only_removes_matching(self):
        self.line.fill()
        player = models.Player(self.special_type)

        assert self.line.intersect(player) == 0
        assert len(self.line) == self.line.max


class TestPlane(object):
    def setup_method(self, method):
        self.width = 5
        self.length = 50
        self.types = ['arthur', 'lancelot', 'galahad']
        self.plane = models.Plane(self.width, self.length, self.types)

        for x in range(self.length):
            self.plane.add()

    def test_add_in_order_y(self):
        plane = models.Plane(1, self.length, self.types)
        for last_y in range(self.length):
            plane.add()
            coords = set(coord for (piece, coord) in plane)
            for y in range(last_y + 1):
                assert models.Coord(0, y) in coords

    def test_add_to_all_x(self):
        x_values = set(coord.x for (piece, coord) in self.plane)
        for x in range(self.width):
            assert x in x_values

    def test_intersect_returns_number_of_pieces_removed(self):
        player = models.Player(self.types[0])

        remaining = len(self.plane)
        for line in range(self.width):
            removed = self.plane.intersect(line, player)
            assert removed + len(self.plane) == remaining
            remaining = len(self.plane)


class TestBoard(object):
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
    def setup_method(self, method):
        self.player_x = 2
        self.player_y = 2
        self.length_x = 2
        self.length_y = 2
        self.num_players = 1
        self.types = ['arthur', 'lancelot', 'galahad']
        self.board = models.Board(self.player_x, self.player_y,
                                  self.length_x, self.length_y,
                                  self.num_players, self.types)

    def test_offset_left(self):
        assert self.board.offset('left', models.Coord(0, 0)) == models.Coord(0, 2)
        assert self.board.offset('left', models.Coord(1, 0)) == models.Coord(0, 3)
        assert self.board.offset('left', models.Coord(0, 1)) == models.Coord(1, 2)
        assert self.board.offset('left', models.Coord(1, 1)) == models.Coord(1, 3)

    def test_offset_right(self):
        assert self.board.offset('right', models.Coord(0, 0)) == models.Coord(5, 2)
        assert self.board.offset('right', models.Coord(1, 0)) == models.Coord(5, 3)
        assert self.board.offset('right', models.Coord(0, 1)) == models.Coord(4, 2)
        assert self.board.offset('right', models.Coord(1, 1)) == models.Coord(4, 3)

    def test_offset_up(self):
        assert self.board.offset('up', models.Coord(0, 0)) == models.Coord(2, 5)
        assert self.board.offset('up', models.Coord(1, 0)) == models.Coord(3, 5)
        assert self.board.offset('up', models.Coord(0, 1)) == models.Coord(2, 4)
        assert self.board.offset('up', models.Coord(1, 1)) == models.Coord(3, 4)

    def test_offset_down(self):
        assert self.board.offset('down', models.Coord(0, 0)) == models.Coord(2, 0)
        assert self.board.offset('down', models.Coord(1, 0)) == models.Coord(3, 0)
        assert self.board.offset('down', models.Coord(0, 1)) == models.Coord(2, 1)
        assert self.board.offset('down', models.Coord(1, 1)) == models.Coord(3, 1)
