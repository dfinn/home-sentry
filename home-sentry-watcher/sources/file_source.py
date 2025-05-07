import cv2

from models.source_definition import SourceDefinition
from sources.videosource import VideoSource


class FileSource(VideoSource):

    def __init__(self, source_id: str, url: str, log_verbose):
        super().__init__(SourceDefinition(id='file_source', name=f'File: {url}', type='file', url=url, enabled=True, exclusions=[], zones=[]), log_verbose)
        self.image = cv2.imread(url)
        if self.image is None:
            raise ValueError(f'FileSource failed to load file "{url}"')

    def capture(self):
        return self.image
