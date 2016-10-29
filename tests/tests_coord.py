# Ewan Macpherson September 2016
# Test script for the TrackCoord class

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.curve


class CoordGeneralTests(unittest.TestCase):

    def test_position(self):
        tc = ec.curve.TrackCoord(5, 5, 0, ec.curve.Q.NONE, curvature=0)
        self.assertEqual((tc.pos_x, tc.pos_z), (5, 5))

    def test_exception_position(self):
        with self.assertRaisesRegex(ec.curve.CoordException, 'Position values'):
            tc = ec.curve.TrackCoord(None, 5, 0, ec.curve.Q.NONE, curvature=0)


class CoordBearingTests(unittest.TestCase):

    def test_exception_rotation_over_range(self):
        with self.assertRaisesRegex(ec.curve.CoordException, 'y-axis rotation'):
            tc = ec.curve.TrackCoord(0, 0, 100, ec.curve.Q.NE, curvature=0)

    def test_exception_rotation_under_range(self):
        with self.assertRaisesRegex(ec.curve.CoordException, 'y-axis rotation'):
            tc = ec.curve.TrackCoord(0, 0, -100, ec.curve.Q.NE, curvature=0)

    def test_exception_wrong_bearing(self):
        with self.assertRaisesRegex(ValueError, 'bearing needs to'):
            tc = ec.curve.TrackCoord(0, 0, None, ec.curve.Q.NONE, curvature=0)

    def test_exception_wrong_quad(self):
        with self.assertRaisesRegex(ec.curve.CoordException, 'compass quadrant'):
            tc = ec.curve.TrackCoord(0, 0, 0, quad="A")

    def test_quad_ne(self):
        tc = ec.curve.TrackCoord(0, 0, 30, ec.curve.Q.NE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 30)

    def test_quad_se(self):
        tc = ec.curve.TrackCoord(0, 0, 30, ec.curve.Q.SE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 150)

    def test_quad_sw(self):
        tc = ec.curve.TrackCoord(0, 0, 30, ec.curve.Q.SW, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 210)

    def test_quad_nw(self):
        tc = ec.curve.TrackCoord(0, 0, 30, ec.curve.Q.NW, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 330)

    def test_quad_neg(self):
        tc = ec.curve.TrackCoord(0, 0, -60, ec.curve.Q.NE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 60)

    def test_bearing(self):
        tc = ec.curve.TrackCoord(0, 0, math.pi, ec.curve.Q.NONE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 180)


class CoordCurvatureTests(unittest.TestCase):

    def test_radius_straight(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=0)
        self.assertEqual(tc.radius, 0)

    def test_radius_left(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=0.01)
        self.assertEqual(tc.radius, 100)

    def test_radius_right(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=-0.01)
        self.assertEqual(tc.radius, 100)

    def test_clockwise_straight(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=0)
        self.assertEqual(tc.clockwise, 'straight')

    def test_clockwise_acw(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=0.01)
        self.assertEqual(tc.clockwise, 'ACW')

    def test_clockwise_cw(self):
        tc = ec.curve.TrackCoord(0, 0, 0, ec.curve.Q.NONE, curvature=-0.01)
        self.assertEqual(tc.clockwise, 'CW')

    def test_get_quad_ne(self):
        tc = ec.curve.TrackCoord(0, 0, math.pi / 6, ec.curve.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 30)
        self.assertEqual(q, ec.curve.Q.NE.name)

    def test_get_quad_se(self):
        tc = ec.curve.TrackCoord(0, 0, math.pi * (4 / 6), ec.curve.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 60)
        self.assertEqual(q, ec.curve.Q.SE.name)

    def test_get_quad_sw(self):
        tc = ec.curve.TrackCoord(0, 0, math.pi * (8 / 6), ec.curve.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 60)
        self.assertEqual(q, ec.curve.Q.SW.name)

    def test_get_quad_nw(self):
        tc = ec.curve.TrackCoord(0, 0, math.pi * (11 / 6), ec.curve.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 30)
        self.assertEqual(q, ec.curve.Q.NW.name)