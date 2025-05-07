from unittest import TestCase

from models.point import Point


class TestPoint(TestCase):

    def test_y_is_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(.7, .2)
        self.assertTrue(p1.is_near_point(p2, .1))

    def test_x_is_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(.8, .3)
        self.assertTrue(p1.is_near_point(p2, .1))

    def test_x_and_y_are_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(.5, .5)
        self.assertTrue(p1.is_near_point(p2, .2))

    def test_x_not_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(.5, .3)
        self.assertFalse(p1.is_near_point(p2, .1))

    def test_y_not_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(.8, 1.0)
        self.assertFalse(p1.is_near_point(p2, .1))

    def test_x_and_y_not_within_threshold(self):
        p1 = Point(.7, .3)
        p2 = Point(0, .001)
        self.assertFalse(p1.is_near_point(p2, .1))
