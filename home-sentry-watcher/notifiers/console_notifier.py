from models.detection_result import DetectionResult
from notifiers.notifier import Notifier


class ConsoleNotifier(Notifier):

    def notify_detections(self, detection_result: DetectionResult, source_name: str):
        print(f'Detected {detection_result.count()} people -- {source_name}')
