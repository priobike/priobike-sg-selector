import {TileLayer} from '@deck.gl/geo-layers';
import {BitmapLayer} from '@deck.gl/layers';

export default class CyclOSMTileLayer extends TileLayer {
  constructor(props) {
    const config = {
      data: [
        'https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
        'https://b.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
        'https://c.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
      ],
      maxRequests: 20,

      pickable: false,
      highlightColor: [0, 0, 0, 0],
      minZoom: 0,
      maxZoom: 19,
      tileSize: 128,
      zoomOffset: devicePixelRatio === 1 ? -1 : 0,

      renderSubLayers: props => {
        const {
          bbox: {west, south, east, north}
        } = props.tile;

        return [
          new BitmapLayer(props, {
              data: null,
              image: props.data,
              bounds: [west, south, east, north],
          })
        ];
      }
    }

    super({ ...config, ...props });
  }
}
