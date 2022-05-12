import {GeoJsonLayer} from '@deck.gl/layers';
import {TripsLayer} from '@deck.gl/geo-layers';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const routeId = new URLSearchParams(window.location.search).get('route_id');

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
class RouteDirectionLayer extends TripsLayer {
  constructor(props) {
    const config = {
      id: 'route-layer',
      data: `${domain}:${port}/composer/api/route/${routeId}/segments`,
      getPath: d => d.waypoints.map(p => p.coordinates),
      getTimestamps: d => d.waypoints.map(p => p.progress),
      getColor: [255, 255, 255],
      opacity: 0.25,
      widthMinPixels: 8,
      jointRounded: true,
      capsRounded: true,
      fadeTrail: true,
      trailLength: 20,
      currentTime: 100,
    };
    super({ ...config, ...props });
  }
}

class RouteLayer extends GeoJsonLayer {
  constructor(props) {
    const config = {
      id: 'route',
      data: `${domain}:${port}/composer/api/route/${routeId}`,

      lineWidthMinPixels: 8,
      pickable: false,
      color: [0, 0, 0, 255],
      opacity: 1,
    };
    super({ ...config, ...props });
  }
}

export {
  RouteDirectionLayer,
  RouteLayer,
};
