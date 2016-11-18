# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Track sections

import math

from ec.coord import Q, TrackCoord
from ec.common import Bearing, transform, LinearEquation


class TrackError(Exception):
    pass


class TrackSection(object):
    """ Section of track, either straight, curve with constant curvature
        or easement curve. Takes a set of coordinates as input, and another
        set of coordinates as output, to join with another track.
    """
    # Base measurements for normalisation
    n_speed, n_radius, n_length = 200, 800, 298.507

    def __init__(self, curve, minimum, speed):
        self.clockwise = None
        self.minimum_radius = minimum
        self.speed_tolerance = speed
        self.start = curve

        try:
            if self.minimum_radius <= 0:
                raise TrackError('The minimum radius of curvature must '
                                 'be a positive non-zero number.')
            if abs(self.start.curvature) > 1 / self.minimum_radius:
                raise TrackError('Radius must be equal or greater than '
                                 'the minimum radius of curvature.')

        except AttributeError as err:
            raise AttributeError('TrackCoord object required.') from err

    def factor(self):
        """ Normalisation factor as used in the Fresnel integrals. """
        return (self.speed_tolerance / 200) ** 3 \
            * self.n_length * self.n_radius

    def fresnel(self, length):
        """ Calculates the polynomials for the easement curves, which are
            based on the Taylor series for the Fresnel integrals used for the
            Euler spiral, and normalised - each variable t is multiplied by
            factor a, and then the overall result is divided by a.
            z-axis: C(L) with 2 terms; x-axis: S(L) with 1 term
        """
        if self.clockwise is None:
            raise AttributeError('The clockwise attribute has not been set'
                                 'yet.')

        a, t = 1 / math.sqrt(2*self.factor()), length
        x, z = a**2*t**3 / 3, t - a**4*t**5 / 10

        return (-x, z) if not self.clockwise else (x, z)

    def easement_angle(self, length):
        """ Returns the tangential angle of the easement curve at a length
            from the origin. The angle is between the curve at that particular
            point and the z-axis, and is in radians.
        """

        a, t = 1 / math.sqrt(2 * self.factor()), length
        # Derivatives of the polynomials from fresnel()
        xp, zp = a**2*t**2, 1 - a**4*t**4 / 2

        return math.acos(zp / math.hypot(xp, zp))

    def easement_curvature(self, length):
        """ Returns the signed curvature at a length on the easement curve
            from the origin. It is the inverse of the radius of curvature.
            Calculates curvature by using the normalisation factor.
        """
        if self.clockwise is None:
            raise AttributeError('The clockwise attribute has not been set'
                                 'yet.')

        curvature = length / self.factor()
        return -curvature if self.clockwise else curvature

    def easement_length(self, curvature):
        """ Uses the normalisation factor to find the length of easement curve
            starting with zero curvature and ending with a set curvature.
        """
        return self.factor() * abs(curvature)

    def get_static_radius(self, add, apply_result=True):
        """ Finds the radius of curvature for a static curve from a pair of
            using the starting coordinates and another TrackCoord object, both
            on the same curve.
            If apply: apply result to the self.start.curvature property and
            return None.
        """
        align = LinearEquation(self.start.bearing,
                               (self.start.pos_x, self.start.pos_z))
        try:
            end_point = (add.pos_x, add.pos_z)
        except AttributeError as err:
            raise AttributeError('The other coord needs to be an TrackCoord '
                                 'object.') from err

        dist_align = align.dist(end_point)
        if 0 <= dist_align < 0.0005:
            raise TrackError('A curve cannot be formed from a pair of '
                             'coordinates already on the same line.')

        chord_length = math.hypot(self.start.pos_x - add.pos_x,
                                  self.start.pos_z - add.pos_z)
        # Triangle with chord and two tangents is an isoceles triangle;
        # diff bearing is double that of interior angle
        diff_angle = 2 * math.asin(dist_align / chord_length)
        roc = chord_length / (2 * math.sin(diff_angle/2))

        if apply_result:
            # Create a vector to right of alignment line and check whether
            # other point is on same side
            perpendicular = self.start.bearing + Bearing(math.pi/2, rad=True)
            right_vector = (self.start.pos_x + math.sin(perpendicular.rad),
                            self.start.pos_z + math.cos(perpendicular.rad))
            self.start.curvature = -1 / roc if \
                align.same_side(end_point, right_vector) else 1 / roc

        else:
            return roc

    def easement_curve(self, end_curv):
        """ Creates the easement curve based on the curvature at end of curve
            and outputs a TrackCoord object.
        """
        if abs(end_curv) > 1 / self.minimum_radius:
            raise TrackError(
                'Ending radius of curvature must be at least {0},'
                'the minimum RoC.'.format(self.minimum_radius))

        start_curv = self.start.curvature
        # Checking if curvature are aligned correctly for both start and end
        if start_curv == end_curv:
            raise ValueError(
                'The ending curvature given is the same as the starting '
                'curvature.')
        elif start_curv == 0:
            self.clockwise = True if end_curv < 0 else False
        elif start_curv < 0 and end_curv <= 0:
            self.clockwise = True
        elif start_curv > 0 and end_curv >= 0:
            self.clockwise = False
        else:
            raise ValueError(
                'Starting and ending curvature must both be >= 0 or <= 0. '
                'Start: {0}, End: {1}'.format(start_curv, end_curv))

        # Checks whether parametric equations need to be reversed
        if abs(start_curv) > abs(end_curv):
            reverse = True
            self.clockwise = not self.clockwise
        else:
            reverse = False

        # Calculates the length of easement curves from curvature 0
        # Flip the curvature as well if needed
        m = 1 if not reverse else -1
        start_length = self.easement_length(m * start_curv)
        end_length = self.easement_length(m * end_curv)
        curve_length = abs(start_length - end_length)

        # Find angles and positions
        x0, z0 = self.fresnel(start_length)
        x1, z1 = self.fresnel(end_length)
        xs, zs = self.start.pos_x, self.start.pos_z

        r0 = Bearing(self.easement_angle(start_length), rad=True)
        r1 = Bearing(self.easement_angle(end_length), rad=True)
        rs = self.start.bearing

        # Adjusting alignment of curves
        if not self.clockwise:
            r0, r1 = -r0, -r1

        if reverse:
            r0, r1 = r0.flip(), r1.flip()

        # Transform the end point
        tx, tz = transform(a=(x1, z1), r=rs-r0, b=(x0, z0), c=(xs, zs))
        ry = rs + r1 - r0

        return TrackCoord(pos_x=tx, pos_z=tz, rotation=ry, quad=Q.NONE,
                          curvature=end_curv, org_length=curve_length,
                          org_curvature=self.start.curvature,
                          org_type='easement')

    def static_curve(self, angle_diff):
        """ Creates a static (no change in curvature) track section based
            on the radius of curvature set with TrackCoord. Outputs
            another TrackCoord object. Length of the static curve depends
            on the difference in bearing given.
        """
        if self.start.curvature == 0:
            raise TrackError('Angle cannot be specified if the track is '
                             'already straight.')
        else:
            t = angle_diff
            length = t / abs(self.start.curvature)

        self.clockwise = False if self.start.curvature > 0 else True
        radius = self.start.radius

        x, z = radius * (1 - math.cos(t)), radius * math.sin(t)
        r = Bearing(t, rad=True)
        x, r = (-x, -r) if not self.clockwise else (x, r)

        # Moving curve to starting coordinates
        xs, zs, rs = self.start.pos_x, self.start.pos_z, self.start.bearing
        tx, tz = transform(a=(x, z), r=rs, c=(xs, zs))
        ry = rs + r

        return TrackCoord(pos_x=tx, pos_z=tz, rotation=ry, quad=Q.NONE,
                          curvature=self.start.curvature, org_length=length,
                          org_curvature=self.start.curvature,
                          org_type='static')

    def straight_line(self, length):
        """ Creates a straight line with zero curvature. Outputs another
            TrackCoord object.
        """
        if self.start.curvature != 0:
            raise TrackError('The starting curvature must be zero to '
                             'create a straight line.')

        line = LinearEquation(self.start.bearing,
                              (self.start.pos_x, self.start.pos_z))
        end_x, end_y = line.move(length)

        return TrackCoord(pos_x=end_x, pos_z=end_y,
                          rotation=self.start.bearing, quad=Q.NONE,
                          curvature=0, org_length=length, org_curvature=0,
                          org_type='straight')

    def __repr__(self):
        return '{tc}; min radius: {m}; speed: {s}; clockwise: {cl}'.format(
            tc=repr(self.start), m=self.minimum_radius, s=self.speed_tolerance,
            cl=self.clockwise)
