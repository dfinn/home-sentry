import time
import unittest

import shapely.geometry

from models.person_detection import PersonDetection
from models.point import Point
from models.zone import Zone

zone = Zone('zone1', 'Zone 1', [Point(0.0, 0.496),
                                Point(0.789, 0.296),
                                Point(1.0, 0.535),
                                Point(1.0, 1.0),
                                Point(0.0, 1.0)])


class TestZones(unittest.TestCase):

    def test_point_in_polygon(self):
        point = shapely.geometry.Point(15, 15)
        poly = shapely.geometry.Polygon([(10, 10), (20, 10), (20, 20), (10, 20)])
        self.assertTrue(poly.contains(point))

    def test_detection_result_not_in_zone(self):
        person_detection = PersonDetection(Point(0.110, 0.151), Point(0.135, 0.190), .95, time.time())
        self.assertFalse(zone.contains(person_detection))

    def test_detection_result_in_zone(self):
        person_detection = PersonDetection(Point(0.316, 0.477), Point(0.376, 0.553), .95, time.time())
        self.assertTrue(zone.contains(person_detection))

    def test_detection_result_partially_in_zone(self):
        person_detection = PersonDetection(Point(0.260, 0.266), Point(0.457, 0.492), .95, time.time())
        self.assertTrue(zone.contains(person_detection))
