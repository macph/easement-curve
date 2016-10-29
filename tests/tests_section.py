# Ewan Macpherson September 2016
# Test script for the TrackSection class

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.common
import ec.curve
from tests.tests_common import CustomAssertions


class BaseTSTests(unittest.TestCase, CustomAssertions):

    def setUp(self):
        self.curved_left = ec.curve.TrackCoord(
            pos_x=31.875, pos_z=49.061, rotation=51.329, quad=ec.curve.Q.NW, curvature=1 / 600)
        self.curved_right = ec.curve.TrackCoord(
            pos_x=-30.678, pos_z=-17.147, rotation=5.787, quad=ec.curve.Q.NW, curvature=-1 / 600)
        self.straight = ec.curve.TrackCoord(
            pos_x=4.57, pos_z=39.724, rotation=-32.748, quad=ec.curve.Q.SE, curvature=0)
        self.s, self.m = 120, 500

    def tearDown(self):
        del self.curved_left, self.curved_right, self.straight, self.s, self.m


class TrackSectionTests(BaseTSTests):

    def test_exception_track_coord(self):
        with self.assertRaisesRegex(AttributeError, 'TrackCoord'):
            ts = ec.curve.TrackSection(None, self.m, self.s)

    def test_exception_minimum_radius(self):
        with self.assertRaises(ec.curve.TrackException):
            ts = ec.curve.TrackSection(self.curved_left, 800, self.s)

    def test_curvature_attribute(self):
        ts = ec.curve.TrackSection(self.curved_left, self.m, self.s)
        self.assertAlmostEqual(ts.start.curvature, 1/600)

    def test_speed_tolerance(self):
        ts = ec.curve.TrackSection(self.curved_left, self.m, self.s)
        self.assertEqual(ts.speed_tolerance, 120)


class FresnelTests(BaseTSTests):

    def setUp(self):
        super(FresnelTests, self).setUp()
        self.ts = ec.curve.TrackSection(self.curved_left, self.m, self.s)
        self.l = 80

    def tearDown(self):
        super(FresnelTests, self).tearDown()
        del self.ts, self.l

    def test_exception_clockwise_none(self):
        with self.assertRaisesRegex(AttributeError, 'clockwise'):
            self.ts.get_fresnel(self.l)

    def test_clockwise_result(self):
        self.ts.clockwise = True
        r1 = self.ts.get_fresnel(self.l)
        self.ts.clockwise = False
        r2 = self.ts.get_fresnel(self.l)
        r2 = [-r2[0], r2[1]]
        self.assertEqual(tuple(r1), tuple(r2))

    def test_fresnel_values(self):
        self.ts.clockwise = True
        values = {'x': 1.6543235518558268, 'z': 79.96921115283997}
        result = self.ts.get_fresnel(self.l)
        self.assertDataAlmostEqual(values, dict(zip(('x', 'z'), result)))

    def test_angle_clockwise(self):
        self.ts.clockwise = True
        self.assertTrue(self.ts.get_angle(self.l), 0.06207833753494783)

    def test_curvature_clockwise(self):
        self.ts.clockwise = True
        self.assertTrue(self.ts.get_curvature(self.l), -0.00155096470004343)

    def test_curvature_not_clockwise(self):
        self.ts.clockwise = False
        self.assertTrue(self.ts.get_curvature(self.l), 0.00155096470004343)

    def test_length(self):
        self.ts.clockwise = True
        self.assertTrue(self.ts.get_length(1/750), 68.7744)


class FindStaticRadiusTests(unittest.TestCase):

    def setUp(self):
        self.start = ec.curve.TrackCoord(
            pos_x=-29.794, pos_z=-41.463, rotation=10.202, quad=ec.curve.Q.SW, curvature=0)
        self.left = ec.curve.TrackCoord(
            pos_x=31.415, pos_z=154.380, rotation=24.511, quad=ec.curve.Q.SW, curvature=0)
        self.right = ec.curve.TrackCoord(
            pos_x=-19.177, pos_z=127.315, rotation=3.003, quad=ec.curve.Q.SE, curvature=0)
        self.s, self.m = 120, 500
        self.ts = ec.curve.TrackSection(self.start, self.m, self.s)

    def tearDown(self):
        super(FindStaticRadiusTests, self).tearDown()
        del self.ts, self.start, self.left, self.right, self.s, self.m

    def test_exception_wrong_object(self):
        with self.assertRaisesRegex(AttributeError, 'TrackCoord object'):
            self.ts.get_static_radius(None)

    def test_already_on_line(self):
        with self.assertRaisesRegex(ec.curve.TrackException, 'A curve cannot be'):
            tc = ec.curve.TrackCoord(pos_x=-28.023, pos_z=-31.621, rotation=0,
                                     quad=ec.curve.Q.NONE, curvature=0)
            self.ts.get_static_radius(tc)

    def test_find_radius_right(self):
        result = self.ts.get_static_radius(self.right, apply_result=False)
        self.assertAlmostEqual(result, 735.3875804726549)

    def test_apply_curvature_right(self):
        self.ts.get_static_radius(self.right)
        self.assertAlmostEqual(self.ts.start.curvature, -0.001359817930914901)

    def test_find_radius_right_opposite(self):
        new_ts = ec.curve.TrackSection(self.right, self.m, self.s)
        result = new_ts.get_static_radius(self.start)
        self.assertAlmostEqual(new_ts.start.curvature, -0.001359817930914901)

    def test_find_radius_left(self):
        result = self.ts.get_static_radius(self.left, apply_result=False)
        self.assertAlmostEqual(result, 823.7749637682972, places=3)

    def test_apply_curvature_left(self):
        self.ts.get_static_radius(self.left)
        self.assertAlmostEqual(self.ts.start.curvature, 0.0012139237582865768)

    def test_find_radius_left_opposite(self):
        new_ts = ec.curve.TrackSection(self.left, self.m, self.s)
        result = new_ts.get_static_radius(self.start)
        self.assertAlmostEqual(new_ts.start.curvature, 0.0012140339764863358)

    def test_find_radius_axes_clockwise(self):
        other = ec.curve.TrackCoord(pos_x=800, pos_z=0, rotation=90, quad=ec.curve.Q.NW)
        self.ts.start = ec.curve.TrackCoord(pos_x=0, pos_z=800, rotation=0, quad=ec.curve.Q.NW)
        self.ts.get_static_radius(other)
        self.assertAlmostEqual(self.ts.start.curvature, -1/800)

    def test_find_radius_axes_not_clockwise(self):
        other = ec.curve.TrackCoord(pos_x=0, pos_z=800, rotation=0, quad=ec.curve.Q.SE)
        self.ts.start = ec.curve.TrackCoord(pos_x=800, pos_z=0, rotation=90, quad=ec.curve.Q.SE)
        self.ts.get_static_radius(other)
        self.assertAlmostEqual(self.ts.start.curvature, 1/800)


class CurveBaseTests(unittest.TestCase, CustomAssertions):

    def setUp(self):
        minimum, speed = 500, 120

        straight = ec.curve.TrackCoord(
            pos_x=5, pos_z=5, rotation=60, quad=ec.curve.Q.NE, curvature=0)
        left = ec.curve.TrackCoord(
            pos_x=-5, pos_z=5, rotation=30, quad=ec.curve.Q.SE, curvature=0.001)
        right = ec.curve.TrackCoord(
            pos_x=-5, pos_z=-5, rotation=60, quad=ec.curve.Q.NW, curvature=-0.001)

        self.straight = ec.curve.TrackSection(straight, minimum, speed)
        self.left = ec.curve.TrackSection(left, minimum, speed)
        self.right = ec.curve.TrackSection(right, minimum, speed)

    def tearDown(self):
        del self.straight, self.left, self.right


class EasementCurveTests(CurveBaseTests):

    def test_exception_minimum_radius(self):
        with self.assertRaisesRegex(ec.curve.TrackException, 'must be at least'):
            self.straight.easement_curve(1/250)

    def test_exception_same_radius(self):
        with self.assertRaisesRegex(ValueError, 'curvature given is the same'):
            self.left.easement_curve(1/1000)

    def test_exception_opposite_curvature(self):
        with self.assertRaisesRegex(ValueError, 'Starting and ending curvature'):
            self.left.easement_curve(-1/800)

    def test_easement_origin_to_left(self):
        start = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NE, curvature=0)
        end = ec.curve.TrackSection(start, 500, 120).easement_curve(1/1000)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': -0.443, 'z': 51.579, 'b': 360-1.478}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_origin_to_right(self):
        start = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NE, curvature=0)
        end = ec.curve.TrackSection(start, 500, 120).easement_curve(-1/1000)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': 0.443, 'z': 51.579, 'b': 1.478}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_straight_to_left(self):
        end = self.straight.easement_curve(1/700)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': 68.152, 'z': 42.954, 'b': 56.983}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_straight_to_right(self):
        end = self.straight.easement_curve(-1/700)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': 69.445, 'z': 40.714, 'b': 63.017}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_left_to_straight(self):
        end = self.left.easement_curve(0)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': 21.555, 'z': -39.220, 'b': 180-31.478}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_right_to_straight(self):
        end = self.right.easement_curve(0)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': -49.220, 'z': 21.555, 'b': 360-58.522}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_left_to_left(self):
        end = self.left.easement_curve(1/700)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': 6.294, 'z': -14.003, 'b': 180-31.539}
        self.assertDataAlmostEqual(end_r, end_e, places=3)

    def test_easement_right_to_right(self):
        end = self.right.easement_curve(-1/700)
        end_r = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.deg}
        end_e = {'x': -24.003, 'z': 6.294, 'b': 360-58.461}
        self.assertDataAlmostEqual(end_r, end_e, places=3)


class StaticCurveTests(CurveBaseTests):

    def test_exception_straight(self):
        with self.assertRaisesRegex(ec.curve.TrackException, 'track is already straight'):
            self.straight.static_curve(1)

    def test_static_curve_no_angle(self):
        ep = self.left.static_curve(0)
        start = (self.left.start.pos_x, self.left.start.pos_z,
                 self.left.start.bearing)
        end = (ep.pos_x, ep.pos_z, ep.bearing)
        self.assertEqual(start, end)

    def test_static_curve_left_90(self):
        end = self.left.static_curve(math.pi/2)
        end_dict = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.rad}
        result_d = {'x': 1361.0254037844388, 'z': -361.02540378443865,
                    'b': math.pi/3}
        self.assertDataAlmostEqual(end_dict, result_d)

    def test_static_curve_right_90(self):
        end = self.right.static_curve(math.pi/2)
        end_dict = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.rad}
        result_d = {'x': -371.02540378443865, 'z': 1361.0254037844388,
                    'b': math.pi / 6}
        self.assertDataAlmostEqual(end_dict, result_d)

    def test_static_curve_left_60(self):
        end = self.left.static_curve(math.pi/3)
        end_dict = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.rad}
        result_d = {'x': 861.0254037844387, 'z': -494.99999999999994,
                    'b': math.pi/2}
        self.assertDataAlmostEqual(end_dict, result_d)

    def test_static_curve_right_60(self):
        end = self.right.static_curve(math.pi/3)
        end_dict = {'x': end.pos_x, 'z': end.pos_z, 'b': end.bearing.rad}
        result_d = {'x': -504.99999999999994, 'z': 861.0254037844387,
                    'b': 0}
        self.assertDataAlmostEqual(end_dict, result_d)

if __name__ == "__main__":
    unittest.main()