import numpy as np

from models.source_definition import SourceDefinition
from sources.videosource import VideoSource


class FakeSource(VideoSource):
    """
    Fake source for testing purposes which returns a blank image
    """

    def __init__(self, source_definition: SourceDefinition, log_verbose: bool):
        super().__init__(source_definition, log_verbose)

    def capture(self) -> np.array:
        return np.zeros((480, 640))
