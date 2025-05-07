import sys

from config_helper import ConfigHelper
from detection_manager import DetectionManager
from notifiers.console_notifier import ConsoleNotifier
from sources.file_source import FileSource

if len(sys.argv) < 3:
    print('Must specify config directory and input filename')
    exit(1)

config_directory = sys.argv[1]
input_filename = sys.argv[2]
config_helper = ConfigHelper(config_directory)
detector = config_helper.get_detector()
console_notifier = ConsoleNotifier()
detection_manager = DetectionManager(detector, console_notifier, config_helper)

file_source = FileSource('file_source', input_filename, True)
detection_manager.capture_detect_notify(file_source)
