import React from "react";
import { Typography, Button, Stack } from '@mui/material';

import SGList from './list';

const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class SGSidebar extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedSGs: props.selectedSGs,
      confirmedSGs: props.confirmedSGs,
      blockSubmitting: false
    };
  }

  async submitRouteBindings() {
    const { selectedSGs, confirmedSGs } = this.state;

    this.setState({ blockSubmitting: true });

    const payload = {
      sgIds: selectedSGs,
      confirmed: confirmedSGs
    }
    await fetch(`${domain}:${port}/composer/api/route/${routeId}/bindings`, {
      method: 'POST',
      body: JSON.stringify(payload)
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
    if (prevProps.selectedSGs !== this.props.selectedSGs) {
      this.setState({
        selectedSGs: this.props.selectedSGs
      });
    }
    if (prevProps.confirmedSGs !== this.props.confirmedSGs) {
      this.setState({
        confirmedSGs: this.props.confirmedSGs
      });
    }
  }

  render() {
    const { selectedSGs, confirmedSGs, blockSubmitting } = this.state;
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
            Click on the SG geometries to add them to this list.
            Check the item if you are sure that the geometry is
            fitting to the route.
          </Typography>
          <SGList
            selectedSGs={selectedSGs}
            onRemove={onRemove}
            onToggleConfirmed={onToggleConfirmed}
            onShowRegion={onShowRegion}
            confirmedSGs={confirmedSGs} />
          <Button
            disabled={blockSubmitting}
            variant="contained"
            onClick={() => this.submitRouteBindings()}
            color="primary">
            Submit Route Bindings
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
