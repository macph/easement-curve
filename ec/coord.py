# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Track coordinates

from enum import Enum
import math

from ec.common import Bearing


class Q(Enum):
    NONE, NE, SE, SW, NW = range(5)


class CoordError(Exception):
    pass


class TrackCoord(object):
    """ Contains the coordinates and curvature of a point on a track. Used to
        carry information between curve sections.
        org_curvature and org_length are used to store info about length of
        track beforehand.
    """

    def __init__(self, pos_x, pos_z, rotation, quad, curvature=None,
                 org_curvature=None, org_length=None, org_type=None):
        # Properties only
        self._bearing = None
        self._curvature = None
        self._org_curvature = None

        # Setting instance variables
        self.pos_x = pos_x
        self.pos_z = pos_z
        self.curvature = curvature
        self.org_length = org_length
        self.org_curvature = org_curvature
        self.org_type = org_type

        # Check if position values are valid
        try:
            math.sqrt(self.pos_x ** 2 + self.pos_z ** 2)
        except TypeError as err:
            raise CoordError('Position values must be int/floats.', err)

        # Converting y-axis rotation and quadrant to bearing
        if quad in [Q.NE, Q.SE, Q.SW, Q.NW]:
            self.quad = (rotation, quad)
        elif quad == Q.NONE:
            self.bearing = rotation
        else:
            raise CoordError('quad argument must either be a compass '
                             'quadrant or none.')

    @property
    def bearing(self):
        return self._bearing

    @bearing.setter
    def bearing(self, value):
        # Check if value is already a Bearing object
        try:
            value.rad
        except AttributeError:
            self._bearing = Bearing(value, rad=True)
        else:
            self._bearing = value

    @property
    def quad(self):
        bearing = self._bearing.deg
        quadrants = {
            0: (bearing, Q.NE.name),
            90: (180 - bearing, Q.SE.name),
            180: (bearing - 180, Q.SW.name),
            270: (360 - bearing, Q.NW.name)
        }

        for r in quadrants.keys():
            if r <= bearing < r + 90:
                return quadrants[r]
        else:
            # Just in case bearing was 360 and escaped the above dict
            if round(bearing) == 360:
                return quadrants[0]
            # Otherwise, raises error
            raise ValueError(
                'Bearing: {} is not within [0, 360) / [0, 2pi).'
                ''.format(repr(bearing)))

    @quad.setter
    def quad(self, value):
        try:
            rotation, quad = value
        except ValueError as err:
            raise ValueError('The quad property requires two values: '
                             'rotation and quadrant.') from err

        quadrants = {
            Q.NE: abs(rotation),
            Q.SE: 180 - abs(rotation),
            Q.SW: 180 + abs(rotation),
            Q.NW: 360 - abs(rotation)
        }

        try:
            if abs(rotation) <= 90:
                self._bearing = Bearing(quadrants[quad])
            else:
                raise CoordError('The y-axis rotation must be in the range '
                                 '[-90, 90].')

        except KeyError:
            raise CoordError('{!r} is not a valid quadrant.'.format(quad))

        except TypeError as err:
            raise CoordError(
                '{0:!r} is not a valid number for the rotation variable.'
                ''.format(rotation), err)

    @staticmethod
    def get_radius_clockwise(stored_variable):
        if stored_variable < 0:
            return 1 / abs(stored_variable), 'CW'
        elif stored_variable > 0:
            return 1 / abs(stored_variable), 'ACW'
        else:
            return 0, 'straight'

    @staticmethod
    def set_radius_clockwise(var, stored_var):
        raise AttributeError('Property {0} cannot be set on its own. Use the '
                             '{1} property.'.format(var, stored_var))

    @property
    def curvature(self):
        return self._curvature

    @curvature.setter
    def curvature(self, value):
        self._curvature = value

    @property
    def radius(self):
        return self.get_radius_clockwise(self._curvature)[0]

    @radius.setter
    def radius(self):
        self.set_radius_clockwise('radius', 'curvature')

    @property
    def clockwise(self):
        return self.get_radius_clockwise(self._curvature)[1]

    @clockwise.setter
    def clockwise(self):
        self.set_radius_clockwise('clockwise', 'curvature')

    @property
    def org_curvature(self):
        return self._org_curvature

    @org_curvature.setter
    def org_curvature(self, value):
        self._org_curvature = value

    @property
    def org_radius(self):
        return self.get_radius_clockwise(self._org_curvature)[0]

    @org_radius.setter
    def org_radius(self):
        self.set_radius_clockwise('org_radius', 'org_curvature')

    @property
    def org_clockwise(self):
        return self.get_radius_clockwise(self._org_curvature)[1]

    @org_clockwise.setter
    def org_clockwise(self):
        self.set_radius_clockwise('org_clockwise', 'org_curvature')

    def move(self, mv_x, mv_z):
        """ Moves the TrackCoord object to a different set of coordinates.
            The coord argument must be a tuple (x, z) of length 2.
        """
        self.pos_x += mv_x
        self.pos_z += mv_z

    def __repr__(self):
        return 'org: {ol} {oc}; pos: {px} {pz}; curv: {c}; brg: {b}'.format(
            ol=self.org_length, oc=self._org_curvature, px=self.pos_x,
            pz=self.pos_z, c=self._curvature, b=repr(self._bearing)
        )

    def __str__(self):
        if self.curvature == 0:
            str_r = "Straight section:"
        else:
            radius = self.radius
            str_r = ("Curved section: radius of curvature "
                     "{:.0f}".format(radius))

        return ("{r} position ({x:.3f}, {z:.3f}) and bearing of {a:.3f}"
                "".format(r=str_r, x=self.pos_x, z=self.pos_z,
                          a=self.bearing.deg))
