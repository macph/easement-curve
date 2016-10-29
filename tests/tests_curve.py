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


class BaseTCTests(unittest.TestCase, CustomAssertions):

    def setUp(self):
        minimum_high, speed_high = 500, 120
        minimum_low, speed_low = 200, 80

        self.start_straight = ec.curve.TrackCoord(
            pos_x=217.027, pos_z=34.523, rotation=48.882, quad=ec.curve.Q.NE, curvature=0)
        self.start_curved = ec.curve.TrackCoord(
            pos_x=354.667, pos_z=137.112, rotation=59.824, quad=ec.curve.Q.NE, curvature=0)
        self.start_curved_add = ec.curve.TrackCoord(
            pos_x=287.741, pos_z=92.965, rotation=53.356, quad=ec.curve.Q.NE, curvature=0)

        self.end_left = ec.curve.TrackCoord(
            pos_x=467.962, pos_z=465.900, rotation=12.762, quad=ec.curve.Q.NE, curvature=0)
        self.end_right = ec.curve.TrackCoord(
            pos_x=582.769, pos_z=223.772, rotation=75.449, quad=ec.curve.Q.NE, curvature=0)

        # For curves with diff > 270
        self.end_far_left = ec.curve.TrackCoord(
            pos_x=-123.550, pos_z=199.813, rotation=5.913, quad=ec.curve.Q.SW, curvature=0)
        # To test low RoC with low angle diff - should raise exception
        self.end_low_angle = ec.curve.TrackCoord(
            pos_x=554.679, pos_z=226.288, rotation=65.670, quad=ec.curve.Q.NE, curvature=0)

        self.straight_high = ec.curve.TrackCurve(self.start_straight, minimum_high, speed_high)
        self.straight_low = ec.curve.TrackCurve(self.start_straight, minimum_low, speed_low)
        self.left = ec.curve.TrackCurve(self.start_curved, minimum_high, speed_high)

    def tearDown(self):
        del self.start_straight, self.start_curved, self.start_curved_add
        del self.end_left, self.end_right, self.end_far_left, self.end_low_angle
        del self.straight_high, self.straight_low, self.left