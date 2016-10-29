# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Independent functions/classes for use with track calculations

import math


class Verbose(object):
    """ Used to print calculation data if the verbose parameter is
        specified, but by default it does not.
    """
    verbose = False
    counter = 0

    @classmethod
    def __init__(cls, *args, **kwargs):
        if cls.verbose:
            c = '{:3d}'.format(cls.counter) if cls.counter > 0 else ''
            print(c, *args, **kwargs)
            cls.counter += 1

    @classmethod
    def reset(cls):
        cls.counter = 1


def transform(a, r, b=(0, 0), c=None):
    """ Rotates a point a = (x, y) around axis b = (x0, y0) by r clockwise
        and translates by c = (x1, y1) such that b = c.
        a, b, c are all tuples.
        r can be either Bearing object or an int/float in radians.
        By default: b = c = (0, 0), the origin.
        Used with the curve methods.
    """
    x, y = range(2)
    try:
        t = r.rad
    except AttributeError:
        t = r
    if c is None:
        c = b
    try:
        new_x = c[x] + (a[x] - b[x]) * math.cos(t) + (a[y] - b[y]) * math.sin(t)
        new_y = c[y] - (a[x] - b[x]) * math.sin(t) + (a[y] - b[y]) * math.cos(t)
    except AttributeError:
        raise AttributeError("a, b, c must be tuples of length 2.")
    return new_x, new_y


class Bearing(object):
    """ Defines the bearing as rotation clockwise from the North (+ve y axis in
        Cartesian coordinates). Calculations are in radians.
    """

    def __init__(self, angle, rad=False):
        self._rad = None
        try:
            if rad:
                self.rad = float(angle)
            else:
                self.deg = float(angle)

        except (TypeError, ValueError) as err:
            raise ValueError("The bearing needs to be either integer or"
                             "float.", err)

    @property
    def deg(self):
        """ Sets bearing in degrees"""
        return math.degrees(self._rad)

    @deg.setter
    def deg(self, value):
        self._rad = math.radians(value % 360)

    @property
    def rad(self):
        """ Sets bearing in radians"""
        return self._rad

    @rad.setter
    def rad(self, value):
        self._rad = value % (2*math.pi)

    def __str__(self):
        return "Bearing {0} degrees / {1} radians".format(self.deg, self.rad)

    def __repr__(self):
        return str(self._rad)

    def __neg__(self):
        return Bearing(2*math.pi - self.rad, rad=True)

    def __add__(self, other):
        try:
            return Bearing(self.rad+other.rad, rad=True)
        except AttributeError:
            return Bearing(self.rad+other, rad=True)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return Bearing(self.rad-other.rad, rad=True)
        except AttributeError:
            return Bearing(self.rad-other, rad=True)

    def __rsub__(self, other):
        return - self.__sub__(other)

    def __eq__(self, other):
        try:
            return self.rad == other.rad
        except AttributeError:
            return self.rad == other

    def __ne__(self, other):
        try:
            return self.rad != other.rad
        except AttributeError:
            return self.rad != other

    def __abs__(self):
        """ Treats bearing as if it's negative if > math.pi and returns
            Bearing object with absolute value."""
        abs_rad = 2*math.pi - self.rad if self.rad > math.pi else self.rad
        return Bearing(abs_rad, rad=True)

    def flip(self):
        """ Returns Bearing object with bearing pointing in opposite direction,
            eg 30 -> 210, 120 -> 300, 270 -> 90, etc.
        """
        return Bearing(self.rad + math.pi, rad=True)

    def nearly_equal(self, other, places=7, flip=False):
        """ Checks if the two Bearing objects are almost equal, as errors can
            creep into conversion calculations. Default of 5 decimal places.
            If flip: tests both original and flipped bearing of other.
        """
        try:
            org_value = other.rad
            flip_value = other.flip().rad if flip else None
        except AttributeError:
            org_value = other
            flip_value = (math.pi + other) % (2*math.pi)

        if self.rad == org_value or self.rad == flip_value:
            return True
        else:
            vl = [i for i in [org_value, flip_value] if i is not None]
            return any(round(self.rad-j, places) == 0 for j in vl)


class LinearEquation(object):
    """ Defines a linear equation in Cartesian coordinates, as well as finding
        the distance between the line and a point, and finding the intersect
        between two lines.
    """

    def __init__(self, bearing, point):
        try:
            self.b = bearing.rad
            self.u, self.v = point
        except AttributeError as err:
            raise AttributeError('bearing must be a Bearing object.') from err
        except TypeError as err:
            raise TypeError('point must be a tuple of length 2.') from err

    def x(self, y):
        """ Returns x value of line given y. """
        return (self.u*math.cos(self.b)
                + (y - self.v)*math.sin(self.b)) / math.cos(self.b)

    def y(self, x):
        """ Returns y value of line given x. """
        return (self.v*math.sin(self.b)
                + (x - self.u)*math.cos(self.b)) / math.sin(self.b)

    def dist(self, p, absolute=True):
        """ Shortest distance between point p = (x,y) and the line. """
        result = (p[0]-self.u)*math.cos(self.b) - \
                 (p[1]-self.v)*math.sin(self.b)
        return abs(result) if absolute else result

    def same_side(self, p1, p2):
        """ Checks if both points p1 and p2 are on the same side of the
            line in Cartesian coordinates. Returns True if so, False
            otherwise. If either or both of the points are on the line
            (ie dist = 0) then returns True.
        """
        d1, d2 = self.dist(p1, False), self.dist(p2, False)
        if d1 == 0 or d2 == 0:
            return True
        else:
            return bool(d1 > 0) == bool(d2 > 0)

    def intersect(self, other):
        """ Finds the point at where the two lines intersect."""
        try:
            if self.b == other.b or self.b == (other.b+math.pi) % (2*math.pi):
                raise ValueError("The two lines cannot be parallel.")
        except AttributeError as err:
            raise AttributeError("'other' must also be a LinearEquation "
                                 "object.") from err

        def math_cot(t): return 1 / math.tan(t)

        u1, v1, b1 = self.u, self.v, self.b
        u2, v2, b2 = other.u, other.v, other.b

        # Can't use cot and tan at specific angles, so cover with alternative formulae
        if b1 % (math.pi/2) == 0 and b2 % (math.pi/2) == 0:
            # Since can't be parallel, must be perpendicular; can just use coords
            x, y = (u1, v2) if b1 in [0, math.pi] else (u2, v1)
        else:
            try:
                x = (u1*math_cot(b1) - u2*math_cot(b2) + v2 - v1) \
                    / (math_cot(b1) - math_cot(b2))
            except ZeroDivisionError:
                x = (u2*math.tan(b1) + u1*math.tan(b2)
                     + (v1-v2)*math.tan(b1)*math.tan(b2)) \
                    / (math.tan(b2) - math.tan(b1))
            try:
                y = (v1*math.tan(b1) - v2*math.tan(b2) + u2 - u1) \
                    / (math.tan(b1) - math.tan(b2))
            except ZeroDivisionError:
                y = (v2*math_cot(b1) + v1*math_cot(b2)
                     + (u1-u2)*math_cot(b1)*math_cot(b2)) \
                    / (math_cot(b2) - math_cot(b1))

        return x, y

    def __str__(self):
        return 'LinearEquation at coordinates ({0}, {1}) with bearing {2}'.format(self.u, self.v, self.b)
