import { randomUUID } from 'crypto';
import express, { Response } from 'express';
import { readFile, writeFile } from 'fs/promises';
import * as http from 'http';
import { WebSocket, WebSocketServer } from 'ws';
import SourceDefinition from './source_definition';

var API_KEY = process.env.API_KEY;
var port = 8080;

const version = readFile("version.txt", "utf8");
console.log(`home-sentry-be version ${version} starting up`);


var SOURCES_PATH = process.env.SOURCES_PATH as string;

class SourceManager {
  constructor(private onSourcesUpdated: () => void) {
  }

  /**
   * Get all defined sources.
   * @returns Array of SourceDefinition objects, or null if an error occurs.
   */
  async getSources(): Promise<Array<SourceDefinition>> {
    try {
      console.log(`Loading sources from ${SOURCES_PATH}`);
      return JSON.parse(await readFile(SOURCES_PATH, "utf8"));
    } catch (e) {
      console.log(`Error loading sources: ${e}`);
      throw e;
    }
  }

  async getSourceById(sourceId: string): Promise<SourceDefinition | undefined> {
    const sources = await this.getSources();
    const source = sources.find(source => source.id == sourceId);
    if (source == undefined) {
      console.warn(`No source found with id '${sourceId}'`);
    }
    return source;
  }

  // Update the source specified and save. Return true if successful, false if a source with matching ID is not found.
  async updateSource(sourceToUpdate: SourceDefinition) {
    const id = sourceToUpdate.id;
    const sources = await this.getSources();
    const index = sources.findIndex(source => source.id == id);
    if (index == -1) {
      console.warn(`updateSource: No source found with id '${id}'`);
      return false;
    } else {
      console.log(`Updating source '${id}'`);
      sources[index] = sourceToUpdate;
      await this.saveSources(sources);
      return true;
    }
  }

  async saveSources(sources: Array<SourceDefinition>) {
    console.log(`Saving ${SOURCES_PATH}`);
    await writeFile(SOURCES_PATH, JSON.stringify(sources));
    this.onSourcesUpdated();
  }
}

// Create Express http server
var app = express();
const server = http.createServer(app);

// Create WebSocket /events endpoint
const wss = new WebSocketServer({ path: '/events', noServer: true });

// Create SourceManager
const sourceManager = new SourceManager(() => {
  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      console.log('Sending sources_updated event');
      client.send(JSON.stringify({ 'event': 'sources_updated' }));
    }
  });
});

// Middleware to parse request body.
app.use(express.json());

// Validate that correct API key is provided in each request.
app.use(function (request, response, next) {
  let request_api_key = request.header("x-api-key");
  if (request_api_key == API_KEY) {
    console.log('API key accepted');
    next()
  } else {
    console.log('API key rejected');
    response.status(401).send({ error: { message: "Invalid API key" } });
  }
});

// Helper function to get sources and invoke the callback with the result.  If an error occurs, send a 500 response.
async function withSources(response: Response, callback: (sources: Array<SourceDefinition>) => void) {
  try {
    const sources = await sourceManager.getSources();
    callback(sources);
  } catch (e) {
    console.log(`Error loading sources: ${e}`);
    response.sendStatus(500);
  }
}


server.listen(port, function () {
  console.log(`Home Sentry backend listening on port ${port}`);
})

server.on('upgrade', function upgrade(request, socket, head) {
  console.log('WebSocket upgrade requested');
  if (request.headers['x-api-key'] === API_KEY) {
    console.log('API key valid, WebSocket upgrade accepted');
    wss.handleUpgrade(request, socket, head, function (ws) {
      wss.emit('connection', ws, request);
    });
  }
  else {
    console.log('Invalid API key, WebSocket upgrade denied');
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
  }
});

wss.on('connection', (ws: WebSocket, connection: http.IncomingMessage) => {
  const ip = connection.socket.remoteAddress;

  console.log(`WebSocket connection established from ${ip}`);

  ws.on('message', (message: string) => {
    console.log('Received WebSocket message: %s', message);
  });

  ws.on('close', function close() {
    console.log(`Client ${ip} WebSocket disconnected`);
  });
});


////////////////////////////////////  API Endpoints for sources  ////////////////////////////////////

// Get all sources
app.get('/sources', async function (req, res) {
  withSources(res, (sources) => {
    res.json(sources);
  });
})

// Get source by ID
app.get('/sources/:source_id', async function (req, res) {
  withSources(res, (sources) => {
    const source_id = req.params.source_id;
    const source = sources.find(source => source.id == source_id);
    res.json(source);
  });
})

// Update source
app.put('/sources/:source_id', async function (req, res) {
  console.log('Updating source:', req.body);
  try {
    const updateResult = await sourceManager.updateSource(req.body);
    res.sendStatus(updateResult ? 204 : 404);
  } catch (e) {
    console.log(`Error updating source: ${e}`);
    res.sendStatus(500);
  }
})


////////////////////////////////////  API Endpoints for exclusions  ////////////////////////////////////

// Add exclusion
app.post('/sources/:source_id/exclusions', async (req, res) => {
  const source_id = req.params.source_id;
  console.log(`Adding exclusion for source ${source_id}`);

  withSources(res, async (sources) => {
    const source_to_update = sources.find(source => source.id == source_id);
    if (source_to_update != null) {
      const exclusion = {
        "id": randomUUID(),
        "name": req.body.name,
        "top_left": req.body.top_left,
        "bottom_right": req.body.bottom_right,
        "threshold": req.body.threshold
      };
      console.log('Adding exclusion:', exclusion)
      source_to_update.exclusions.push(exclusion);
      sourceManager.saveSources(sources);
      res.sendStatus(201);
    } else {
      res.sendStatus(404);
    }
  });
});

// Delete exclusion
app.delete('/sources/:source_id/exclusions/:exclusion_id', async (req, res) => {
  const source_id = req.params.source_id;
  const exclusion_to_delete = req.params.exclusion_id;
  console.log(`Deleting exclusion ${exclusion_to_delete} from source ${source_id}`);

  withSources(res, async (sources) => {
    const source_to_update = sources.find(source => source.id == source_id);
    if (source_to_update != null) {
      if (source_to_update.exclusions.some(exclusions => exclusions.id === exclusion_to_delete)) {
        source_to_update.exclusions = source_to_update.exclusions.filter(exclusions => exclusions.id != exclusion_to_delete);
        sourceManager.saveSources(sources);
        res.sendStatus(204);
      } else {
        console.log(`Exclusion ${exclusion_to_delete} not found in source ${source_id}`);
        res.sendStatus(404);
      }
    } else {
      res.sendStatus(404);
    }
  });
});


////////////////////////////////////  API Endpoints for zones  ////////////////////////////////////

// Add Zone
app.post('/sources/:source_id/zones', async (req, res) => {
  const source_id = req.params.source_id;
  console.log(`Adding zone for source ${source_id}`);

  withSources(res, async (sources) => {
    const source_to_update = sources.find(source => source.id == source_id);
    if (source_to_update != null) {
      const zone = {
        "id": randomUUID(),
        "name": req.body.name,
        "points": req.body.points
      };
      console.log('Adding zone:', zone)
      if (!source_to_update.zones) source_to_update.zones = []
      source_to_update.zones.push(zone);
      sourceManager.saveSources(sources);
      res.sendStatus(201);
    } else {
      res.sendStatus(404);
    }
  });
});

// Delete zone
app.delete('/sources/:source_id/zones/:zone_id', async (req, res) => {
  const source_id = req.params.source_id;
  const zone_to_delete = req.params.zone_id;
  console.log(`Deleting zone ${zone_to_delete} from source ${source_id}`);

  withSources(res, async (sources) => {
    const source_to_update = sources.find(source => source.id == source_id);
    if (source_to_update == null) {
      console.log(`Source ${source_id} not found`)
      res.sendStatus(404);
      return;
    }
    if (source_to_update.zones.some(zone => zone.id === zone_to_delete)) {
      source_to_update.zones = source_to_update.zones.filter(zone => zone.id != zone_to_delete);
      sourceManager.saveSources(sources);
      res.sendStatus(204);
    } else {
      console.log(`Zone ${zone_to_delete} not found in source ${source_id}`);
      res.sendStatus(404);
    }
  });
});

