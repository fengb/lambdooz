from lambdooz import common


class TestCoord(object):
    def setup(self):
        self.x = 123
        self.y = 456
        self.coord = common.Coord(self.x, self.y)

    def test_accessors(self):
        assert self.coord.x == self.x
        assert self.coord.y == self.y

    def test_equality(self):
        assert self.coord == common.Coord(self.x, self.y)
        assert hash(self.coord) == hash(common.Coord(self.x, self.y))

    def test_inequality(self):
        assert self.coord != 0
        assert self.coord != (self.x, self.y)
        assert self.coord != common.Coord(self.x + 1, self.y)

    def test_add_subtract(self):
        x = 518
        y = -297
        coord = common.Coord(x, y)

        assert self.coord + coord == common.Coord(self.x + x, self.y + y)
        assert self.coord - coord == common.Coord(self.x - x, self.y - y)
        assert coord - self.coord == common.Coord(x - self.x, y - self.y)

    def test_multiply(self):
        s = 1.2

        assert self.coord * s == common.Coord(self.x * s, self.y * s)

    def test_negate(self):
        assert -self.coord == common.Coord(-self.x, -self.y)

    def test_transpose(self):
        assert self.coord.transpose() == common.Coord(self.y, self.x)

    def test_reflection(self):
        assert self.coord.reflect_x() == common.Coord(-self.x, self.y)
        assert self.coord.reflect_y() == common.Coord(self.x, -self.y)
