# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Curve calculations

from copy import copy
import math

from ec.common import Bearing, LinearEquation
from ec.section import TrackSection


class CurveError(Exception):
    pass


class TrackCurve(TrackSection):
    """ Group of track sections. Like TrackSection, takes a set of coordinates
        as input but utilises methods to create curves with track sections
        joining up tracks.
        Additonal parameter: 'split' option for whether to split the static
        curve section into multiple 500 m sections.
    """
    max_length = 500

    def __init__(self, curve, minimum, speed, split=True):
        super(TrackCurve, self).__init__(curve, minimum, speed)
        self.split_static = split

    def ts_easement_curve(self, curve, end_curv):
        """ Creates a TrackSection instance and returns its easement_curve
            method, for operational and reading ease.
        """
        ts = TrackSection(curve, self.minimum_radius, self.speed_tolerance)
        return ts.easement_curve(end_curv)

    def ts_static_curve(self, curve, angle_diff=None, arc_length=None):
        """ Creates a TrackSection instance and returns its static_curve
            method with 'angle' type, for operational and reading ease.
        """
        ts = TrackSection(curve, self.minimum_radius, self.speed_tolerance)
        return ts.static_curve(angle_diff, arc_length)

    def find_diff_angle(self, other, apply_cw=False):
        """ Finds the difference in bearing between the two tracks with
            bearing A and B. If A-B > B-A then B is to the right with a
            clockwise curve, and vice versa.
            If apply_cw is True, will pick side depending on self.clockwise
            already set, even if it has the bigger difference in bearing.
        """
        # Checks how the 2nd track is aligned wrt the 1st
        if self.start.bearing.nearly_equal(other.bearing):
            raise CurveError('Tracks 1 and 2 must not be parallel.')

        elif (self.start.bearing - other.bearing).rad == math.pi:
            # The two tracks are in opposite directions
            # Check whether other track is to left or right of the starting track
            start_point = (self.start.pos_x, self.start.pos_z)
            start_line = LinearEquation(self.start.bearing, start_point)
            right_side = (start_point[0] + math.sin(self.start.bearing.rad),
                          start_point[1] + math.cos(self.start.bearing.rad))

            if start_line.dist((other.pos_x, other.pos_z)) == 0:
                raise CurveError('The other track is on the same alignment'
                                 ' as the starting track.')
            diff_b = Bearing(math.pi, rad=True)
            cw = start_line.same_side((other.pos_x, other.pos_z), right_side)
            if apply_cw and cw is not self.clockwise:
                raise CurveError('The starting track is curved away from the '
                                 'other track - cannot make a suitable '
                                 'alignment.')

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
            raise CurveError('Tracks 1 and 2 must not be parallel.')
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

    def curve_fit_radius(self, other, radius, clockwise=None):
        """ Finds a curve with easement sections and static curve of a certain
            radius of curvature that fits the two straight tracks.
        """
        if radius < self.minimum_radius:
            raise CurveError(
                'Radius {0} must be greater than the minimum radius of '
                'curvature.'.format(radius))

        try:
            if other.curvature != 0 or self.start.curvature != 0:
                raise CurveError('Both tracks must be straight.')

            if self.start.bearing.nearly_equal(other.bearing):
                raise CurveError('Tracks 1 and 2 must not be parallel.')
            elif self.start.bearing.nearly_equal(other.bearing.flip()):
                # Can't fit curve of specific radius to two parallel tracks -
                # 1) only one valid radius value, 2) can be placed anywhere
                # along tracks.
                raise CurveError('This method does not work with tracks '
                                 'parallel in opposite directions.')

        except AttributeError as err:
            raise AttributeError('Tracks 1 and 2 need to be TrackCoord '
                                 'objects.') from err

        # Sets signed curvature and angle difference between 2 straight tracks
        self.clockwise = clockwise
        diff_angle = self.find_diff_angle(other, True)
        curvature = -1 / radius if self.clockwise else 1 / radius

        # Finds length of easement curve and adjusts angle diff of static curve
        easement_length = self.easement_length(curvature)
        static_curve_angle = diff_angle.rad - 2 * self.easement_angle(easement_length)
        if static_curve_angle < 0:
            # Angle diff from two easement curves bigger than angle between
            # the two straight tracks; can't fit them in
            raise CurveError(
                'The easement curves are too long to fit within the curve; '
                'consider increasing the radius of curvature.')

        # Construct the 3 sections of curve
        ec1 = self.ts_easement_curve(self.start, curvature)
        static_length = abs(static_curve_angle / curvature)
        if not self.split_static or static_length <= self.max_length:
            # Single static section
            static = self.ts_static_curve(ec1, static_curve_angle)
            ec2 = self.ts_easement_curve(static, 0)
            # Assembling into a list and copying to ensure no changed values -
            # they depend on each other
            curve_data = [copy(s) for s in [self.start, ec1, static, ec2]]

        else:
            sections = math.floor(static_length/self.max_length)
            static = []
            for s in range(sections):
                next_section = static[s-1] if s != 0 else ec1
                static += [self.ts_static_curve(next_section,
                                                arc_length=self.max_length)]
            remainder = static_length % self.max_length
            static += [self.ts_static_curve(static[-1], arc_length=remainder)]

            ec2 = self.ts_easement_curve(static[-1], 0)
            curve_data = [copy(s) for s in [self.start, ec1] + static + [ec2]]

        # Finds the required translation to align the curve with the 2 tracks
        # Should already be aligned with 1st
        line_track = LinearEquation(other.bearing,
                                    (other.pos_x, other.pos_z))
        line_end_point = LinearEquation(self.start.bearing,
                                        (ec2.pos_x, ec2.pos_z))
        end_point = line_track.intersect(line_end_point)

        # Applies translation to each of the sections
        for ts in curve_data:
            ts.move(end_point[0] - ec2.pos_x, end_point[1] - ec2.pos_z)
        return curve_data

    def curve_fit_length(self, other, length, clockwise=None, places=4,
                         iterations=50):
        """ Finds a curve with easement sections and static curve of a certain
            length that fits the two tracks, by using the bisection method to
            find the correct radius of curvature.
        """
        n_floor, n_ceiling = None, None
        roc = self.minimum_radius

        # Let initial curve_fit_radius eval handle all the CurveExceptions
        # Run loop for a set number of iterations
        for j in range(iterations):
            try:
                curve = self.curve_fit_radius(other=other, radius=roc,
                                              clockwise=clockwise)

            except CurveError as err:
                if 'The easement curves are too long' in str(err):
                    n_floor = roc
                else:
                    raise

            else:
                static_length = sum(i.org_length for i in curve if
                                    i.org_type == 'static')
                if round(static_length - length, places) == 0:
                    # Accurate enough
                    return curve
                elif static_length > length:
                    # Static curve too long - try reducing RoC to increase easement length
                    n_ceiling = roc
                elif static_length < length:
                    # Static curve too short - try raising RoC to decrease easement length
                    n_floor = roc

            if n_floor is not None:
                if n_ceiling is not None:
                    roc = (n_floor + n_ceiling) / 2
                else:
                    # No ceiling yet, so raise RoC
                    roc *= 2
            else:
                # Floor should have been set with first iteration
                raise CurveError('The required radius of curvature for static '
                                 'curve of length {} is too small.'
                                 ''.format(length))

        # Loop runs out of iterations
        else:
            raise CurveError(
                'A suitable alignment was not found after {0} iterations. '
                ''.format(iterations))

    def curve_fit_point(self, other, add_point=None, places=4, iterations=100):
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
                raise CurveError('The end track must be straight.')
            if self.start.bearing.nearly_equal(other.bearing):
                raise CurveError('Tracks 1 and 2 must not be parallel.')

        except AttributeError as err:
            raise AttributeError('Tracks 1 and 2 need to be TrackCoord '
                                 'objects.') from err

        if add_point is not None:
            try:
                self.get_static_radius(add_point)
            except AttributeError as err:
                raise AttributeError('Add_point must be another TrackCoord '
                                     'object.') from err

        # Setting clockwise direction if starting curvature is not straight
        if self.start.curvature != 0:
            self.clockwise = self.start.curvature < 0
            diff_angle = self.find_diff_angle(other, True)
            if diff_angle.rad > math.pi:
                raise CurveError('The curved track is not aligned in the '
                                 'same direction as the other track.')

        else:
            diff_angle = self.find_diff_angle(other)
            if not self.check_start_alignment(other) and not \
                    self.start.bearing.nearly_equal(other.bearing.flip()):
                # Other track behind start point, so flip CW/ACW to create a
                # balloon loop instead and recalculate diff_angle
                self.clockwise = not self.clockwise
                diff_angle = self.find_diff_angle(other, True)

        line_other = LinearEquation(bearing=other.bearing,
                                    point=(other.pos_x, other.pos_z))
        start_point = (self.start.pos_x, self.start.pos_z)
        # Set upper and lower bounds, and set starting curvature
        n_floor, n_ceiling = None, None
        curvature = 1 / self.minimum_radius
        curvature *= -1 if self.clockwise else 1

        # If starting curvature is not zero, adjust diff_angle to take into
        # account 'negative' section of easement curve
        if self.start.curvature != 0:
            pre_angle = self.easement_angle(self.easement_length(self.start.curvature))
        else:
            pre_angle = 0

        # Ensuring it runs in a loop with a limited number of iterations
        for j in range(iterations):
            easement_length = self.easement_length(curvature)
            static_curve_angle = diff_angle.rad - self.easement_angle(easement_length) \
                - abs(self.easement_angle(easement_length) - pre_angle)

            if static_curve_angle < 0:
                # RoC too small; set a floor and repeat loop
                n_floor = curvature

            else:
                if self.start.curvature != curvature:
                    # Usual EC -> Static -> EC setup
                    ec1 = self.ts_easement_curve(self.start, curvature)
                    curve_data = [self.start, copy(ec1)]
                else:
                    # Skip the first easement curve
                    curve_data = [self.start]

                static_length = abs(static_curve_angle / curvature)
                # Checking if static curve is longer than 500
                if not self.split_static or static_length <= self.max_length:
                    # Single static section
                    static = self.ts_static_curve(curve_data[-1],
                                                  static_curve_angle)
                    ec2 = self.ts_easement_curve(static, 0)
                    curve_data += [copy(s) for s in [static, ec2]]
                # If split_static is True and longer than 500m, split
                else:
                    sections = math.floor(static_length / self.max_length)
                    ls_static = []
                    for s in range(sections):
                        next_section = ls_static[s-1] if s != 0 else \
                            curve_data[-1]
                        ls_static += [self.ts_static_curve(
                            next_section, arc_length=self.max_length)]
                    # Adding the remainder section
                    remainder = static_length % self.max_length
                    ls_static += [self.ts_static_curve(ls_static[-1],
                                                       arc_length=remainder)]
                    ec2 = self.ts_easement_curve(ls_static[-1], 0)
                    curve_data += [copy(s) for s in ls_static + [ec2]]

                end_point = (curve_data[-1].pos_x, curve_data[-1].pos_z)

                if line_other.dist(end_point) < 10 ** (-places):
                    # Result accurate enough
                    return curve_data

                elif line_other.same_side(start_point, end_point):
                    # Same side, ie curve hasn't reached the other track -
                    # need larger RoC
                    n_floor = curvature

                elif not line_other.same_side(start_point, end_point):
                    # Opposite sides, ie curve overshot - need smaller RoC
                    n_ceiling = curvature

                # Zero length of static curve but still overshot - won't work
                elif not line_other.same_side(start_point, end_point) \
                        and static_curve_angle < 10 ** -3:
                    raise CurveError(
                        'The starting point is too close to the second track '
                        'for this curve - try moving the start point away.')

                else:
                    raise ValueError('Something went wrong here - dist',
                                     line_other.dist(end_point))

            if n_floor is not None:
                if n_ceiling is not None:
                    # Both floor and ceiling are set, so find midpoint
                    curvature = (n_ceiling + n_floor)/2
                else:
                    # Ceiling value is set but not under so reduce RoC
                    curvature *= 1/2
            else:
                # Floor should have been set with first iteration
                raise CurveError(
                    'Start point is too close to the straight track such that '
                    'the required RoC is smaller than the minimum.')

        # Loop runs out of iterations
        else:
            raise CurveError(
                'A suitable alignment was not found after {0} iterations. '
                ''.format(iterations))
