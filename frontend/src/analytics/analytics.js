import React from 'react';
import ReactDOMServer from 'react-dom/server';

import DeckGL from '@deck.gl/react';
import { MapView } from '@deck.gl/core';
import {GeoJsonLayer} from '@deck.gl/layers';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';

import CyclOSMTileLayer from '../common/components/layers/cyclosm';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const algorithm = new URLSearchParams(window.location.search).get('algorithm_name');


const INITIAL_VIEW_STATE = {
  longitude: 9.993682,
  latitude: 53.551086,
  zoom: 12,
  pitch: 0,
  bearing: 0,
  width: window.innerWidth,
  height: window.innerHeight,
};

class Tooltip extends React.Component {
  render() {
    const header = (
      <Typography variant="h5" component="div">
        LSA {this.props.properties.pk}
      </Typography>
    );
    let confirmed;
    if (this.props.properties.tp_c > 0 || this.props.properties.fn_c > 0 || this.props.properties.fp_c > 0) {
      confirmed = (
        <Typography sx={{ fontSize: 14 }} color="text.secondary">
          {this.props.properties.f1_c} F1 (Confirmed) <br />
          {this.props.properties.tp_c} True Positives (Confirmed) <br />
          {this.props.properties.fp_c} False Positives (Confirmed) <br />
          {this.props.properties.fn_c} False Negatives (Confirmed)
        </Typography>
      );
    } else {
      confirmed = (
        <Typography sx={{ fontSize: 14 }} color="text.secondary">
          No Confirmed Results
        </Typography>
      );
    }

    let unconfirmed;
    if (this.props.properties.tp > 0 || this.props.properties.fn > 0 || this.props.properties.fp > 0) {
      unconfirmed = (
        <Typography sx={{ fontSize: 14 }} color="text.secondary">
          {this.props.properties.f1} F1 <br />
          {this.props.properties.tp} True Positives <br />
          {this.props.properties.fp} False Positives <br />
          {this.props.properties.fn} False Negatives
        </Typography>
      );
    } else {
      unconfirmed = (
        <Typography sx={{ fontSize: 14 }} color="text.secondary">
          No Unconfirmed Results
        </Typography>
      );
    }

    return (
      <Card>
        <CardContent>
          {header}
          <Divider />
          {confirmed}
          <Divider />
          {unconfirmed}
        </CardContent>
      </Card>
    );
  }
}

class AnalyticsTooltipSource {
  render({object}) {
    if (!object) return object && {};
    console.log(object.properties);

    const element = <Tooltip properties={object.properties} />;
    return object && {
      html: ReactDOMServer.renderToString(element),
      style: { background: 'transparent' }
    };
  }
}

const tooltipSource = new AnalyticsTooltipSource();

class LSAAnalyticsLayer extends GeoJsonLayer {
  static interpolateColor(properties) {
    if (properties.tp > 0 || properties.fn > 0 || properties.fp > 0) {
      return [
        Math.round(255 * (1 - properties.f1)),
        Math.round(255 * properties.f1),
        0,
      ];
    }
    return [0, 0, 0];
  }

  constructor(props) {
    const config = {
      id: 'lsas',
      data: `${domain}:${port}/analytics/api/statistics?algorithm_name=${algorithm}`,
      pickable: true,
      lineCapRounded: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 255],
      getLineColor: d => LSAAnalyticsLayer.interpolateColor(d.properties),
      lineWidthMinPixels: 8,
      opacity: 0.5,
    };
    super({ ...config, ...props });
  }
}

class AnalyticsLSAMap extends React.Component {
  render() {
    const layers = [
      new CyclOSMTileLayer(),
      new LSAAnalyticsLayer(),
    ];

    return (
      <section className="deck-gl">
        <DeckGL
          initialViewState={INITIAL_VIEW_STATE}
          controller={true}
          views={[ new MapView({ repeat: true }) ]}
          layers={layers}
          getTooltip={tooltipSource.render}
          />
      </section>
    );
  }
}


export default class Analytics extends React.Component {
  render() {
    return (
      <main>
        <AnalyticsLSAMap />
      </main>
    );
  }
}
