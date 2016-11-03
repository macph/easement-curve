# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Test script for the Bearing class

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.common


class BearingTests(unittest.TestCase):

    def test_exception_wrong_type(self):
        with self.assertRaisesRegex(ValueError, 'bearing needs to'):
            tb = ec.common.Bearing("AA")

    def test_above_range_deg(self):
        tb = ec.common.Bearing(370)
        self.assertAlmostEqual(tb.deg, 10)

    def test_below_range_deg(self):
        tb = ec.common.Bearing(-10)
        self.assertAlmostEqual(tb.deg, 350)

    def test_above_range_rad(self):
        tb = ec.common.Bearing(2.5*math.pi, rad=True)
        self.assertAlmostEqual(tb.rad, 0.5*math.pi)

    def test_below_range_rad(self):
        tb = ec.common.Bearing(-0.5*math.pi, rad=True)
        self.assertAlmostEqual(tb.rad, 1.5*math.pi)

    def test_set_deg(self):
        tb = ec.common.Bearing(math.pi, rad=True)
        tb.deg = 90
        self.assertAlmostEqual(tb.rad, 0.5*math.pi)

    def test_set_rad(self):
        tb = ec.common.Bearing(180)
        tb.rad = 1.5*math.pi
        self.assertAlmostEqual(tb.deg, 270)

    def test_add_bearing(self):
        t1 = ec.common.Bearing(180)
        t2 = ec.common.Bearing(270)
        tb = t1 + t2
        self.assertAlmostEqual(tb.deg, 90)

    def test_add_float(self):
        t1 = ec.common.Bearing(90)
        t2 = math.pi
        tb = t1 + t2
        self.assertAlmostEqual(tb.deg, 270)

    def test_radd_float(self):
        t1 = math.pi
        t2 = ec.common.Bearing(270)
        tb = t1 + t2
        self.assertAlmostEqual(tb.deg, 90)

    def test_sub_bearing(self):
        t1 = ec.common.Bearing(270)
        t2 = ec.common.Bearing(60)
        tb = t1 - t2
        self.assertAlmostEqual(tb.deg, 210)

    def test_sub_float(self):
        t1 = ec.common.Bearing(0.5*math.pi, rad=True)
        t2 = 0.25*math.pi
        tb = t1 - t2
        self.assertAlmostEqual(tb.deg, 45)

    def test_rsub_float(self):
        t1 = 1.5*math.pi
        t2 = ec.common.Bearing(math.pi, rad=True)
        tb = t1 - t2
        self.assertAlmostEqual(tb.rad, 0.5*math.pi)

    def test_negative(self):
        ta = ec.common.Bearing(135)
        tb = -ta
        self.assertAlmostEqual(tb.deg, 225)

    def test_flip(self):
        t = ec.common.Bearing(135)
        self.assertAlmostEqual(t.flip().deg, 315)

    def test_abs(self):
        t = ec.common.Bearing(135)
        at = abs(t)
        self.assertAlmostEqual((t.deg, at.deg), (135, 135))

    def test_nearly_equal_exactly(self):
        t1, t2 = ec.common.Bearing(180), ec.common.Bearing(math.pi, rad=True)
        self.assertTrue(t1.nearly_equal(t2))

    def test_nearly_equal_def_not(self):
        t1, t2 = ec.common.Bearing(180), ec.common.Bearing(270)
        self.assertFalse(t1.nearly_equal(t2))

    def test_nearly_equal_approx(self):
        t1, t2 = ec.common.Bearing(89.9999995), ec.common.Bearing(90)
        self.assertTrue(t1.nearly_equal(t2))

    def test_nearly_equal_not_approx(self):
        t1, t2 = ec.common.Bearing(90.001), ec.common.Bearing(90.002)
        self.assertFalse(t1.nearly_equal(t2))