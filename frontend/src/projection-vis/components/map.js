import React from "react";
import DeckGL from '@deck.gl/react';
import { MapView, WebMercatorViewport } from '@deck.gl/core';
import { StaticMap as Map } from 'react-map-gl';
import { BASEMAP } from '@deck.gl/carto';
import { RouteLayer } from './layers/route';
import { LSAsLayer, ProjectionConnectionLayer } from './layers/lsas';
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
      /* selectedLSAs: props.selectedLSAs,
      confirmedLSAs: props.confirmedLSAs */
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
    fetch(`${domain}:${port}/projection_vis/api/route/${routeId}/region`)
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
      /* new RouteDirectionLayer({ currentTime: this.state.animationProgress }), */
      new LSAsLayer({
        data: this.props.LSAs,
        getLineColor: d => {
          if (d.properties.pk.includes("-")) {
            return [252, 136, 3];
          }
          return [0, 195, 255];
        }
      }),
      new ProjectionConnectionLayer({
        data: this.props.projectionConnections,
        getLineColor: d => {
          let duplicateCount = 0;
          for (const lsa of this.props.projectionConnections["features"]){
            if (lsa["geometry"]["coordinates"][1][0] == d["geometry"]["coordinates"][1][0] && lsa["geometry"]["coordinates"][1][1] == d["geometry"]["coordinates"][1][1]){
              duplicateCount += 1;
            }
          }
          if (duplicateCount > 1){
            return [255, 0 , 0];
          }
          return [0, 0, 0];
        }
      }),
      /* new LSAsDirectionLayer({ currentTime: this.state.animationProgress }), */
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
