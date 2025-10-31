import tempfile
import time
from unittest import TestCase
from unittest.mock import Mock

import numpy as np

from config_helper import ConfigHelper
from detection_manager import DetectionManager
from detectors.detector import Detector
from models.detection_result import DetectionResult
from models.exclusion import Exclusion
from models.person_detection import PersonDetection
from models.point import Point
from models.source_definition import SourceDefinition
from sources.fake_source import FakeSource
from sources.source_manager import SourceManager
from tests.helpers.test_notifier import TestNotifier

SOURCE_ID = 'test_source'
SOURCE_NAME = 'Test Source'
IMAGE = np.zeros((480, 640))


class TestDetectionManager(TestCase):

    def init(self, exclusion):
        source_definition = SourceDefinition(id=SOURCE_ID, name=SOURCE_NAME, type='test', url='test', enabled=True,
                                             exclusions=[exclusion], zones=[], confidence_threshold=0.5)
        self.video_source = FakeSource(source_definition, True)
        self.detector: Detector = Mock()
        source_manager: SourceManager = Mock()
        self.test_notifier = TestNotifier()
        self.config_helper: ConfigHelper = Mock()
        self.config_helper.get_image_resize_width.return_value = 640
        self.config_helper.get_save_images.return_value = False
        self.config_helper.get_show_images.return_value = False
        self.config_helper.get_output_folder.return_value = tempfile.mkdtemp()
        self.config_helper.get_cool_down_interval.return_value = 0
        self.config_helper.get_last_person_detection_exclusion_threshold.return_value = 0.05
        self.config_helper.get_last_person_detection_expiration_seconds.return_value = 60
        source_manager.get_source_definition = Mock(return_value=source_definition)
        self.detection_manager = DetectionManager(detector=self.detector, notifier=self.test_notifier,
                                                  config_helper=self.config_helper)

    def test_excluded_detection_is_filtered_exact_match(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.250, 0.333),
                            bottom_right=Point(0.303, 0.464), threshold=.1))
        person_detections = [PersonDetection(Point(0.250, 0.333), Point(0.303, 0.464), .95, time.time())]
        detection_result = DetectionResult(person_detections, IMAGE)
        self.assertEqual(1, detection_result.count())
        self.detection_manager.filter_excluded_detections(detection_result, self.video_source)
        self.assertEqual(0, detection_result.count())

    def test_excluded_detection_is_filtered_near_match(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.250, 0.333),
                            bottom_right=Point(0.303, 0.464), threshold=.1))
        person_detections = [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())]
        detection_result = DetectionResult(person_detections, IMAGE)
        self.assertEqual(1, detection_result.count())
        self.detection_manager.filter_excluded_detections(detection_result, self.video_source)
        self.assertEqual(0, detection_result.count())

    def test_non_excluded_detection_is_not_filtered(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        person_detections = [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())]
        detection_result = DetectionResult(person_detections, IMAGE)
        self.assertEqual(1, detection_result.count())
        self.detection_manager.filter_excluded_detections(detection_result, self.video_source)
        self.assertEqual(1, detection_result.count())

    def test_notification_sent_when_person_detected(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)

    def test_notification_not_sent_when_person_detected_at_same_location_as_previous(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)

    def test_notification_sent_when_person_detected_at_different_location_as_previous(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.5, 0.5), Point(0.8, 0.8), .95, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(2, self.test_notifier.num_notifications)

    def test_notification_sent_after_last_person_detection_expires(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), .95, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)
        self.video_source.last_person_detection.detection_time = 0
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(2, self.test_notifier.num_notifications)

    def test_notification_not_sent_when_confidence_below_threshold(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        # Source has confidence_threshold=0.5, detection has confidence=0.4 (below threshold)
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), 0.4, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(0, self.test_notifier.num_notifications)

    def test_notification_sent_when_confidence_above_threshold(self):
        self.init(Exclusion(id='test_exclusion', name='Test Exclusion', top_left=Point(0.8, 0.8),
                            bottom_right=Point(0.9, 0.9), threshold=.1))
        # Source has confidence_threshold=0.5, detection has confidence=0.6 (above threshold)
        self.detector.detect.return_value = DetectionResult(
            [PersonDetection(Point(0.21, 0.25), Point(0.31, 0.49), 0.6, time.time())], IMAGE)
        self.detection_manager.capture_detect_notify(self.video_source)
        self.assertEqual(1, self.test_notifier.num_notifications)
