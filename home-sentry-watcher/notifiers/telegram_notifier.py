import cv2
import requests

from models.detection_result import DetectionResult
from notifiers.notifier import Notifier
from timer import Timer


class TelegramNotifier(Notifier):

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def get_updates(self):
        print('Getting updates')
        response = requests.get(self.url_for('getUpdates'))
        print(f'Response status: {response.status_code}')
        print(response.json())

    def send_text(self, text, log):
        log.info(f'Sending text: {text}')
        response = requests.post(self.url_for('sendMessage'), json={
            "chat_id": self.chat_id,
            "text": text
        })
        log.info(f'sendMessage: {response.status_code}')

    def send_photo(self, image, caption):
        files = {'photo': image}
        response = requests.post(self.url_for('sendPhoto'), {'chat_id': self.chat_id, 'caption': caption}, files=files)

    def send_video(self, video_bytes, caption, log):
        log.info(f'Sending video: {caption}')
        files = {'video': video_bytes}
        response = requests.post(self.url_for('sendVideo'), {'chat_id': self.chat_id, 'caption': caption}, files=files)
        log.info(f'sendVideo: {response.status_code}')

    def url_for(self, method_name):
        return f'https://api.telegram.org/bot{self.token}/{method_name}'

    def notify_detections(self, detection_result: DetectionResult, source_definition, log):
        source_name = source_definition.name
        success, np_array = cv2.imencode('.jpg', detection_result.image)
        if success:
            self.send_photo(np_array.tobytes(), f'{source_name} - {detection_result}')
        else:
            self.send_text(f'{source_name} - {detection_result} *** error converting image ***', log)
