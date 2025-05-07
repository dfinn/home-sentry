# Home Sentry

Monitors RTSP video streams from your cameras and notifies you when people are detected.

### Features:
- Supports any number of RTSP camera feeds (within available memory)
- Configurable notification targets: Telegram or MQTT
- Configurable cool-down period to avoid repeat notifications
- Configuirable confidence threshold for notification to occur  
- Supports custom "zones" for each camera source, so you can include only specified region(s) for detection
- Supports user-defined "exclusions" for each camera source, so you can exclude a specific fixed location causing repeat false detections
- Automatic temporary exclusion of previous detected location, to help reduce false detections from fixed objects

### Overview:
Home Sentry consists of two components, the watcher (home-sentry-watcher) and the backend (home-sentry-be).  

At startup, the watcher component queries the backend for the list of defined camera sources and opens a video stream from each one.  It then cycles round-robin through each feed, pulling the latest frame and using PyTorch object detection to check if any people are detected.  

When a detection occurs, the following checks occur to see if a notification will be sent:
- The detection confidence must be greater than the configured confidence threshold
- The detection must occur within a defined zone.  If no zones are defined for a video source, then the entire image is considered to be a valid zone. 
- The detection must not match any of the exclusions defined for that video source. 
- The detection must not match the automatically-defined "last person" detection within the configured lifespan for that value (see last_person_detection_expiration_seconds)

### Terminology

**Point**: An location specified by its relative X, Y coordinate. All user-configured coordinates, such as the top-left and bottom-right values mentioned below, are relative values between 0.0 and 1.0 so that the exact camera resolutions do not need to be considered.  For example, an X coordinate of 0.0 indiates the left edge of the image, 1.0 indicates the right edge, and 0.5 indicates the middle.  

**Person detection**: The location where a person was detected, specified by a bounding box defined by a top-left and bottom-right point.  It also includes the confidence value (between 0.0 - 1.0) that the object detector reported.

**Zone**: Defined by a list of points that defines a polygon.  The polygon does not need to be closed.  For a person detection to be considered inside the zone, it can be either fully contained or just partially overlap.  Each video source has its own list of zones.  If none are defined, the entire image is considered one zone.

**Exclusion**: Defined as a bounding box (top-left and bottom-right) location for which to ignore detections. Useful for fixed objects, like a shadow or chair that keeps triggering false detections.  It also includes a "threshold" value, that specifies the detection can occurs within plus or minus that extra amount from the excluded location and still match.  Example: a detection occurs at (0.455, 0.083), and you have an exclusion defined for (0.4, 0.1) with a threshold of 0.1   The detection would match the exclusion because both the X and Y values of the exclusion point are within 0.1 of the detected location.


### Setup

1) You'll need to create a directory containing a few required configuration files. When you launch home-sentry-watcher, you'll provide this directory path on the command line. Please refer to [config-files.MD](config-files.MD)

2) Configure and run the backend component:
[home-sentry-be setup instructions](home-sentry-be/readme.MD)

3) Configure and run the watcher component:
[home-sentry-watcher setup instructions](home-sentry-watcher/readme.MD)
