# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Test script for the TrackCoord class

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.coord


class CoordGeneralTests(unittest.TestCase):

    def test_position(self):
        tc = ec.coord.TrackCoord(5, 5, 0, ec.coord.Q.NONE, curvature=0)
        self.assertEqual((tc.pos_x, tc.pos_z), (5, 5))

    def test_exception_position(self):
        with self.assertRaisesRegex(ec.coord.CoordError, 'Position values'):
            ec.coord.TrackCoord(None, 5, 0, ec.coord.Q.NONE, curvature=0)


class CoordBearingTests(unittest.TestCase):

    def test_exception_rotation_over_range(self):
        with self.assertRaisesRegex(ec.coord.CoordError, 'y-axis rotation'):
            ec.coord.TrackCoord(0, 0, 100, ec.coord.Q.NE, curvature=0)

    def test_exception_rotation_under_range(self):
        with self.assertRaisesRegex(ec.coord.CoordError, 'y-axis rotation'):
            ec.coord.TrackCoord(0, 0, -100, ec.coord.Q.NE, curvature=0)

    def test_exception_wrong_bearing(self):
        with self.assertRaisesRegex(ValueError, 'bearing needs to'):
            ec.coord.TrackCoord(0, 0, None, ec.coord.Q.NONE, curvature=0)

    def test_exception_wrong_quad(self):
        with self.assertRaisesRegex(ec.coord.CoordError, 'compass quadrant'):
            ec.coord.TrackCoord(0, 0, 0, quad="A")

    def test_quad_ne(self):
        tc = ec.coord.TrackCoord(0, 0, 30, ec.coord.Q.NE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 30)

    def test_quad_se(self):
        tc = ec.coord.TrackCoord(0, 0, 30, ec.coord.Q.SE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 150)

    def test_quad_sw(self):
        tc = ec.coord.TrackCoord(0, 0, 30, ec.coord.Q.SW, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 210)

    def test_quad_nw(self):
        tc = ec.coord.TrackCoord(0, 0, 30, ec.coord.Q.NW, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 330)

    def test_quad_neg(self):
        tc = ec.coord.TrackCoord(0, 0, -60, ec.coord.Q.NE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 60)

    def test_bearing(self):
        tc = ec.coord.TrackCoord(0, 0, math.pi, ec.coord.Q.NONE, curvature=0)
        self.assertAlmostEqual(tc.bearing.deg, 180)


class CoordCurvatureTests(unittest.TestCase):

    def test_radius_straight(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=0)
        self.assertEqual(tc.radius, 0)

    def test_radius_left(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=0.01)
        self.assertEqual(tc.radius, 100)

    def test_radius_right(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=-0.01)
        self.assertEqual(tc.radius, 100)

    def test_clockwise_straight(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=0)
        self.assertEqual(tc.clockwise, 'straight')

    def test_clockwise_acw(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=0.01)
        self.assertEqual(tc.clockwise, 'ACW')

    def test_clockwise_cw(self):
        tc = ec.coord.TrackCoord(0, 0, 0, ec.coord.Q.NONE, curvature=-0.01)
        self.assertEqual(tc.clockwise, 'CW')

    def test_get_quad_ne(self):
        tc = ec.coord.TrackCoord(0, 0, math.pi / 6, ec.coord.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 30)
        self.assertEqual(q, ec.coord.Q.NE.name)

    def test_get_quad_se(self):
        tc = ec.coord.TrackCoord(0, 0, math.pi * (4 / 6), ec.coord.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 60)
        self.assertEqual(q, ec.coord.Q.SE.name)

    def test_get_quad_sw(self):
        tc = ec.coord.TrackCoord(0, 0, math.pi * (8 / 6), ec.coord.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 60)
        self.assertEqual(q, ec.coord.Q.SW.name)

    def test_get_quad_nw(self):
        tc = ec.coord.TrackCoord(0, 0, math.pi * (11 / 6), ec.coord.Q.NONE, curvature=0)
        r, q = tc.quad
        self.assertAlmostEqual(r, 30)
        self.assertEqual(q, ec.coord.Q.NW.name)
