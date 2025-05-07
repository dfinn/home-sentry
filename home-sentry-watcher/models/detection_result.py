from typing import List

import cv2
import numpy as np

from models.person_detection import PersonDetection


class DetectionResult:

    def __init__(self, person_detections: List[PersonDetection], image: np.array):
        """
        :param person_detections: An array of PersonDetection
        """
        self.person_detections: List[PersonDetection] = person_detections
        self.image: np.array = image

    def __str__(self):
        str_val = ''
        for d in self.person_detections:
            if len(str_val) > 0:
                str_val += ', '
            str_val += f'({d})'
        return str_val

    def count(self) -> int:
        return len(self.person_detections)

    def draw_boxes(self):
        for pd in self.person_detections:
            tl = pd.top_left.relative_coords_to_abs(self.image).to_tuple()
            br = pd.bottom_right.relative_coords_to_abs(self.image).to_tuple()
            cv2.rectangle(self.image, tl, br, (0, 255, 0), 2)
