import json
from time import sleep

import paho.mqtt.client as mqtt

from models.detection_result import DetectionResult
from notifiers.notifier import Notifier

TOPIC = 'home_sentry/detections'


class MqttNotifier(Notifier):

    def __init__(self, broker_host, username, password):
        print(f'Connecting to MQTT broker at {broker_host}')
        self.is_connected = False
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(username, password)
        self.client.connect(broker_host, 1883, 60)
        self.client.loop_start()
        while not self.is_connected:
            sleep(1)

    def shutdown(self):
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f'Successfully connected to MQTT broker with result code {rc}')
            self.is_connected = True
        else:
            print(f'Error connecting to MQTT broker, result code {rc}')
            exit(1)

    def notify_detections(self, detection_result: DetectionResult, source_definition, log):
        payload = json.dumps({'num_detections': detection_result.count()})
        log.info(f'Publishing MQTT notification payload: {payload}')
        self.client.publish(TOPIC, payload=payload, qos=0, retain=False)
