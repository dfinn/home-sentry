from logger import Logger
from models.detection_result import DetectionResult
from models.source_definition import SourceDefinition
from notifiers.notifier import Notifier


class ConsoleNotifier(Notifier):

    def notify_detections(self, detection_result: DetectionResult, source_definition: SourceDefinition, log: Logger):
        log.info(f'Detected {detection_result.count()} people')
