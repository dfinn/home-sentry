import http.cookiejar
import json
import os
import socket
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from models.detection_result import DetectionResult
from notifiers.notifier import Notifier

ZM_TRIGGER_PORT = 6802


class ZoneMinderNotifier(Notifier):

    def __init__(self, hostname, record_duration, username=None, password=None):
        self.hostname = hostname
        self.record_duration = record_duration
        self.username = username
        self.password = password
        self.telegram_notifier = None

    def notify_detections(self, detection_result: DetectionResult, source_definition, log):
        monitor_id = source_definition.zoneminder_monitor_id
        if monitor_id is None:
            log.info(f'ZoneMinder: skipping trigger — zoneminder_monitor_id not set')
            return
        message = f"{monitor_id}|on+{self.record_duration}|1|person_detected|Person Detected\n"
        try:
            with socket.create_connection((self.hostname, ZM_TRIGGER_PORT), timeout=5) as sock:
                sock.sendall(message.encode())
            thread = threading.Thread(target=self._fetch_event_url, args=(monitor_id, source_definition.name, log), daemon=True)
            thread.start()
        except OSError as e:
            log.info(f'ZoneMinder trigger failed ({self.hostname}:{ZM_TRIGGER_PORT}): {e}')

    def _fetch_event_url(self, monitor_id, source_name, log):
        time.sleep(self.record_duration + 2)
        try:
            token = self._get_auth_token(log)
            api_url = f"http://{self.hostname}/zm/api/events/index/MonitorId:{monitor_id}.json?sort=StartTime&direction=desc&page=1&limit=1"
            if token:
                api_url += f"&token={token}"
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read())
            events = data.get('events', [])
            if events:
                event = events[0]['Event']
                event_id = event['Id']
                log.info(f'ZoneMinder event {event_id} recorded')
                if self.telegram_notifier:
                    if event.get('DefaultVideo'):
                        self._download_and_send_video(event_id, source_name, log)
                    else:
                        event_url = f'http://{self.hostname}/zm/index.php?view=event&eid={event_id}'
                        self.telegram_notifier.send_text(f'{source_name}: {event_url}', log)
            else:
                log.info(f'ZoneMinder: no event found for monitor {monitor_id}')
        except Exception as e:
            log.info(f'ZoneMinder event lookup failed: {e}')

    def _download_and_send_video(self, event_id, source_name, log):
        try:
            cookie_jar = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
            login_data = urllib.parse.urlencode({
                'action': 'login',
                'username': self.username,
                'password': self.password,
            }).encode()
            opener.open(f"http://{self.hostname}/zm/index.php", login_data, timeout=10)
            download_url = f"http://{self.hostname}/zm/index.php?view=view_video&mode=mp4&eid={event_id}"
            log.info(f'Downloading ZoneMinder event {event_id} video')
            with opener.open(download_url, timeout=60) as response:
                content_type = response.headers.get('Content-Type', 'unknown')
                video_bytes = response.read()
            log.info(f'Downloaded {len(video_bytes)} bytes, Content-Type: {content_type}')
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(video_bytes)
            log.info(f'Saved to {tmp_path}')
            try:
                self.telegram_notifier.send_video(video_bytes, source_name, log)
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            log.info(f'ZoneMinder video download failed: {e}')

    def _get_auth_token(self, log):
        if not self.username or not self.password:
            return None
        try:
            login_url = f"http://{self.hostname}/zm/api/host/login.json"
            data = urllib.parse.urlencode({'user': self.username, 'pass': self.password}).encode()
            with urllib.request.urlopen(login_url, data=data, timeout=10) as response:
                result = json.loads(response.read())
            return result.get('access_token')
        except Exception as e:
            log.info(f'ZoneMinder authentication failed: {e}')
            return None
