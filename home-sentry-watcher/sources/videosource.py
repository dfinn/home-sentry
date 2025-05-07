from typing import Optional

import numpy as np

from models.person_detection import PersonDetection
from logger import Logger
from models.source_definition import SourceDefinition


class VideoSource:

    def __init__(self, source_definition: SourceDefinition, log_verbose):
        self.source_definition = source_definition
        self.id = source_definition.id
        self.last_detection_time: Optional[float] = None
        self.last_person_detection: PersonDetection = None
        self.log = Logger(self.id, log_verbose)

    def capture(self) -> np.array:
        """
        Capture an image from the source and return it as a numpy image
        :return:
        """
        pass

    def shutdown(self):
        pass
