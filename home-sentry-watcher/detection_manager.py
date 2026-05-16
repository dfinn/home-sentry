import os
import time

import cv2
import numpy as np

from config_helper import ConfigHelper
from detectors.detector import Detector
from logger import Logger
from models.detection_result import DetectionResult
from models.exclusion import Exclusion
from notifiers.notifier import Notifier
from sources.videosource import VideoSource
from utils import show_image_foreground, on_mouse_event


class DetectionManager:

    def __init__(self, detector: Detector, notifier: Notifier, config_helper: ConfigHelper):
        self.detector = detector
        self.notifier = notifier
        self.config_helper = config_helper
        self.show_images = config_helper.get_show_images()
        self.save_images = config_helper.get_save_images()
        self.output_folder = config_helper.get_output_folder()
        self.image_resize_width = config_helper.get_image_resize_width()
        self.cool_down_interval = config_helper.get_cool_down_interval()
        self.last_person_detection_exclusion_threshold = config_helper.get_last_person_detection_exclusion_threshold()
        self.last_person_detection_expiration_seconds = config_helper.get_last_person_detection_expiration_seconds()
        self.resize_buffer = None
        os.makedirs(self.output_folder, exist_ok=True)

    def resize_image(self, image: np.array, logger: Logger):
        """
        Resizes the provided image to self.image_resize_width, preserving the aspect ratio.
        Re-uses the resize_buffer after it has been allocated the first time.
        Returns the resized image.
        """
        image_height = image.shape[0]
        image_width = image.shape[1]
        resize_ratio = image_width / self.image_resize_width
        image_resize_height = int(image_height / resize_ratio)
        if self.resize_buffer is None:
            logger.info('Resize buffer not allocated yet, creating it now')
            if len(image.shape) == 2:
                # Black and white
                num_channels = 1
            else:
                # Color
                num_channels = image.shape[2]
            self.resize_buffer = np.empty((self.image_resize_width, image_resize_height, num_channels),
                                          dtype=image.dtype)
        resized_image = cv2.resize(image, dsize=(self.image_resize_width, image_resize_height),
                                   dst=self.resize_buffer)
        logger.verbose(
            f'Resized image from {image_width}x{image_height} to {self.image_resize_width}x{image_resize_height}')
        return resized_image

    def capture_detect_notify(self, video_source: VideoSource):
        source_definition = video_source.source_definition
        log = video_source.log
        log.verbose(f'Capturing image from source {source_definition.name}')
        image = video_source.capture()
        if image is None:
            log.verbose('No image returned, skipping detection')
            return
        resized_image = self.resize_image(image, log)
        del image
        detection_start_time = time.perf_counter()
        detection_result = self.detector.detect(resized_image, video_source)
        detection_elapsed_time = time.perf_counter() - detection_start_time
        should_log = log.is_verbose_mode or detection_result.count() > 0
        self.filter_by_confidence_threshold(detection_result, video_source)
        self.filter_excluded_detections(detection_result, video_source)

        # Determine how many detections are inside of any zone versus outside of any zone
        print(f'calling filter_detection_results_by_zone with {len(detection_result.person_detections)} detections')
        (inside_zone_count, outside_zone_count) = source_definition.filter_detection_results_by_zone(detection_result)

        if should_log:
            log.verbose(
                f'Detection time {detection_elapsed_time:0.4f} seconds, inside_zone_count={inside_zone_count}, '
                f'outside_zone_count={outside_zone_count} [{detection_result}]')
        if inside_zone_count > 0:
            had_recent_detection = False
            if video_source.last_detection_time is not None:
                seconds_since_last_detection = time.time() - video_source.last_detection_time
                time_to_wait = self.cool_down_interval - seconds_since_last_detection
                if seconds_since_last_detection < self.cool_down_interval:
                    had_recent_detection = True
                    log.info('Recent detection occurred, waiting for cool down period before next capture')
            if not had_recent_detection:
                detection_result.draw_boxes()
                self.notifier.notify_detections(detection_result, source_definition, log)
                video_source.last_detection_time = time.time()
                video_source.last_person_detection = detection_result.person_detections[0]
                if self.save_images:
                    dest = f'{self.output_folder}/{source_definition.id}.jpg'
                    log.info(f'Saving {dest}')
                    cv2.imwrite(dest, detection_result.image)
        if self.show_images:
            show_image_foreground(source_definition.name, detection_result.image, on_mouse_event)

    def filter_by_confidence_threshold(self, detection_result: DetectionResult, source: VideoSource):
        """
        Removes any detections from the provided detection_result which have confidence
        below or equal to the confidence_threshold defined for the source.
        """
        threshold = source.source_definition.confidence_threshold
        detections_to_keep = [
            person_detection for person_detection in detection_result.person_detections
            if person_detection.confidence > threshold
        ]
        if len(detections_to_keep) < len(detection_result.person_detections):
            source.log.verbose(
                f'Filtered out {len(detection_result.person_detections) - len(detections_to_keep)} '
                f'detections below confidence threshold {threshold}')
        detection_result.person_detections = detections_to_keep

    def filter_excluded_detections(self, detection_result: DetectionResult, source: VideoSource):
        """
        Removes any detections from the provided detection_result which match any exclusions defined for the source.
        An exclusion is automatically created for the most recent person detection.
        The most recent person detection will expire 1 hour after the last detection at that same location.
        """
        detections_to_keep = []
        exclusions = source.source_definition.exclusions
        log = source.log
        if source.last_person_detection is not None:
            if (
                    time.time() - source.last_person_detection.detection_time) > self.last_person_detection_expiration_seconds:
                log.info('Expiring last person detection')
                source.last_person_detection = None
        last_person_detection = source.last_person_detection
        exclusions = exclusions.copy()
        if last_person_detection is not None:
            last_person_exclusion = Exclusion(id='last_person', name='Last Person Detection',
                                              top_left=last_person_detection.top_left,
                                              bottom_right=last_person_detection.bottom_right,
                                              threshold=self.last_person_detection_exclusion_threshold)
            exclusions.append(last_person_exclusion)
        for person_detection in detection_result.person_detections:
            any_exclusion_matched = False
            for exclusion in exclusions:
                matches_exclusion = person_detection.matches_exclusion(exclusion)
                log.verbose(
                    f'Checking detection {person_detection} against exclusion {exclusion}: match={matches_exclusion}')
                if matches_exclusion:
                    log.verbose('Exclusion matched')
                    any_exclusion_matched = True
                    # If this exclusion was from the last person detection, then update the last person detection time.
                    if exclusion.id == 'last_person':
                        log.info(f'Updating last_person detection time to {time.time()}')
                        source.last_person_detection.detection_time = time.time()
                    break
            if not any_exclusion_matched:
                print('No exclusions matched, appending to detections_to_keep')
                detections_to_keep.append(person_detection)
        print(f'Returning from filter_excluded_detections with {len(detections_to_keep)} detections_to_keep')
        detection_result.person_detections = detections_to_keep
