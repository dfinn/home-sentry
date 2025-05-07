import numpy as np

from models.detection_result import DetectionResult
from sources.videosource import VideoSource


class Detector:
    """
    Base class for detectors
    """

    def detect(self, numpy_image: np.array, video_source: VideoSource) -> DetectionResult:
        """
        Run detection and look for people in the input image (in numpy format).
        :param numpy_image: Input image on which to run detection
        :param video_source: The video source that generated the image
        :return: A DetectionResult
        """
        pass
