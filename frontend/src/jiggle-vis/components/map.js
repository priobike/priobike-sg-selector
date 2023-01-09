import React from "react";
import DeckGL from '@deck.gl/react';
import { MapView, WebMercatorViewport } from '@deck.gl/core';
import { StaticMap as Map } from 'react-map-gl';
import { BASEMAP } from '@deck.gl/carto';
import { RouteLayer, RouteDirectionLayer } from './layers/route';
import { LSAsLayer, LSAsDirectionLayer } from './layers/lsas';
import LSATooltipSource from './tooltip';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const routeId = new URLSearchParams(window.location.search).get('route_id');

const tooltipSource = new LSATooltipSource();

export default class LSAMap extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      animationProgress: 0,
      viewport: new WebMercatorViewport({
        longitude: 9.993682,
        latitude: 53.551086,
        zoom: 12,
        pitch: 0,
        bearing: 0,
        width: window.innerWidth,
        height: window.innerHeight,
      }),
    };

    // Create a deck gl ref and bind the onClick listener
    this.deckRef = React.createRef();

    this.animationID = null;
  }

  updateViewport = (region) => {
    this.setState((prevState) => {
      const viewport = new WebMercatorViewport(prevState.viewport);
      const { longitude, latitude, zoom } = viewport.fitBounds(
        [[region.minX, region.minY], [region.maxX, region.maxY]],
        { padding: 100 }
      );
      const clampedZoom = Math.min(zoom, 18);
      return {
        viewport: {
          ...prevState.viewport,
          longitude,
          latitude,
          zoom: clampedZoom,
        }
      };
    });
  };

  /* componentDidUpdate(prevProps) {
    if (prevProps.selectedLSAs !== this.props.selectedLSAs) {
      this.setState({
        selectedLSAs: this.props.selectedLSAs
      });
    }
    if (prevProps.confirmedLSAs !== this.props.confirmedLSAs) {
      this.setState({
        confirmedLSAs: this.props.confirmedLSAs
      });
    }
  } */

  animate = () => {
    const step = 0.5;
    const maxProgress = 120;
    this.setState((oldState) => ({
      animationProgress: (oldState.animationProgress + step) % maxProgress,
    }));
    this.animationID = window.requestAnimationFrame(this.animate);
  };

  componentDidMount() {
    window.requestAnimationFrame(this.animate);

    // Fetch the route region from the server
    fetch(`${domain}:${port}/jiggle_vis/api/route/${routeId}/region`)
      .then(res => res.json())
      .then(res => {
        const region = {
          minX: res.min_x,
          minY: res.min_y,
          maxX: res.max_x,
          maxY: res.max_y,
        };
        this.updateViewport(region);
      });
  }

  componentWillUnmount() {
    window.cancelAnimationFrame(this.state.animationID);
  }

  render() {
    const layers = [
      new RouteLayer(),
      new RouteDirectionLayer({ currentTime: this.state.animationProgress }),
      new LSAsLayer({
        data: this.props.LSAs,
        getLineColor: d => {
          if (d.properties.pk.includes("-")) {
            return [99, 60, 2];
          }
          return [0, 255, 0];
        }
      }),
      new LSAsDirectionLayer({ currentTime: this.state.animationProgress }),
    ];

    return (
      <section className="deck-gl">
        <DeckGL
          ref={this.deckRef}
          initialViewState={this.state.viewport}
          controller={true}
          views={[ new MapView({ repeat: true }) ]}
          layers={layers}
          getTooltip={tooltipSource.render}>
          <Map mapStyle={BASEMAP.VOYAGER} />
        </DeckGL>
      </section>
    );
  }
}
