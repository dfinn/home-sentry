from typing import List

from shapely.geometry import Polygon

from models.person_detection import PersonDetection
from models.point import Point


class Zone:
    """
    Defines a region of the captured image in which the person detection must occur in
    order to be considered valid.
    """

    def __init__(self, id: str, name: str, points: List[Point]):
        self.id = id
        self.name = name
        self.points = points
        self.polygon = Polygon([point.to_tuple() for point in self.points])

    @staticmethod
    def from_dict(data: dict) -> 'Zone':
        return Zone(
            data['id'],
            data['name'],
            [Point.from_dict(point_data) for point_data in data['points']],
        )

    def contains(self, person_detection: PersonDetection):
        """
        Returns true if the specific PersonDetection is included in or partially overlaps this zone
        """
        person_detection_polygon = Polygon([(person_detection.top_left.x, person_detection.top_left.y),
                                            (person_detection.bottom_right.x, person_detection.top_left.y),
                                            (person_detection.bottom_right.x, person_detection.bottom_right.y),
                                            (person_detection.top_left.x, person_detection.bottom_right.y)])
        return person_detection_polygon.intersects(self.polygon)
