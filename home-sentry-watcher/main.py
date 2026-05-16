import sys

import cv2

from config_helper import ConfigHelper
from detection_manager import DetectionManager
from sources.source_manager import SourceManager

with open('version.txt') as f:
    version = f.readline()
    print(f'Home Sentry Watcher version {version} starting up')

if len(sys.argv) < 2:
    print('Must specify config directory')
    exit(1)

config_directory = sys.argv[1]
config_helper = ConfigHelper(config_directory)
source_manager = SourceManager(config_helper, config_helper.get_backend_url(), config_helper.get_backend_ws_url(),
                               config_helper.get_backend_api_key())
detector = config_helper.get_detector()
notifier = config_helper.get_notifier()
video_sources = source_manager.build_video_sources()
show_images = config_helper.get_show_images()
detection_manager = DetectionManager(detector, notifier, config_helper)

print('Starting main capture loop')
while True:
    for source in video_sources:
        detection_manager.capture_detect_notify(source)
    if show_images:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

for source in video_sources:
    source.shutdown()

source_manager.shutdown()
