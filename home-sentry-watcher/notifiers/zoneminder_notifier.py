import json
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from models.detection_result import DetectionResult
from notifiers.notifier import Notifier

ZM_TRIGGER_PORT = 6802


class ZoneMinderNotifier(Notifier):

    def __init__(self, hostname, monitor_number, record_duration, username=None, password=None):
        self.hostname = hostname
        self.monitor_number = monitor_number
        self.record_duration = record_duration
        self.username = username
        self.password = password

    def notify_detections(self, detection_result: DetectionResult, source_name: str):
        message = f"{self.monitor_number}|on+{self.record_duration}|1|person_detected|Person Detected\n"
        try:
            with socket.create_connection((self.hostname, ZM_TRIGGER_PORT), timeout=5) as sock:
                sock.sendall(message.encode())
            thread = threading.Thread(target=self._fetch_event_url, daemon=True)
            thread.start()
        except OSError as e:
            print(f'ZoneMinder trigger failed ({self.hostname}:{ZM_TRIGGER_PORT}): {e}')

    def _fetch_event_url(self):
        time.sleep(self.record_duration + 2)
        try:
            token = self._get_auth_token()
            api_url = f"http://{self.hostname}/zm/api/events/index/MonitorId:{self.monitor_number}.json?sort=StartTime&direction=desc&page=1&limit=1"
            if token:
                api_url += f"&token={token}"
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read())
            events = data.get('events', [])
            if events:
                event_id = events[0]['Event']['Id']
                print(f'ZoneMinder event URL: http://{self.hostname}/zm/index.php?view=event&eid={event_id}')
            else:
                print(f'ZoneMinder: no event found for monitor {self.monitor_number}')
        except Exception as e:
            print(f'ZoneMinder event URL lookup failed: {e}')

    def _get_auth_token(self):
        if not self.username or not self.password:
            return None
        try:
            login_url = f"http://{self.hostname}/zm/api/host/login.json"
            data = urllib.parse.urlencode({'user': self.username, 'pass': self.password}).encode()
            with urllib.request.urlopen(login_url, data=data, timeout=10) as response:
                result = json.loads(response.read())
            return result.get('access_token')
        except Exception as e:
            print(f'ZoneMinder authentication failed: {e}')
            return None
