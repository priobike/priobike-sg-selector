import {GeoJsonLayer} from '@deck.gl/layers';
import {TripsLayer} from '@deck.gl/geo-layers';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const routeId = new URLSearchParams(window.location.search).get('route_id');

class LSAsLayer extends GeoJsonLayer {
  constructor(props) {
    const config = {
      id: 'lsas',
      data: props.data,
      lineWidthMinPixels: 8,
      /* pickable: true, */
      lineCapRounded: true,
      /* autoHighlight: true, */
      highlightColor: [255, 255, 255, 255],
      getLineColor: [0, 255, 0],
      opacity: 1,
    };
    super({ ...config, ...props });
  }
}

class ProjectionConnectionLayer extends GeoJsonLayer {
  constructor(props) {
    const config = {
      id: 'projection-connections',
      data: props.data,
      lineWidthMinPixels: 2,
      lineCapRounded: true,
      getLineColor: [0, 0, 0],
      opacity: 1,
      getLineWidth: 0.2
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
class LSAsDirectionLayer extends TripsLayer {
  constructor(props) {
    const config = {
      id: 'trips-layer',
      data: `${domain}:${port}/demo/api/signalgroups/segments`,
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
  LSAsLayer,
  LSAsDirectionLayer,
  ProjectionConnectionLayer
}
