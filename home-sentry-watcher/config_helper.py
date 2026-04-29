import json

from notifiers.console_notifier import ConsoleNotifier
from notifiers.mqtt_notifier import MqttNotifier
from notifiers.multi_notifier import MultiNotifier
from notifiers.telegram_notifier import TelegramNotifier
from notifiers.zoneminder_notifier import ZoneMinderNotifier

SETTINGS = "settings.json"
DETECTOR = "detector.json"
NOTIFICATIONS = "notifications.json"


class ConfigHelper:

    def __init__(self, config_directory):
        print(f'Using config directory {config_directory}')
        self.config_directory = config_directory.rstrip('/')
        self.settings = None
        self.detector = None
        self.notifications = None
        self.sources = None
        self.load_all_configs()

    def load_all_configs(self):
        self.settings = self.load_from_json_config_file(SETTINGS)
        self.detector = self.load_from_json_config_file(DETECTOR)
        self.notifications = self.load_from_json_config_file(NOTIFICATIONS)

    def load_config_file_contents(self, config_file):
        path = self.get_config_file_path(config_file)
        print(f'Loading from config file {path}')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_from_json_config_file(self, config_file):
        data = self.load_config_file_contents(config_file)
        return json.loads(data)

    def get_config_file_path(self, config_section):
        return self.config_directory + '/' + config_section

    def get_detector(self):
        config = self.detector['config']
        if 'name' not in self.detector:
            raise KeyError('Missing required detector/name section in config')
        detector_name = self.detector['name']
        print(f'Detector name: {detector_name}')
        if detector_name == 'pytorch':
            from detectors.pytorch_detector import PyTorchDetector
            return PyTorchDetector(config)
        else:
            raise KeyError(f'Invalid detector name "{detector_name}"')

    def get_notifier(self):
        destinations = self.notifications['destinations']
        print(f'Notification destinations: {destinations}')
        notifiers = [self._build_notifier(d) for d in destinations]
        return MultiNotifier(notifiers)

    def _build_notifier(self, destination):
        if destination == 'mqtt':
            if 'mqtt' not in self.notifications:
                raise KeyError('Missing required notifications/mqtt section in config')
            mqtt_config = self.notifications['mqtt']
            return MqttNotifier(mqtt_config['hostname'], mqtt_config['username'], mqtt_config['password'])
        elif destination == 'telegram':
            if 'telegram' not in self.notifications:
                raise KeyError('Missing required notifications/telegram section in config')
            telegram_config = self.notifications['telegram']
            return TelegramNotifier(telegram_config['token'], telegram_config['chat_id'])
        elif destination == 'zoneminder':
            if 'zoneminder' not in self.notifications:
                raise KeyError('Missing required notifications/zoneminder section in config')
            zm_config = self.notifications['zoneminder']
            return ZoneMinderNotifier(zm_config['hostname'], zm_config['monitor_number'], zm_config['record_duration'],
                                       zm_config.get('username'), zm_config.get('password'))
        elif destination == 'console':
            return ConsoleNotifier()
        else:
            raise KeyError(f'Unknown notification destination "{destination}"')

    def get_cool_down_interval(self):
        cool_down_interval = self.settings['cool_down_interval']
        return cool_down_interval

    def get_backend_url(self):
        return self.settings['backend_url']

    def get_backend_ws_url(self):
        return self.settings['backend_ws_url']

    def get_backend_api_key(self):
        return self.settings['backend_api_key']

    def get_show_images(self):
        return self.settings['show_images']

    def get_save_images(self):
        return self.settings['save_images']

    def get_output_folder(self):
        return self.settings['output_folder']

    def get_image_resize_width(self):
        return self.settings['image_resize_width']

    def get_last_person_detection_exclusion_threshold(self):
        return self.settings['last_person_detection_exclusion_threshold']

    def get_last_person_detection_expiration_seconds(self):
        return self.settings['last_person_detection_expiration_seconds']

    def is_verbose_mode(self):
        return self.settings['verbose']
