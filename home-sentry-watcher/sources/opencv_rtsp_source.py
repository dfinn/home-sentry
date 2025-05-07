from threading import Thread
from time import sleep

import cv2
import numpy as np

from models.source_definition import SourceDefinition
from sources.videosource import VideoSource


class OpenCvRtspSource(VideoSource):

    def __init__(self, source_definition: SourceDefinition, url: str, log_verbose):
        super().__init__(source_definition, log_verbose)
        self.url = url
        self.capturer = cv2.VideoCapture(url)
        # Retain only the latest frame to reduce memory usage.
        self.capturer.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.latest_frame = None
        self.shutdown_requested = False
        self.capture_thread = Thread(target=self.capture_loop)
        self.capture_thread.start()

    def capture_loop(self):
        self.log.info('Capture thread started')
        while not self.shutdown_requested:
            ret, frame = self.capturer.read()
            if not ret:
                self.log.info('*** WARNING: read() returned false, restarting RTSP capture')
                sleep(1)
                self.capturer.release()
                self.capturer = cv2.VideoCapture(self.url)
                self.log.info('*** Video capturer has been restarted.')
                continue
            self.latest_frame = frame
        self.capturer.release()

    def shutdown(self):
        self.log.info('Shutting down capture thread')
        self.shutdown_requested = True
        self.capture_thread.join()
        self.log.info('Shutdown completed')

    def capture(self) -> np.array:
        return self.latest_frame
