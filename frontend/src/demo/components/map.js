import React from "react";
import DeckGL from '@deck.gl/react';
import { MapView, WebMercatorViewport } from '@deck.gl/core';
import { StaticMap as Map } from 'react-map-gl';
import { BASEMAP } from '@deck.gl/carto';
import { RouteLayer, RouteDirectionLayer } from './layers/route';
import { LSAsLayer, LSAsDirectionLayer } from './layers/lsas';
import LSATooltipSource from './tooltip';
import { Button } from "@mui/material";

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const matcher = new URLSearchParams(window.location.search).get('matcher');

const tooltipSource = new LSATooltipSource();

export default class LSAMap extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      animationProgress: 0,
      matches: undefined,
      viewport: new WebMercatorViewport({
        longitude: 9.993682,
        latitude: 53.551086,
        zoom: 12,
        pitch: 0,
        bearing: 0,
        width: window.innerWidth,
        height: window.innerHeight,
      }),
      route: undefined
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

  matchSignalgroups = () => {
    // Fetch the matches from the server
    fetch(`${domain}:${port}/demo/api/route/${routeId}/matches${matcher ? "?matcher=" + matcher : ""}`)
    .then(res => res.json())
    .then(res => {
      this.setState({
        matches: res,
      });
    });
  }

  render() {
    const layers = [
      new RouteLayer(),
      new RouteDirectionLayer({ currentTicyclome: this.state.animationProgress }),
      new LSAsLayer({
        data: this.props.LSAs,
        getLineColor: d => {
          if (this.state.matches !== undefined) {
            for (const lsa of this.state.matches) {
              if (lsa == d.properties.lsa) {
                return [0, 255, 0];
              }
            }
          }
          return [255, 0, 0];
        },
        updateTriggers: {
          getLineColor: [this.state.matches]
        }
      }),
      new LSAsDirectionLayer({ currentTime: this.state.animationProgress }),
    ];

    return (
      <section className="deck-gl">
        <Button variant="contained" onClick={this.matchSignalgroups} className="maps-button">
          Match
        </Button>
        <DeckGL
          ref={this.deckRef}
          initialViewState={this.state.viewport}
          controller={true}
          views={[new MapView({ repeat: true })]}
          layers={layers}
          getTooltip={tooltipSource.render}>
          <Map mapStyle={BASEMAP.VOYAGER} />
        </DeckGL>
      </section>
    );
  }
}
