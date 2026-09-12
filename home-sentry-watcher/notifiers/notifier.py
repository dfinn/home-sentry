from logger import Logger
from models.detection_result import DetectionResult
from models.source_definition import SourceDefinition


class Notifier:

    def notify_detections(self, detection_result: DetectionResult, source_definition: SourceDefinition, log: Logger):
        pass
