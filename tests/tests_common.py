# Ewan Macpherson September 2016
# Test script for the easement_curves script

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import ec.common
import ec.curve


class CustomAssertions(object):
    """ Custom assertions for use with unittest."""

    @staticmethod
    def assertDataAlmostEqual(first, second, places=7, msg=''):
        """ Checks if dict with same set of keys have values that is
            approximately equal to x places (default 7). Can use tuples
            or lists too, as long as they are of the same length.
        """
        if first == second:
            return

        try:
            first.items()
        except AttributeError:
            if len(first) != len(second):
                raise TypeError("Both list/tuples must be of the same length.")
            else:
                first = {i: first[i] for i in range(len(first))}
                second = {i: second[i] for i in range(len(second))}
        else:
            if set(first) != set(second):
                raise TypeError("Both dicts must have the same set of keys.")

        ls_inequalities = []
        for k in first.keys():
            if round(first[k] - second[k], places) != 0:
                try:
                    line = '{k!r}: {f:.{p}f} != {s:.{p}f}'.format(k=k, f=first[k], s=second[k], p=places)
                except ValueError:
                    line = '{k!r}: {f!r} != {s!r}'.format(k=k, f=first[k], s=second[k])
                ls_inequalities.append(line)

        if not ls_inequalities:
            return
        else:
            message = '\n'.join([msg] + ls_inequalities)
            raise AssertionError(message)


class TransformTests(unittest.TestCase, CustomAssertions):

    ts = ec.curve.TrackSection

    def test_no_movement(self):
        start = (4, 3)
        self.assertEqual(ec.common.transform(a=start, r=0), start)

    def test_positive_rotation(self):
        start = (4, 3)
        end = ec.common.transform(a=start, r=0.643501108793)
        self.assertDataAlmostEqual(end, (5, 0))

    def test_negative_rotation(self):
        start = (4, 3)
        end = ec.common.transform(a=start, r=-2.498091544797)
        self.assertDataAlmostEqual(end, (-5, 0))

    def test_rotation_bearing(self):
        start, rotation = (4, -3), ec.common.Bearing(-2.214297435588, rad=True)
        end = ec.common.transform(a=start, r=rotation)
        self.assertDataAlmostEqual(end, (0, 5))

    def test_rotation_other_place(self):
        start, axis, rotation = (6, 7), (-6, 2), 0.394791119700
        end = ec.common.transform(a=start, b=axis, r=rotation)
        self.assertDataAlmostEqual(end, (7, 2))

    def test_translation_no_rotation(self):
        start, translation = (2, 2), (-6, 10)
        end = ec.common.transform(a=start, r=0, c=translation)
        self.assertDataAlmostEqual(end, (-4, 12))

    def test_rotation_translation(self):
        start, translation, rotation = (12, 5), (-6, 3), -1.176005207095
        end = ec.common.transform(a=start, r=rotation, c=translation)
        self.assertDataAlmostEqual(end, (-6, 16))

    def test_all_three(self):
        start, axis, translation = (10, 4), (-5, 12), (3, 20)
        rotation = 1.080839000541
        end = ec.common.transform(a=start, r=rotation, b=axis, c=translation)
        self.assertDataAlmostEqual(end, (3, 3))


class LinearEquationBaseTests(unittest.TestCase):

    def test_exception_no_tuple(self):
        with self.assertRaisesRegex(TypeError, 'tuple of length 2'):
            b = ec.common.Bearing(0)
            le = ec.common.LinearEquation(b, 0)

    def test_exception_wrong_value(self):
        with self.assertRaisesRegex(TypeError, 'tuple of length 2'):
            b = ec.common.Bearing(0)
            le = ec.common.LinearEquation(b, None)

    def test_exception_bearing_number(self):
        with self.assertRaisesRegex(AttributeError, 'Bearing object'):
            le = ec.common.LinearEquation(1, (0, 0))

    def test_exception_bearing_none(self):
        with self.assertRaisesRegex(AttributeError, 'Bearing object'):
            le = ec.common.LinearEquation(None, (0, 0))

    def test_le_bearing(self):
        b = ec.common.Bearing(90)
        le = ec.common.LinearEquation(b, (10, 23))
        self.assertEqual(le.b, math.pi/2)

    def test_le_position(self):
        b = ec.common.Bearing(math.pi, rad=True)
        le = ec.common.LinearEquation(b, (-4, 5))
        self.assertEqual((le.u, le.v), (-4, 5))


class LinearEquationMethodTests(unittest.TestCase):

    def setUp(self):
        self.b = ec.common.Bearing(60)
        self.le = ec.common.LinearEquation(self.b, (-4, 5))

    def tearDown(self):
        del self.b, self.le

    def test_x(self):
        self.assertAlmostEqual(self.le.x(6), math.sqrt(3)-4)

    def test_y(self):
        self.assertAlmostEqual(self.le.y(-4-2*math.sqrt(3)), 3)

    def test_dist_at_point(self):
        self.assertAlmostEqual(self.le.dist((-4, 5)), 0)

    def test_dist_on_line(self):
        self.assertAlmostEqual(self.le.dist((3*math.sqrt(3)-4, 8)), 0)

    def test_dist_y_axis(self):
        p = (0, -1.92820323028)
        self.assertAlmostEqual(self.le.dist(p), 8)

    def test_both_same_side(self):
        p1, p2 = (0, 0), (-1, -1)
        self.assertTrue(self.le.same_side(p1, p2))

    def test_opposite_sides(self):
        p1, p2 = (0, 0), (-5, 5)
        self.assertFalse(self.le.same_side(p1, p2))

    def test_side_both_on_line(self):
        p1, p2 = (-4, 5), (3*math.sqrt(3)-4, 8)
        self.assertTrue(self.le.same_side(p1, p2))

    def test_side_one_on_line(self):
        p1, p2 = (-1, -1), (-4, 5)
        self.assertTrue(self.le.same_side(p1, p2))

    def test_side_other_on_line(self):
        p1, p2 = (-4, 5), (-5, 5)
        self.assertTrue(self.le.same_side(p1, p2))


class LinearEquationIntersectTests(unittest.TestCase, CustomAssertions):

    def setUp(self):
        self.b = [ec.common.Bearing(i) for i in [0, 60, 90, 120, 180, 270]]
        self.le = ec.common.LinearEquation(self.b[1], (-4, 5))

    def tearDown(self):
        del self.b, self.le

    def test_exception_intersect_parallel(self):
        with self.assertRaisesRegex(ValueError, 'cannot be parallel'):
            le0 = ec.common.LinearEquation(self.b[3], (0, -5))
            le1 = ec.common.LinearEquation(self.b[3], (-5, 0))
            le0.intersect(le1)

    def test_exception_parallel_opposite(self):
        with self.assertRaisesRegex(ValueError, 'cannot be parallel'):
            le0 = ec.common.LinearEquation(self.b[2], (0, -5))
            le1 = ec.common.LinearEquation(self.b[5], (-5, 0))
            le0.intersect(le1)

    def test_exception_intersect_wrong_object(self):
        with self.assertRaisesRegex(AttributeError, 'be a LinearEquation'):
            le0 = ec.common.LinearEquation(self.b[3], (0, -5))
            le0.intersect(None)

    def test_intersect_both_orthogonal_1(self):
        le0 = ec.common.LinearEquation(self.b[0], (5, 0))
        le1 = ec.common.LinearEquation(self.b[2], (0, -4))
        self.assertEqual(le0.intersect(le1), (5, -4))

    def test_intersect_both_orthogonal_2(self):
        le0 = ec.common.LinearEquation(self.b[2], (7, 2))
        le1 = ec.common.LinearEquation(self.b[4], (-4, 5))
        self.assertEqual(le0.intersect(le1), (-4, 2))

    def test_intersect_one_orthogonal_1(self):
        le0 = ec.common.LinearEquation(self.b[2], (5, 2))
        le1 = ec.common.LinearEquation(self.b[3], (6, -2))
        self.assertDataAlmostEqual(le0.intersect(le1), (-0.928203230276, 2))

    def test_intersect_one_orthogonal_2(self):
        le0 = ec.common.LinearEquation(self.b[4], (-7, 6))
        le1 = ec.common.LinearEquation(self.b[3], (3, -1))
        self.assertDataAlmostEqual(le0.intersect(le1), (-7, 4.7735026919))

    def test_intersect_none_orthogonal(self):
        le0 = ec.common.LinearEquation(self.b[1], (10, -3))
        le1 = ec.common.LinearEquation(self.b[3], (-5, -2))
        axes, intersect = ('x', 'z'), le0.intersect(le1)
        self.assertDataAlmostEqual(le0.intersect(le1), (3.36602540378, -6.83012701892))