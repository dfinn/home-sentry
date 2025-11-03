You'll need to create the following configuration files and then specify the directory that contains them when you launch the home-sentry-watcher service:
* settings.json
* detector.json
* notifications.json
* sources.json

Please refer to the below sections for details on each config file.

# settings.json

Specifies general configuration settings for the behavior of the system.

| Setting | Description |
| ------- | ----------- |
| cool_down_interval | Duration in seconds after a detection occurs to wait before sending any additional notifications |
| show_images | If true, will show captured frames including detection results in a graphical window. Useful for troubleshooting. |
| save_images | If true, will save the most recent detection result from each source as a .jpg image in the specified output_folder. The filename will be <source_name>.jpg, so new detection images will overwrite any previous one for that source. |
| output_folder | Full path to directory to save the detection images if save_images is true. Will be created if not already present. |
| image_resize_width | Width, in pixels, to resize captured images to before running object detection.  Can improve performance if the RTSP stream is of a very high resolution since object detection will run faster on smaller images (possibly at the cost of detection accuracy if resized too small, however).  Resize height will be calculated automatically to preserve the aspect ratio of the source. |
| last_person_detection_exclusion_threshold | Threshold for the bounding box position to automatically exclude following a detection to prevent further detections at that spot for a period of time. See also last_person_detection_expiration_seconds below.
| last_person_detection_expiration_seconds | Duration in seconds after a detection occurs to automatically exclude that specific location from additional detections.  |
| verbose | If true, enable verbose log output |
| backend_url | URL at which the watcher component can reach the backend component |
| backend_ws_url | URL at which the watcher component can reach the backend websocket |
| backend_api_key | API key for watcher component's requests to the backend component.  Must match the API_KEY provided when launching the backend component.  To secure your server you should make up a long, randomized string to use (for example, a random UUID). |

Example file contents:

```
{  
  "cool_down_interval": 60,
  "show_images": false,
  "save_images": true,
  "output_folder":"/home/homesentry/detections",
  "image_resize_width": 640,
  "last_person_detection_exclusion_threshold": 0.05,
  "last_person_detection_expiration_seconds": 60,
  "verbose":false,
  "backend_url": "http://localhost:8080",
  "backend_ws_url": "ws://localhost:8080/events",
  "backend_api_key": "9ad32cc7-9a14-47ff-96c4-686881c1d809"
}
```


# detector.json

Configuration settings for object detection.

| Setting | Description |
| ------- | ----------- |
| name | Name of the detector to use. Only "pytorch" is supported at this time. |
| config.model | Name of the detector model to use, see the section below. |

Supported pytorch detection models:
| Name | Description |
| ---- | ----------- |
| frcnn-resnet | ResNet50 - accurate but slow |
| frcnn-mobilenet | MobileNet v3 - fast but not as accurate |
| retinanet | RetinaNet - balance between fast/accurate |

Example file contents:
```
{
    "name": "pytorch",
    "config":
    {
        "model": "frcnn-mobilenet"
    }
}
```


# notifications.json

Settings for how notifications are sent when a detection occurs.  Currently supports notifications to either Telegram, MQTT, or just logging to the console.

For information on setting up a Telegram bot and getting the token and chat ID, refer to https://core.telegram.org/bots/api

| Setting | Description |
| ------- | ----------- |
| destination | Must be "telegram", "mqtt", or "console" |
| telegram.token | Telegram token | 
| telegram.chat_id | Telegram chat ID |
| mqtt.hostname | Hostname of the MQTT server |
| mqtt.username | Username for MQTT authentication |
| mqtt.password | Password for MQTT authentication |

Example file contents for Telegram notifications:
```
{
    "destination": "telegram",
    "telegram":
    {
        "token": "xxxxx",
        "chat_id": 12345
    }    
}
```

Example file contents for mqtt notifications:
```
{
    "destination": "telegram",
    "mqtt":
    {
        "username": "user123",
        "password": pass123
    }    
}
```

Example file contents for console notifications:
```
{
    "destination": "console"
}
```


# sources.json

Specifies the list of RTSP sources that will be monitored.  The file consists of a JSON array containing one object for each camera source definition.  For more details about exclusions and zones, as well as the coordinate system, refer to [the terminology section](readme.MD#terminology). 

The following settings must be defined for each source:

| Setting | Description |
| ------- | ----------- |
| id | Unique ID for the source |
| name | Name/description of the source |
| type | Currently only "rtsp" is supported |
| url | The RTSP URL of the source |
| enabled | Whether monitoring of this source is enabled |
| confidence_threshold | Minimum confidence the detector must report for the detection to trigger a notification (example, 0.95 for 95% confidence) |
| exclusions | List of detection locations (ie, bounding boxes) to exclude from notifications. |
| zones | List of zones for this source. If none are defined, the entire image will be considered one zone. |


Exclusion properties:

| Name | Description |
| ------- | ----------- |
| name | Descriptive name of the exclusion (used for logging) |
| threshold | Exclusion will be matched if detection occurs within +/- this amount for either top-left or bottom-right points |
| top_left | Top left (x, y) point of the location to exclude |
| bottom_right | Bottom right (x, y) point of the location to exclude |

Zone properties:

| Name | Description |
| ---- | ----------- |
| id | Unique ID of the zone |
| name | Descriptive name of the zone |
| points | List of (x, y) points defining a polygon for the zone |

Example file contents:
```
[
    {
        "id": "porch",
        "name": "Front Porch",
        "type": "rtsp",
        "url": "rtsp://username:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1&unicast=true&proto=Onvif",
        "enabled": true,
        "confidence_threshold": 0.95,
        "exclusions": [],
        "zones": []
    },
    {
        "id": "driveway",
        "name": "Driveway Camera",
        "type": "rtsp",
        "url": "rtsp://username:password@192.168.1.101:554/cam/realmonitor?channel=1&subtype=1&unicast=true&proto=Onvif",
        "enabled": true,
        "confidence_threshold": 0.90,
        "exclusions":
        [
            {
                "name": "Tree",
                "threshold": 0.1,
                "top_left":
                {
                    "x": 0.673,
                    "y": 0.306
                },
                "bottom_right":
                {
                    "x": 0.733,
                    "y": 0.467
                }
            },
            {
                "name": "Chair",
                "threshold": 0.1,
                "top_left":
                {
                    "x": 0.561,
                    "y": 0.233
                },
                "bottom_right":
                {
                    "x": 0.672,
                    "y": 0.404
                }
            }
        ],
        "zones":
        [
            {
                "id": "zone1",
                "name": "Driveway and sidewalk",
                "points":
                [
                    {
                        "x": 0,
                        "y": 0.496
                    },
                    {
                        "x": 0.789,
                        "y": 0.296
                    },
                    {
                        "x": 1,
                        "y": 0.535
                    },
                    {
                        "x": 1,
                        "y": 1
                    },
                    {
                        "x": 0,
                        "y": 1
                    }
                ]
            }
        ]
    }
]
```

