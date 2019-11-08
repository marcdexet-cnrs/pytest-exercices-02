from math import cos, sin, acos, asin, sqrt, isclose, fabs, pi

""""
Module for simple geometry in 2D
"""


class Point:
    def __init__(self, x, y=None):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def new(cls, xy):
        return Point(xy[0], xy[1])

    def normal(self):
        return Point(-self.y, self.x)

    def reverse(self):
        return Point(-self.x, -self.y)

    def normalize(self, d=0):
        if d == 0:
            d = sqrt(self.x * self.x + self.y * self.y)
        return Point(self.x / d, self.y / d)

    def scalar_product(self, other: 'Point'):
        return self.x * other.x + self.y * other.y

    def is_orthogonal(self, other: 'Point'):
        product = self.scalar_product(other)
        return isclose(product, 0)

    def is_collinear(self, other: 'Point'):
        return self.is_orthogonal(other.normal())

    def __add__(self, other: 'Point'):
        r = NotImplemented
        if isinstance(other, Point):
            r = Point(self.x + other.x, self.y + other.y)
        return r

    def __sub__(self, other: 'Point'):
        r = NotImplemented
        if isinstance(other, Point):
            r = Point(self.x - +other.x, self.y - other.y)
        return r

    def __mul__(self, other):
        r = NotImplemented
        if isinstance(other, float) or isinstance(other, int):
            factor = float(other)
            r = Point(self.x * factor, self.y * factor)
        return r

    def __eq__(self, other: 'Point'):
        r = NotImplemented
        if isinstance(other, tuple):
            other = Point.new(other)
        if isinstance(other, Point):
            r = isclose(self.x, other.x, abs_tol=1e-9) and isclose(self.y, other.y, abs_tol=1e-9)
        return r

    def __repr__(self):
        return f'p({self.x}, {self.y})'

    @staticmethod
    def distance(a: 'Point', b: 'Point') -> float:
        dx = a.x - b.x
        dy = a.y - b.y
        return sqrt(dx * dx + dy * dy)


class Segment:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Line:
    def __init__(self, point: Point, vector: Point):
        self.point = point
        self.vector = vector.normalize()

    def contains(self, point: Point):
        a = self.point
        b = point
        v_ab = Point(a.x - b.x, a.y - b.y)
        return v_ab.is_collinear(self.vector)

    def intersection(self, line: 'Line'):
        v0 = self.vector
        p0 = self.point

        v1 = line.vector
        p1 = line.point

        v1_v0 = v1.scalar_product(v0)

        dp = p1 - p0

        dp_vo = dp.scalar_product(v0)
        dp_v1 = dp.scalar_product(v1)

        if isclose(fabs(v1_v0), 1.):
            raise ValueError('Lines are parallel')
        else:
            coef0 = (dp_vo - dp_v1 * v1_v0) / (1 - v1_v0 * v1_v0)

        return v0 * coef0 + p0

    def __repr__(self):
        return f'line({self.point}, {self.vector})'


class Arc:
    def __init__(self, start: Point, end: Point, start_tangent: Point, end_tangent: Point = None):
        self.start = start
        self.end = end
        if end_tangent is None:
            end_tangent = Geometry.get_symmetrical(start_tangent, (start - end))

        self.center = Arc.compute_center(start, end, start_tangent, end_tangent)
        self.radius = Point.distance(self.center, self.start)
        distance = Point.distance(start, end)
        self.angle = 2 * asin(distance / (2 * self.radius)) if distance else acos(
            start_tangent.scalar_product(end_tangent))
        self.length = self.angle * pi * self.radius

    @classmethod
    def compute_center(cls, start, end, start_tangent, end_tangent):
        if not end_tangent:
            return Arc.compute_center_from_start_tangent(start, end, start_tangent)
        else:
            return Arc.compute_center_from_both_tangents(start, end, start_tangent, end_tangent)

    @staticmethod
    def compute_center_from_start_tangent(start, end, tangent):
        chord = end - start
        c = Point((end.x + start.x) / 2, (end.y + start.y) / 2)
        try:
            center = Arc.compute_intersection_with_each_tangent(start, c, tangent, chord)
        except ValueError:
            center = c
        return center

    @staticmethod
    def compute_center_from_both_tangents(p0, p1, tangent_p0, tangent_p1):
        try:
            center = Arc.compute_intersection_with_each_tangent(p0, p1, tangent_p0, tangent_p1)
        except ValueError:
            center = Point((p1.x + p0.x) / 2, (p1.y + p0.y) / 2)
        return center

    @staticmethod
    def compute_intersection_with_each_tangent(p0, p1, tangent_p0, tangent_p1):
        """
        Computes center from both tangents, from the fist point and the second point.
        :param p0: Point the first point of the Arc
        :param p1: Point  the second point of the Arc
        :param tangent_p0: Point the tangent vector of first point of the Arc
        :param tangent_p1: Point the tangent vector of 2nd point of the Arc
        :return: intersection of normal lines to vectors, aka the center
        """
        radial_p0 = tangent_p0.normal()
        radial_p1 = tangent_p1.normal()
        line_p0 = Line(p0, radial_p0)
        line_p1 = Line(p1, radial_p1)
        return line_p0.intersection(line_p1)

    @staticmethod
    def find_angle_and_chord_vector(start, end, tangent):
        a = start
        b = end
        v = tangent

        distance = Point.distance(a, b)
        u = Point(b.x - a.x, b.y - a.y)
        u = u.normalize(distance)
        v = v.normalize()
        angle = acos(u.scalar_product(v))
        sign = u.x * v.y + u.y * v.x
        angle = 2 * angle * sign

        return angle, u, distance


class Geometry:

    @staticmethod
    def rotate_from_axe(vector, axe):
        axe = axe.normalize()
        cos_ = axe.x
        sin_ = -axe.y
        x = vector.x * cos_ - vector.y * sin_
        y = vector.x * sin_ + vector.y * cos_
        return Point(x, y)

    @staticmethod
    def get_symmetrical(vector, axe):
        symmetrical = Geometry.rotate_from_axe(vector, axe)
        symmetrical = Point(symmetrical.x, -symmetrical.y)
        return Geometry.rotate_from_axe(symmetrical, Point(axe.x, - axe.y))
