# Changelog

All notable changes to home-sentry-watcher are documented in this file.

## [Unreleased] - 1.2.0

- Added `ZoneMinderNotifier` to trigger ZoneMinder recording on detections, and support for configuring multiple simultaneous notification destinations.
- `zoneminder_monitor_id` is now configured per-source instead of globally.
- When a ZoneMinder event is recorded, its video is downloaded and uploaded to Telegram (if a Telegram destination is configured), falling back to sending the event URL if no video is available.
- Fixed verbose log messages.

## [1.1]

- `confidence_threshold` is now defined per-source instead of globally.
- Moved `confidence_threshold` filtering from `PyTorchDetector` to `DetectionManager`.
- Removed label text and duplicate box drawing from `PyTorchDetector`.
- Added new unit tests.

## [1.0]

- Initial release.
