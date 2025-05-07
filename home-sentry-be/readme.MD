# home-sentry-be

### Background
Backend component for Home Sentry, which provides data (eg, the sources list) via a REST API . See the [main readme file](../readme.MD) for more info.

### Setup
1) Install [node.js](https://nodejs.org/en). Tested with node.js versions 16.x and 18.x.

2) Install required dependencies:
```
npm install
```

3) Build
```
npm run build
```

### Launching


Must provide the following environment variables:

**SOURCES_PATH**: full path and filename of the sources JSON file (see [sources.json](../config-files.MD#sourcesjson))

**API_KEY**: must match the value provided for backend_api_key in the [settings.json](../config-files.MD#settingsjson) file

Example:
```
SOURCES_PATH=/homesentry/sources.json API_KEY=9ad32cc7-9a14-47ff-96c4-686881c1d809 npm start
```

