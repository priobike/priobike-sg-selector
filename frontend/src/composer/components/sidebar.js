import React from "react";
import { Typography, Button, Stack } from '@mui/material';

import LSAList from './list';

const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;
const mapData = new URLSearchParams(window.location.search).get('map_data');

export default class LSASidebar extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedLSAs: props.selectedLSAs,
      blockSubmitting: false
    };
  }

  async submitRouteBindings() {
    const { selectedLSAs } = this.state;

    this.setState({ blockSubmitting: true });

    await fetch(`${domain}:${port}/composer/api/route/${routeId}/bindings${mapData ? "?map_data=" + mapData : ""}`, {
      method: 'POST',
      body: JSON.stringify(selectedLSAs)
    });

    this.setState({ blockSubmitting: false });
  }

  async goToNextRoute() {
    const response = await fetch(`${domain}:${port}/composer/api/route/${routeId}/next`);
    const json = await response.json();
    const nextRouteId = json['next_route'];
    // Set the window location to the next route
    window.location.href = `/composer?route_id=${nextRouteId}`;
  }

  componentDidUpdate(prevProps) {
    if (prevProps.selectedLSAs !== this.props.selectedLSAs) {
      this.setState({
        selectedLSAs: this.props.selectedLSAs
      });
    }
  }

  handleConstellationChange = (event, lsaId) => {
    let lsas = structuredClone(this.state.selectedLSAs);
    lsas[lsaId].corresponding_constellation = event.target.value
    this.setState({
      selectedLSAs: lsas
    })
  };

  handleErrorChange = (event, lsaId) => {
    let lsas = structuredClone(this.state.selectedLSAs);
    lsas[lsaId].corresponding_route_error = event.target.value
    this.setState({
      selectedLSAs: lsas
    })
  };

  render() {
    const { selectedLSAs, blockSubmitting } = this.state;
    const { onRemove, onToggleConfirmed, onShowRegion } = this.props;

    return (
      <aside>
        <Stack
          direction="column"
          spacing={2}
          sx={{ pt: '2rem', pb: '2rem' }}>
          <Typography variant="h5">
            Route Composer
          </Typography>
          <Typography variant="body1">
            Click on the LSA geometries to add them to this list.
            Check the item if you are sure that the geometry is
            fitting to the route.
          </Typography>
          <LSAList
            selectedLSAs={selectedLSAs}
            onRemove={onRemove}
            onToggleConfirmed={onToggleConfirmed}
            onShowRegion={onShowRegion}
            handleConstellationChange={this.handleConstellationChange}
            handleErrorChange={this.handleErrorChange}
          />
          <Button
            disabled={blockSubmitting}
            variant="contained"
            onClick={() => this.submitRouteBindings()}
            color="primary">
            Submit Route Bindings ({mapData ? mapData : "osm"})
          </Button>
          <Button
            disabled={blockSubmitting}
            variant="contained"
            onClick={() => this.goToNextRoute()}
            color="primary">
            Go to Next Route
          </Button>
        </Stack>
      </aside>
    );
  }
}
