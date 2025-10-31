from typing import List

from models.detection_result import DetectionResult
from models.exclusion import Exclusion
from models.zone import Zone


class SourceDefinition:

    def __init__(self, id: str, name: str, type: str, url: str, enabled: bool, exclusions: List[Exclusion],
                 zones: List[Zone], confidence_threshold: float):
        self.id = id
        self.name = name
        self.type = type
        self.url = url
        self.enabled = enabled
        self.exclusions: List[Exclusion] = exclusions
        self.zones: List[Zone] = zones
        self.confidence_threshold: float = confidence_threshold

    @staticmethod
    def from_dict(data: dict) -> 'SourceDefinition':
        try:
            return SourceDefinition(
                data['id'],
                data['name'],
                data['type'],
                data['url'],
                data['enabled'],
                [Exclusion.from_dict(exclusion_data) for exclusion_data in data['exclusions']],
                [Zone.from_dict(zone_data) for zone_data in data['zones']] if 'zones' in data else [],
                data['confidence_threshold'],
            )
        except KeyError as e:
            print(f'KeyError when parsing SourceDefinition from data: {data}')
            print(f'Error details: {e}')
            raise e
        except Exception as e:
            print(f'Unknown error when parsing SourceDefinition from data: {data}')
            print(f'Error details: {e}')
            raise e

    def filter_detection_results_by_zone(self, detection_result: DetectionResult):
        """
        :return: Tuple (inside_zone_count, outside_zone_count) indicating the number of detections that were inside
        any of the zones configured for the specified source, and the number of detections that were not in any zone.
        If no zones are defined, then all detections will be considered to be inside a zone.
        """
        inside_zone_count = 0
        outside_zone_count = 0
        if len(self.zones) > 0:
            for person_detection in detection_result.person_detections:
                is_in_zone = False
                for zone in self.zones:
                    if zone.contains(person_detection):
                        is_in_zone = True
                        break
                if is_in_zone:
                    inside_zone_count += 1
                else:
                    outside_zone_count += 1
        else:
            inside_zone_count = len(detection_result.person_detections)
        return inside_zone_count, outside_zone_count
