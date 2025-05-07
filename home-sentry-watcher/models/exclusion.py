import uuid

from models.point import Point


class Exclusion:
    """
    Represents one bounding box (top left, bottom right) for a detection that should not trigger a notification.
    Has a threshold (0.0 - 1.0) representing the percentage of allowed deviation of each point.
    """

    def __init__(self, id: str, name: str, top_left: Point, bottom_right: Point, threshold: float):
        self.id = id
        self.name = name
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.threshold = threshold

    def __str__(self):
        return f'name={self.name}, tl={self.top_left}, br={self.bottom_right}, threshold={self.threshold}'

    @staticmethod
    def from_dict(data: dict) -> 'Exclusion':
        return Exclusion(
            data['id'] if 'id' in data else uuid.uuid4(),
            data['name'],
            Point.from_dict(data['top_left']),
            Point.from_dict(data['bottom_right']),
            data['threshold']
        )
