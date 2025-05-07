from models.exclusion import Exclusion
from models.point import Point


class PersonDetection:

    def __init__(self, top_left: Point, bottom_right: Point, confidence: float, detection_time: float):
        self.top_left: Point = top_left
        self.bottom_right: Point = bottom_right
        self.confidence = confidence
        self.detection_time = detection_time

    def __str__(self):
        return f'tl={self.top_left}, br={self.bottom_right}, conf={self.confidence:0.3f}'

    def matches_exclusion(self, exclusion: Exclusion):
        tl_match = self.top_left.is_near_point(exclusion.top_left, exclusion.threshold)
        br_match = self.bottom_right.is_near_point(exclusion.bottom_right, exclusion.threshold)
        return tl_match and br_match
