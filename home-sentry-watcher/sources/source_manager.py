import copy
import json
import threading
import traceback
from typing import Optional, Dict

import requests
import websocket
from requests.exceptions import HTTPError
from websocket import WebSocketApp

from config_helper import ConfigHelper
from models.source_definition import SourceDefinition
from sources.fake_source import FakeSource
from sources.file_source import FileSource
from sources.opencv_rtsp_source import OpenCvRtspSource
from sources.videosource import VideoSource


class SourceManager:

    def __init__(self, config_helper: ConfigHelper, backend_url: str, backend_ws_url: str, backend_api_key: str):
        self.config_helper: ConfigHelper = config_helper
        self.backend_url: str = backend_url
        self.session = requests.Session()
        self.session.headers.update({'X-Api-Key': backend_api_key})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.source_definitions: Dict[str, SourceDefinition] = self.fetch_source_definitions()
        self.show_source_definitions()
        self.websocket_thread: Optional[threading.Thread] = None
        self.wsapp: Optional[WebSocketApp] = None
        self.connect_websocket(backend_ws_url, backend_api_key)

    def connect_websocket(self, backend_ws_url, backend_api_key):
        print(f'Connecting to websocket url {backend_ws_url}')
        websocket.enableTrace(True)
        self.wsapp = websocket.WebSocketApp(backend_ws_url,
                                            header={'X-Api-Key': backend_api_key},
                                            on_open=self.on_ws_open,
                                            on_message=self.on_ws_message,
                                            on_error=self.on_ws_error,
                                            on_close=self.on_ws_close)
        self.websocket_thread = threading.Thread(target=self.run_websocket)
        self.websocket_thread.start()

    def run_websocket(self):
        print('Starting websocket thread loop')
        self.wsapp.run_forever()
        print('Websocket thread loop had exited')

    def shutdown(self):
        print('Closing websocket')
        self.wsapp.close()
        print('Waiting for websocket thread exit')
        self.websocket_thread.join()
        print('SourceManager shutdown completed')

    def on_ws_open(self, ws):
        print('Websocket opened')

    def on_ws_message(self, ws, payloadstr):
        print(f'Got ws message: {payloadstr}')
        try:
            payload = json.loads(payloadstr)
            print('Parsed message:', payload)
            event_name = payload['event']
            if event_name == 'sources_updated':
                print('Received sources_updated event, fetching updated sources list')
                self.source_definitions = self.fetch_source_definitions()
                self.show_source_definitions()
        except:
            print('Error parsing websocket payload')
            print(traceback.format_exc())

    def on_ws_error(self, ws, error):
        print('Websocket error', error)

    def on_ws_close(self, ws, close_status_code, close_msg):
        print('Websocket closed')

    def fetch_source_definitions(self) -> Dict[str, SourceDefinition]:
        """
        Fetches the list of source definitions from the backend service, and then returns it as a dictionary
        indexed by source id.
        """
        sources_url = self.backend_url + '/sources'
        print(f'Fetching sources from {sources_url}')
        try:
            response = self.session.get(sources_url)
        except requests.exceptions.RequestException as e:
            raise HTTPError(f'Error getting sources list: {e}')
        print(f'Got response code: {response.status_code}')
        self.check_http_response(response, 200, 'Error getting sources list')
        sources_json = response.json()
        sources_list = [SourceDefinition.from_dict(source_data) for source_data in sources_json]
        sources_dict = {}
        for source in sources_list:
            sources_dict[source.id] = source
        print('Got sources:')
        print(sources_dict)
        return sources_dict

    def show_source_definitions(self):
        print(f'{len(self.source_definitions)} sources defined:')
        for key in self.source_definitions.keys():
            s = self.source_definitions[key]
            print(f'   {s.id} ({s.name}): type={s.type}, enabled={s.enabled}, confidence_threshold={s.confidence_threshold}')

    @staticmethod
    def check_http_response(response, expected_status_code, error_message):
        if response.status_code != expected_status_code:
            print(f'HTTP status code {response.status_code} does not match expected value {expected_status_code}')
            if response.headers.get('Content-Type').startswith('application/json'):
                try:
                    data = response.json()
                except Exception as e:
                    print(f'Error parsing json payload from HTTP response: {e}')
                    raise HTTPError(error_message)
            else:
                data = None
            if data is not None and 'error' in data and 'message' in data['error']:
                error_detail = data['error']['message']
                raise HTTPError(f'{error_message} ({error_detail})')
            else:
                raise HTTPError(error_message)

    def get_source_definition(self, id: str) -> SourceDefinition:
        if id in self.source_definitions:
            s = self.source_definitions[id]
            return copy.deepcopy(s)
        else:
            raise KeyError(f'Unable to find source with id "{id}"')

    def build_video_sources(self):
        video_sources = []
        print('Building list of video sources')
        for source_definition in self.source_definitions.values():
            if not source_definition.enabled:
                continue
            video_source = self.build_video_source(source_definition)
            video_sources.append(video_source)
        print(f'Returning list of {len(video_sources)} video sources')
        return video_sources

    def build_video_source(self, source_definition: SourceDefinition) -> VideoSource:
        log_verbose = self.config_helper.is_verbose_mode()
        source_type = source_definition.type
        if source_type == 'rtsp' or source_type == 'opencv_rtsp':
            return OpenCvRtspSource(source_definition, source_definition.url, log_verbose)
        elif source_type == 'file':
            return FileSource(source_definition.id, source_definition.url, log_verbose)
        elif source_type == 'fake':
            return FakeSource(source_definition.id, log_verbose)
        else:
            raise ValueError(f'Unsupported source type {source_type}')
