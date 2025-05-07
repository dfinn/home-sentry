from models.detection_result import DetectionResult
from notifiers.notifier import Notifier


class TestNotifier(Notifier):
    """
    Notifier used for testing which prints to the console and keeps a running count of notifications sent.
    """
    def __init__(self):
        self.num_notifications = 0
        pass

    def notify_detections(self, detection_result: DetectionResult, source_name: str):
        self.num_notifications += 1
        print(f'TestNotifier: detected {detection_result.count()} people -- {source_name}')
