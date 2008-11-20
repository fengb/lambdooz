class Coord(object):
    def __init__(self, x, y):
        self._comp = complex(x, y)

    def __repr__(self):
        return 'Coord(%d, %d)' % (self._comp.real, self._comp.imag)

    def __str__(self):
        return '(%d, %d)' % (self._comp.real, self._comp.imag)

    def __hash__(self):
        return hash(self._comp)

    def __eq__(self, other):
        try:
            return self._comp == other._comp
        except Exception:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        result = self._comp + other._comp
        return Coord(result.real, result.imag)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        result = self._comp * other
        return Coord(result.real, result.imag)

    def __neg__(self):
        return self * -1

    @property
    def x(self):
        return self._comp.real

    @property
    def y(self):
        return self._comp.imag

    def transpose(self):
        return Coord(self._comp.imag, self._comp.real)

    def reflect_x(self):
        return Coord(-self._comp.real, self._comp.imag)

    def reflect_y(self):
        return Coord(self._comp.real, -self._comp.imag)
