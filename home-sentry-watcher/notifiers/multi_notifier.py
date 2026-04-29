from typing import List

from notifiers.notifier import Notifier
from models.detection_result import DetectionResult


class MultiNotifier(Notifier):

    def __init__(self, notifiers: List[Notifier]):
        self.notifiers = notifiers

    def notify_detections(self, detection_result: DetectionResult, source_name: str):
        for notifier in self.notifiers:
            detections_str = ', '.join(str(p) for p in detection_result.person_detections)
            print(f'[{source_name}] Sending notification via {type(notifier).__name__}: {detections_str}')
            notifier.notify_detections(detection_result, source_name)
