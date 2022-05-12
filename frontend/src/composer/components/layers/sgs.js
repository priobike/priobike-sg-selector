import {GeoJsonLayer} from '@deck.gl/layers';
import {TripsLayer} from '@deck.gl/geo-layers';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const routeId = new URLSearchParams(window.location.search).get('route_id');

class SGsLayer extends GeoJsonLayer {
  constructor(props) {
    const config = {
      id: 'sgs',
      data: `${domain}:${port}/composer/api/route/${routeId}/connections`,
      lineWidthMinPixels: 8,
      pickable: true,
      lineCapRounded: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 255],
      opacity: 0.5,
    };
    super({ ...config, ...props });
  }
}

/**
 * Data format:
 * [
 *   {
 *     waypoints: [
 *      {coordinates: [lat, lon], timestamp: 0}
 *       ...,
 *      {coordinates: [lat, lon], timestamp: 1000}
 *     ]
 *   }
 * ]
 */
class SGsDirectionLayer extends TripsLayer {
  constructor(props) {
    const config = {
      id: 'trips-layer',
      data: `${domain}:${port}/composer/api/route/${routeId}/connections/segments`,
      getPath: d => d.waypoints.map(p => p.coordinates),
      getTimestamps: d => d.waypoints.map(p => p.progress),
      getColor: [255, 255, 255],
      opacity: 0.5,
      widthMinPixels: 5,
      jointRounded: true,
      capsRounded: true,
      fadeTrail: true,
      trailLength: 20,
      currentTime: 100,
      autoHighlight: true,
      highlightColor: [0, 0, 0, 255],
    };
    super({ ...config, ...props });
  }
}

export {
  SGsLayer,
  SGsDirectionLayer,
}
