# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Test script for the TrackSection class

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.common
import ec.coord
import ec.section
import ec.curve
from tests.tests_common import CustomAssertions


class BaseTCTests(unittest.TestCase, CustomAssertions):

    def setUp(self):
        super(BaseTCTests, self).setUp()

        minimum_high, speed_high = 500, 120
        minimum_low, speed_low = 200, 80

        self.start_straight = ec.coord.TrackCoord(
            pos_x=217.027, pos_z=34.523, rotation=48.882, quad=ec.coord.Q.NE, curvature=0)
        self.start_curved = ec.coord.TrackCoord(
            pos_x=354.667, pos_z=137.112, rotation=59.824, quad=ec.coord.Q.NE, curvature=-1/600)
        self.start_curved_add = ec.coord.TrackCoord(
            pos_x=287.741, pos_z=92.965, rotation=53.356, quad=ec.coord.Q.NE, curvature=0)

        self.end_left = ec.coord.TrackCoord(
            pos_x=467.962, pos_z=465.900, rotation=12.762, quad=ec.coord.Q.NE, curvature=0)
        self.end_right = ec.coord.TrackCoord(
            pos_x=582.769, pos_z=223.772, rotation=75.449, quad=ec.coord.Q.NE, curvature=0)

        # For curves with diff > 270
        self.end_far_left = ec.coord.TrackCoord(
            pos_x=-123.550, pos_z=199.813, rotation=5.913, quad=ec.coord.Q.SW, curvature=0)
        self.end_far_right = ec.coord.TrackCoord(
            pos_x=296.508, pos_z=681.428-1024, rotation=72.687, quad=ec.coord.Q.NW, curvature=0)
        # For curves with diff = 180
        self.end_reverse_left = ec.coord.TrackCoord(
            pos_x=6.616, pos_z=872.368, rotation=48.882, quad=ec.coord.Q.SW, curvature=0)
        self.end_reverse_right = ec.coord.TrackCoord(
            pos_x=569.182, pos_z=553.873-1024, rotation=48.882, quad=ec.coord.Q.SW, curvature=0)
        # To test how RoC with low angle diff - should raise exception
        self.end_low_angle = ec.coord.TrackCoord(
            pos_x=400.495, pos_z=178.755, rotation=53.612, quad=ec.coord.Q.NE, curvature=0)

        self.straight_high = ec.curve.TrackCurve(self.start_straight, minimum_high, speed_high)
        self.straight_low = ec.curve.TrackCurve(self.start_straight, minimum_low, speed_low)
        self.right = ec.curve.TrackCurve(self.start_curved, minimum_high, speed_high)

    def tearDown(self):
        super(BaseTCTests, self).tearDown()

        del self.start_straight, self.start_curved, self.start_curved_add
        del self.end_left, self.end_right, self.end_far_left, self.end_far_right
        del self.end_reverse_left, self.end_reverse_right, self.end_low_angle
        del self.straight_high, self.straight_low, self.right

    def test_create_easement(self):
        ts = ec.section.TrackSection(self.start_straight, 500, 120)
        self.assertEqual(ts.easement_curve(0.0001).__dict__,
                         self.straight_high.easement_curve(0.0001).__dict__)

    def test_create_static(self):
        ts = ec.section.TrackSection(self.start_straight, 500, 120)
        ts.start.curvature = 0.0001
        self.straight_high.start.curvature = 0.0001
        self.assertEqual(ts.static_curve(math.pi/4).__dict__,
                         self.straight_high.static_curve(math.pi/4).__dict__)


class DiffAngleTests(BaseTCTests):

    def test_exception_parallel(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'must not be parallel'):
            self.straight_high.find_diff_angle(self.start_straight)

    def test_diff_left(self):
        diff_b = self.straight_high.find_diff_angle(self.end_left)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (36.12, False))

    def test_diff_right(self):
        diff_b = self.straight_high.find_diff_angle(self.end_right)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (26.567, True))

    def test_diff_reverse_left(self):
        diff_b = self.straight_high.find_diff_angle(self.end_reverse_left)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (180, False))

    def test_diff_reverse_right(self):
        diff_b = self.straight_high.find_diff_angle(self.end_reverse_right)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (180, True))

    def test_diff_far_left(self):
        self.straight_high.clockwise = False
        diff_b = self.straight_high.find_diff_angle(self.end_far_left, True)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (222.969, False))

    def test_diff_not_far_left(self):
        diff_b = self.straight_high.find_diff_angle(self.end_far_left)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (137.031, True))

    def test_diff_far_right(self):
        self.straight_high.clockwise = True
        diff_b = self.straight_high.find_diff_angle(self.end_far_right, True)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (238.431, True))

    def test_diff_not_far_right(self):
        diff_b = self.straight_high.find_diff_angle(self.end_far_right)
        self.assertDataAlmostEqual((diff_b.deg, self.straight_high.clockwise), (121.569, False))


class AlignmentTests(BaseTCTests):

    def test_exception_parallel(self):
        self.end_reverse_left.bearing = self.end_reverse_left.bearing.flip()
        with self.assertRaisesRegex(ec.curve.CurveError, 'must not be parallel'):
            self.straight_high.check_start_alignment(self.end_reverse_left)

    def test_alignment_left(self):
        self.assertTrue(self.straight_high.check_start_alignment(self.end_left))

    def test_alignment_right(self):
        self.assertTrue(self.straight_high.check_start_alignment(self.end_right))

    def test_alignment_far_left(self):
        self.assertFalse(self.straight_high.check_start_alignment(self.end_far_left))

    def test_alignment_far_right(self):
        self.assertFalse(self.straight_high.check_start_alignment(self.end_far_right))

    def test_alignment_reverse_left(self):
        self.assertFalse(self.straight_high.check_start_alignment(self.end_reverse_left))

    def test_alignment_reverse_right(self):
        self.assertFalse(self.straight_high.check_start_alignment(self.end_reverse_right))


class CurveFitRadiusTests(BaseTCTests):

    def test_exception_curve_radius_minimum_radius(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'Radius 350 must be greater'):
            self.straight_high.curve_fit_radius(self.end_left, 350)

    def test_exception_curve_radius_wrong_object(self):
        with self.assertRaisesRegex(AttributeError, 'need to be TrackCoord'):
            self.straight_high.curve_fit_radius(None, 600)

    def test_exception_curve_radius_cannot_fit(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'The easement curves are too long'):
            self.straight_high.curve_fit_radius(self.end_low_angle, 500)

    def test_exception_curve_radius_curved(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'Both tracks must be straight'):
            self.right.curve_fit_radius(self.end_left, 500)

    def test_exception_curve_radius_reverse(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'This method does not work'):
            self.straight_high.curve_fit_radius(self.end_reverse_left, 500)

    def test_curve_assert_radius(self):
        curve = self.straight_high.curve_fit_radius(self.end_left, 600)
        self.assertAlmostEqual(curve[2].radius, 600)
    
    def test_curve_radius_left(self):
        curve = self.straight_high.curve_fit_radius(self.end_left, 600)
        self.assertTrackAlign(curve[-1], self.end_left)

    def test_curve_radius_right(self):
        curve = self.straight_high.curve_fit_radius(self.end_right, 600)
        self.assertTrackAlign(curve[-1], self.end_right)

    def test_curve_radius_can_fit(self):
        curve = self.straight_high.curve_fit_radius(self.end_low_angle, 1200)
        self.assertTrackAlign(curve[-1], self.end_low_angle)

    def test_curve_radius_far_left(self):
        curve = self.straight_low.curve_fit_radius(self.end_far_left, 225, False)
        self.assertTrackAlign(curve[-1], self.end_far_left)

    def test_curve_radius_far_right(self):
        curve = self.straight_low.curve_fit_radius(self.end_far_right, 225, True)
        self.assertTrackAlign(curve[-1], self.end_far_right)


class CurveFitLengthTests(BaseTCTests):

    def test_exception_curve_radius_minimum_radius(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'The required radius of curvature'):
            self.straight_high.curve_fit_length(self.end_far_left, 100, False)

    def test_exception_curve_radius_wrong_object(self):
        with self.assertRaisesRegex(AttributeError, 'need to be TrackCoord'):
            self.straight_high.curve_fit_length(None, 600)

    def test_exception_curve_radius_curved(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'Both tracks must be straight'):
            self.right.curve_fit_length(self.end_left, 200)

    def test_exception_curve_radius_reverse(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'This method does not work'):
            self.straight_high.curve_fit_length(self.end_reverse_left, 500)

    def test_curve_assert_length(self):
        curve = self.straight_high.curve_fit_length(self.end_left, 300)
        self.assertAlmostEqual(curve[2].org_length, 300, 4)

    def test_curve_radius_left(self):
        curve = self.straight_high.curve_fit_length(self.end_left, 300)
        self.assertTrackAlign(curve[-1], self.end_left)

    def test_curve_radius_right(self):
        curve = self.straight_high.curve_fit_length(self.end_right, 300)
        self.assertTrackAlign(curve[-1], self.end_right)

    def test_curve_radius_far_left(self):
        curve = self.straight_low.curve_fit_length(self.end_far_left, 1000, False)
        self.assertTrackAlign(curve[-1], self.end_far_left)

    def test_curve_radius_far_right(self):
        curve = self.straight_low.curve_fit_length(self.end_far_right, 1000, True)
        self.assertTrackAlign(curve[-1], self.end_far_right)


class CurveFitPointTests(BaseTCTests):

    def test_exception_curve_point_end_curved(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'end track must be straight'):
            self.straight_high.curve_fit_point(self.start_curved)

    def test_exception_curve_point_parallel(self):
        self.end_reverse_left.bearing = self.end_reverse_left.bearing.flip()
        with self.assertRaisesRegex(ec.curve.CurveError, 'must not be parallel'):
            self.straight_high.curve_fit_point(self.end_reverse_left)

    def test_exception_curve_point_wrong_object(self):
        with self.assertRaisesRegex(AttributeError, 'TrackCoord'):
            self.straight_high.curve_fit_point(None)

    def test_exception_curve_point_too_close(self):
        with self.assertRaisesRegex(ec.curve.CurveError, 'is too close'):
            self.straight_high.curve_fit_point(self.end_reverse_left)

    def test_exception_curve_point_curved_right_opposite(self):
        self.right.get_static_radius(self.start_curved_add)
        with self.assertRaisesRegex(ec.curve.CurveError, 'not aligned'):
            self.right.curve_fit_point(self.end_left)

    def test_curve_point_left(self):
        curve = self.straight_high.curve_fit_point(self.end_left)
        self.assertTrackAlign(curve[-1], self.end_left)

    def test_curve_point_right(self):
        curve = self.straight_high.curve_fit_point(self.end_right)
        self.assertTrackAlign(curve[-1], self.end_right)

    def test_curve_point_far_left(self):
        curve = self.straight_low.curve_fit_point(self.end_far_left)
        self.assertTrackAlign(curve[-1], self.end_far_left)

    def test_curve_point_far_right(self):
        curve = self.straight_low.curve_fit_point(self.end_far_right)
        self.assertTrackAlign(curve[-1], self.end_far_right)

    def test_curve_point_reverse_left(self):
        curve = self.straight_low.curve_fit_point(self.end_reverse_left)
        self.assertTrackAlign(curve[-1], self.end_reverse_left)

    def test_curve_point_reverse_right(self):
        curve = self.straight_low.curve_fit_point(self.end_reverse_right)
        self.assertTrackAlign(curve[-1], self.end_reverse_right)

    def test_curve_point_curved_right(self):
        curve = self.right.curve_fit_point(self.end_right, self.start_curved_add)
        self.assertTrackAlign(curve[-1], self.end_right)

    def test_curve_point_left_diff_sp(self):
        curve = self.straight_high.curve_fit_point(self.end_left, end_speed_tolerance=80)
        self.assertTrackAlign(curve[-1], self.end_left)

    def test_curve_point_right_diff_sp(self):
        curve = self.straight_high.curve_fit_point(self.end_right, end_speed_tolerance=80)
        self.assertTrackAlign(curve[-1], self.end_right)

    def test_curve_point_curved_right_diff_sp(self):
        curve = self.right.curve_fit_point(self.end_right, self.start_curved_add, end_speed_tolerance=80)
        self.assertTrackAlign(curve[-1], self.end_right)