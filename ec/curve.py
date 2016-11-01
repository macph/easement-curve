# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Curve calculations

from copy import copy
from enum import Enum
import math

from ec.common import Bearing, LinearEquation, transform


class Q(Enum):
    NONE, NE, SE, SW, NW = range(5)


class CoordException(Exception):
    pass


class TrackException(Exception):
    pass


class CurveException(Exception):
    pass


class TrackCoord(object):
    """ Contains the coordinates and curvature of a point on a track. Used to
        carry information between curve sections.
        org_curvature and org_length are used to store info about length of
        track beforehand.
    """

    def __init__(self, pos_x, pos_z, rotation, quad, curvature=None,
                 org_curvature=None, org_length=None):
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

        # Check if position values are valid
        try:
            math.sqrt(self.pos_x ** 2 + self.pos_z ** 2)
        except TypeError as err:
            raise CoordException("Position values must be int/floats.", err)

        # Converting y-axis rotation and quadrant to bearing
        if quad in [Q.NE, Q.SE, Q.SW, Q.NW]:
            self.quad = (rotation, quad)
        elif quad == Q.NONE:
            self.bearing = rotation
        else:
            raise CoordException("quad argument must either be a compass "
                                 "quadrant or none.")

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
                "Bearing: {} is not within [0, 360) / [0, 2pi)."
                "".format(repr(bearing)))

    @quad.setter
    def quad(self, value):
        try:
            rotation, quad = value
        except ValueError as err:
            raise ValueError("The quad property requires two values: "
                             "rotation and quadrant.") from err
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
                raise CoordException("The y-axis rotation must be in the "
                                     "range [-90, 90].")
        except KeyError:
            raise CoordException("{!r} is not a valid quadrant.".format(quad))
        except TypeError as err:
            raise CoordException(
                "{0:!r} is not a valid number for the rotation variable."
                "".format(rotation), err)

    @staticmethod
    def get_radius_clockwise(stored_variable):
        if stored_variable < 0:
            return 1 / abs(stored_variable), 'CW'
        elif stored_variable > 0:
            return 1 / abs(stored_variable), 'ACW'
        else:
            return 0, 'straight'

    @staticmethod
    def set_radius_clockwise(variable, stored_variable):
        raise AttributeError("Can't set {0} property on its own. Use the "
                             "{1} property.".format(variable, stored_variable))

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


class TrackSection(object):
    """ Section of track, either straight, curve with constant curvature
        or easement curve. Takes a set of coordinates as input, and another
        set of coordinates as output, perhaps to join with another track.
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
                raise TrackException("The minimum radius of curvature must "
                                     "be a positive non-zero number.")
            if abs(self.start.curvature) > 1 / self.minimum_radius:
                raise TrackException("Radius must be equal or greater than "
                                     "the minimum radius of curvature.")

        except AttributeError as err:
            raise AttributeError("TrackCoord object required.") from err

    @property
    def factor(self):
        """ Normalisation factor as used in the Fresnel integrals. """
        return (self.speed_tolerance / 200) ** 3 \
            * self.n_length * self.n_radius

    @factor.setter
    def factor(self, value):
        raise AttributeError("The normalisation factor can only be set via"
                             "its inputs.")

    def check_clockwise(self):
        """ Checks if clockwise is set; AttributeError is raised if not."""
        if self.clockwise is None:
            raise AttributeError("The clockwise attribute has not been set"
                                 "yet.")

    def get_fresnel(self, length):
        """ Calculates the polynomials for the easement curves, which are
            based on the Taylor series for the Fresnel integrals used for the
            Euler spiral, and normalised - each variable t is multiplied by
            factor a, and then the overall result is divided by a.
            z-axis: C(L) with 2 terms; x-axis: S(L) with 1 term
        """
        self.check_clockwise()
        a, t = 1 / math.sqrt(2*self.factor), length
        x, z = a**2*t**3 / 3, t - a**4*t**5 / 10

        return (-x, z) if not self.clockwise else (x, z)

    def get_angle(self, length):
        """ Returns the tangential angle of the easement curve at a length
            from the origin. The angle is between the curve at that particular
            point and the z-axis, and is in radians.
        """
        self.check_clockwise()
        a, t = 1 / math.sqrt(2 * self.factor), length
        # Derivatives of the polynomials from get_fresnel()
        xp, zp = a**2*t**2, 1 - a**4*t**4 / 2
        return math.acos(zp / math.hypot(xp, zp))

    def get_curvature(self, length):
        """ Returns the signed curvature at a length on the easement curve
            from the origin. It is the inverse of the radius of curvature.
            Calculates curvature by using the normalisation factor.
        """
        self.check_clockwise()
        curvature = length/self.factor
        return -curvature if self.clockwise else curvature

    def get_length(self, curvature):
        """ Uses the normalisation factor to find the length of easement curve
            starting with zero curvature and ending with a set curvature.
        """
        return self.factor * abs(curvature)

    def get_static_radius(self, other, apply_result=True):
        """ Finds the radius of curvature for a static curve from a pair of
            using the starting coordinates and another TrackCoord object, both
            on the same curve.
            If apply: apply result to the self.start.curvature property and
            return None.
        """
        align = LinearEquation(self.start.bearing,
                               (self.start.pos_x, self.start.pos_z))
        try:
            end_point = (other.pos_x, other.pos_z)
        except AttributeError as err:
            raise AttributeError("The other coord needs to be an TrackCoord "
                                 "object.") from err
        dist_align = align.dist(end_point)
        if 0 <= dist_align < 0.0005:
            raise TrackException("A curve cannot be formed from a pair of "
                                 "coordinates already on the same line.")

        chord_length = math.hypot(self.start.pos_x - other.pos_x,
                                  self.start.pos_z - other.pos_z)
        # Triangle with chord and two tangents is an isoceles triangle; diff bearing is double that of interior angle
        diff_angle = 2 * math.asin(dist_align / chord_length)
        roc = chord_length / (2 * math.sin(diff_angle/2))

        if apply_result:
            # Create a vector to right of alignment line and check whether other point is on same side
            perpendicular = self.start.bearing + Bearing(math.pi/2, rad=True)
            right_vector = (self.start.pos_x + math.sin(perpendicular.rad),
                            self.start.pos_z + math.cos(perpendicular.rad))
            self.start.curvature = -1 / roc if \
                align.same_side(end_point, right_vector) else 1 / roc
        else:
            return roc

    def easement_curve(self, end_curv):
        """ Creates the easement curve based on the length, radius of curvature
            or tangential angle at end of curve and outputs a TrackCoord
            object.
        """
        if abs(end_curv) > 1 / self.minimum_radius:
            raise TrackException(
                "Ending radius of curvature must be at least {0},"
                "the minimum RoC.".format(self.minimum_radius))

        start_curv = self.start.curvature
        # Checking if curvature are aligned correctly for both start and end
        if start_curv == end_curv:
            raise ValueError(
                "The ending curvature given is the same as the starting "
                "curvature.")
        elif start_curv == 0:
            self.clockwise = True if end_curv < 0 else False
        elif start_curv < 0 and end_curv <= 0:
            self.clockwise = True
        elif start_curv > 0 and end_curv >= 0:
            self.clockwise = False
        else:
            raise ValueError(
                "Starting and ending curvature must both be >= 0 or <= 0. "
                "Start: {0}, End: {1}".format(start_curv, end_curv))

        # Checks whether parametric equations need to be reversed
        if abs(start_curv) > abs(end_curv):
            reverse = True
            self.clockwise = not self.clockwise
        else:
            reverse = False

        # Calculates the length of easement curves from curvature 0
        # Flip the curvature as well if needed
        m = 1 if not reverse else -1
        start_length = self.get_length(m * start_curv)
        end_length = self.get_length(m * end_curv)
        curve_length = abs(start_length - end_length)

        # Find angles and positions
        x0, z0 = self.get_fresnel(start_length)
        x1, z1 = self.get_fresnel(end_length)
        xs, zs = self.start.pos_x, self.start.pos_z

        r0 = Bearing(self.get_angle(start_length), rad=True)
        r1 = Bearing(self.get_angle(end_length), rad=True)
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
                          org_curvature=self.start.curvature)

    def static_curve(self, angle_diff):
        """ Creates a static (no change in curvature) track section based
            on the radius of curvature set with TrackCoord. Outputs
            another TrackCoord object. Length of the static curve depends
            on the difference in bearing given.
        """
        if self.start.curvature == 0:
            raise TrackException("Can't specify an angle if the track is "
                                 "already straight.")
        else:
            t = angle_diff
            length = t / abs(self.start.curvature)

        self.clockwise = False if self.start.curvature > 0 else True
        radius = self.start.radius

        x, z = radius * (1 - math.cos(t)), radius * math.sin(t)
        r = Bearing(t, rad=True)
        x, r = (-x, -r) if not self.clockwise else (x, r)

        xs, zs, rs = self.start.pos_x, self.start.pos_z, self.start.bearing
        tx, tz = transform(a=(x, z), r=rs, c=(xs, zs))
        ry = rs + r

        return TrackCoord(pos_x=tx, pos_z=tz, rotation=ry, quad=Q.NONE,
                          curvature=self.start.curvature, org_length=length,
                          org_curvature=self.start.curvature)

    def __repr__(self):
        return '{tc}; min radius: {m}; speed: {s}; clockwise: {cl}'.format(
            tc=repr(self.start), m=self.minimum_radius, s=self.speed_tolerance,
            cl=self.clockwise)


class TrackCurve(TrackSection):

    def __init__(self, curve, minimum, speed):
        """ Inherits from TrackSection. """
        super(TrackCurve, self).__init__(curve, minimum, speed)

    def ts_easement_curve(self, curve, end_curv):
        """ Creates a TrackSection instance and returns its easement_curve
            method, for operational and reading ease.
        """
        ts = TrackSection(curve, self.minimum_radius, self.speed_tolerance)
        return ts.easement_curve(end_curv)

    def ts_static_curve(self, curve, angle_diff):
        """ Creates a TrackSection instance and returns its static_curve
            method with 'angle' type, for operational and reading ease.
        """
        ts = TrackSection(curve, self.minimum_radius, self.speed_tolerance)
        return ts.static_curve(angle_diff)

    def find_diff_angle(self, other, apply_cw=False):
        """ Finds the difference in bearing between the two tracks with
            bearing A and B. If A-B > B-A then B is to the right with a
            clockwise curve, and vice versa.
            If apply_cw is True, will pick side depending on self.clockwise
            already set, even if it has the bigger difference in bearing.
        """
        # Checks how the 2nd track is aligned wrt the 1st
        if self.start.bearing.nearly_equal(other.bearing):
            raise CurveException('Tracks 1 and 2 must not be parallel.')

        elif (self.start.bearing - other.bearing).rad == math.pi:
            # The two tracks are in opposite directions
            # Check whether other track is to left or right of the starting track
            start_point = (self.start.pos_x, self.start.pos_z)
            start_line = LinearEquation(self.start.bearing, start_point)
            right_side = (start_point[0] + math.sin(self.start.bearing.rad),
                          start_point[1] + math.cos(self.start.bearing.rad))

            if start_line.dist((other.pos_x, other.pos_z)) == 0:
                raise CurveException('The other track is on the same alignment'
                                     ' as the starting track.')
            diff_b = Bearing(math.pi, rad=True)
            cw = start_line.same_side((other.pos_x, other.pos_z), right_side)
            if apply_cw and cw is not self.clockwise:
                raise CurveException('The starting track is curved away from '
                                     'the other track - cannot make a suitable'
                                     ' alignment.')

        elif (self.start.bearing - other.bearing).rad > \
                (other.bearing - self.start.bearing).rad:
            # 2nd track is aligned to the right
            diff_b, cw = other.bearing - self.start.bearing, True

        else:
            # Otherwise 2nd track is aligned to the left
            diff_b, cw = self.start.bearing - other.bearing, False

        if not apply_cw or self.clockwise is None:
            self.clockwise = cw
            return diff_b
        else:
            return diff_b if self.clockwise is cw else -diff_b

    def check_start_alignment(self, other):
        """ Checks whether the start point is aligned towards the other track -
            if it isn't, it will not be possible to extend a curve to join it.
            Raises False if it doesn't, True otherwise.
            Since LinearEquation.same_side(a, b) returns True if one of the
            points is on the line, it follows that this method returns False
            if the other alignment lies on the line.
        """

        if self.start.bearing.nearly_equal(other.bearing):
            raise CurveException('Tracks 1 and 2 must not be parallel.')
        elif (self.start.bearing - other.bearing).rad == math.pi:
            # Difference 180 deg
            return False
        else:
            # Check how the two points are aligned to each other.
            first = LinearEquation(other.bearing, (other.pos_x, other.pos_z))
            start_point = (self.start.pos_x, self.start.pos_z)
            second = LinearEquation(self.start.bearing, start_point)
            intersect = first.intersect(second)
            point_beyond = (intersect[0] + math.sin(self.start.bearing.rad),
                            intersect[1] + math.cos(self.start.bearing.rad))

            return not first.same_side(point_beyond, start_point)

    def curve_fit_radius(self, radius, other):
        """ Finds a curve with easement sections and static curve of a certain
            radius of curvature that fits the two straight tracks.
        """
        if radius < self.minimum_radius:
            raise CurveException(
                'Radius {0} must be greater than the minimum radius of '
                'curvature.'.format(radius))

        try:
            if other.curvature != 0 or self.start.curvature != 0:
                raise CurveException('Both tracks must be straight.')
            if self.start.bearing.nearly_equal(other.bearing):
                raise CurveException('Tracks 1 and 2 must not be parallel.')
            elif self.start.bearing.nearly_equal(other.bearing.flip()):
                # Can't fit curve of specific radius to two parallel tracks -
                # 1) only one valid radius value, 2) can be placed anywhere
                # along tracks.
                raise CurveException('This method does not work with tracks '
                                     'parallel in opposite directions.')
        except AttributeError as err:
            raise AttributeError('Tracks 1 and 2 need to be TrackCoord '
                                 'objects.') from err

        # Sets signed curvature and angle difference between 2 straight tracks
        diff_angle = self.find_diff_angle(other, True)
        curvature = -1 / radius if self.clockwise else 1 / radius

        # Finds length of easement curve and adjusts angle diff of static curve
        easement_length = self.get_length(curvature)
        static_curve_angle = diff_angle.rad - 2 * self.get_angle(easement_length)
        if static_curve_angle < 0:
            # Angle diff from two easement curves bigger than angle between
            # the two straight tracks; can't fit them in
            raise CurveException(
                "The easement curves are too long to fit within the curve;\n"
                "consider increasing the radius of curvature.")

        # Constructs the 3 sections of curve
        ec1 = self.ts_easement_curve(self.start, curvature)
        static = self.ts_static_curve(ec1, static_curve_angle)
        ec2 = self.ts_easement_curve(static, 0)

        # Assembling into a dict and copying to ensure no changed values -
        # they depends on each other
        curve_data = {'start': copy(self.start), 'ec1': copy(ec1),
                      'static': copy(static), 'ec2': copy(ec2)}

        # Finds the required translation to align the curve with the 2 tracks
        # Should already be aligned with 1st
        line_track = LinearEquation(other.bearing,
                                    (other.pos_x, other.pos_z))
        line_end_point = LinearEquation(self.start.bearing,
                                        (ec2.pos_x, ec2.pos_z))
        end_point = line_track.intersect(line_end_point)

        # Applies translation to each of the sections
        for ts in curve_data.values():
            ts.move(end_point[0] - ec2.pos_x, end_point[1] - ec2.pos_z)

        return curve_data

    def curve_fit_point(self, other, places=4, iterations=50):
        """ Extends a curve with easement sections from a point on a track,
            which can be curved, to join with a straight track. Uses the
            bisection method to find the correct radius of curvature by
            checking if the aligned curve has reached the second track or
            overshot.
            places: minimum distance between easement curve and 2nd track
            iterations: maximum number of iterations before giving up
        """
        try:
            if other.curvature != 0:
                raise CurveException('The end track must be straight.')
            if self.start.bearing.nearly_equal(other.bearing):
                raise CurveException('Tracks 1 and 2 must not be parallel.')
        except AttributeError as err:
            raise AttributeError('Tracks 1 and 2 need to be TrackCoord '
                                 'objects.') from err

        # Setting clockwise direction if starting curvature is not straight
        if self.start.curvature != 0:
            self.clockwise = self.start.curvature < 0
            diff_angle = self.find_diff_angle(other)
        else:
            diff_angle = self.find_diff_angle(other)
            if not self.check_start_alignment(other):
                # Flip CW direction and recalculate diff_angle
                self.clockwise = not self.clockwise
                diff_angle = self.find_diff_angle(other)

        line_other = LinearEquation(bearing=other.bearing,
                                    point=(other.pos_x, other.pos_z))
        # Set upper and lower bounds, and set starting curvature
        start_point = (self.start.pos_x, self.start.pos_z)
        n_floor, n_ceiling = None, None
        curvature = 1 / self.minimum_radius
        curvature *= -1 if self.clockwise else 1

        # If starting curvature is not zero, adjust diff_angle to take into
        # account 'negative' section of easement curve
        if self.start.curvature != 0:
            pre_angle = self.get_angle(self.get_length(self.start.curvature))
        else:
            pre_angle = 0

        # Ensuring it runs in a loop with a limited number of iterations
        for n in range(iterations):
            easement_length = self.get_length(curvature)
            static_curve_angle = diff_angle.rad - self.get_angle(easement_length) \
                - abs(self.get_angle(easement_length) - pre_angle)

            if static_curve_angle < 0:
                # RoC too small; set a floor and repeat loop
                n_floor = curvature
            else:
                if self.start.curvature != curvature:
                    # Usual EC -> Static -> EC setup
                    ec1 = self.ts_easement_curve(self.start, curvature)
                    static = self.ts_static_curve(
                        ec1, static_curve_angle)
                    ec2 = self.ts_easement_curve(static, 0)
                else:
                    # easement_length & pre_angle is cancelled out
                    ec1 = None
                    static = self.ts_static_curve(
                        self.start, static_curve_angle)
                    ec2 = self.ts_easement_curve(static, 0)

                # Copying to ensure no changes
                curve_data = {'start': copy(self.start), 'ec1': copy(ec1),
                              'static': copy(static), 'ec2': copy(ec2)}
                end_point = (curve_data['ec2'].pos_x, curve_data['ec2'].pos_z)

                if line_other.dist(end_point) < 10 ** (-places):
                    # Result accurate enough
                    return curve_data

                elif line_other.same_side(start_point, end_point):
                    # They are both positive or both negative, - same side
                    # Checking if absolute curvature is bigger than floor
                    if n_floor is None:
                        n_floor = curvature
                    else:
                        n_floor = curvature

                # Zero length of static curve but still overshot - won't work
                elif not line_other.same_side(start_point, end_point) \
                        and static_curve_angle < 10 ** -3:
                    raise CurveException(
                        "The starting point is too close to the second track "
                        "for this curve - try moving the start point away.")

                elif not line_other.same_side(start_point, end_point):
                    # They don't have the same sign, therefore opposite sides
                    # Checking if absolute curvature is smaller than ceiling
                    if n_ceiling is None:
                        n_ceiling = curvature
                    else:
                        n_ceiling = curvature

                else:
                    raise ValueError("Something went wrong here - dist",
                                     line_other.dist(end_point))

            if n_ceiling is not None:
                if n_floor is not None:
                    # Both floor and ceiling set, so find midpoint
                    curvature = (n_ceiling + n_floor)/2
                else:
                    # Ceiling value is set but not under so reduce RoC
                    curvature *= 2
            else:
                if n_floor is not None:
                    # Floor value is set but not over so increase RoC
                    curvature *= 1/2
                else:
                    raise ValueError("Something went wrong here - dist "
                                     "not being set as over or under.")

            if curvature > 1 / self.minimum_radius:
                raise CurveException(
                    "Start point is too close to the straight track such that "
                    "the required RoC is smaller than the minimum.")

        # Loop runs out of iterations
        else:
            raise CurveException(
                "A suitable alignment was not found after {0} iterations. "
                "".format(iterations))
