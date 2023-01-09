import React from "react";
import { Typography, Button, Stack, TextField, Grid, Slider } from '@mui/material';

const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class LSASidebar extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      blockSubmitting: false,
      onUpdateLSAs: props.onUpdateLSAs,
      numberOfJiggledLSAs: props.jiggleParams.numberOfJiggledLSAs ? props.jiggleParams.numberOfJiggledLSAs : 1,
      rotationLowerBound: props.jiggleParams.rotationLowerBound ? props.jiggleParams.rotationLowerBound : -3,
      rotationUpperBound: props.jiggleParams.rotationUpperBound ? props.jiggleParams.rotationUpperBound : 3,
      scaleLowerBound: props.jiggleParams.scaleLowerBound ? props.jiggleParams.scaleLowerBound : 0.975,
      scaleUpperBound: props.jiggleParams.scaleUpperBound ? props.jiggleParams.scaleUpperBound : 1.025,
      translationXLowerBound: props.jiggleParams.translationXLowerBound ? props.jiggleParams.translationXLowerBound : -5,
      translationXUpperBound: props.jiggleParams.translationXUpperBound ? props.jiggleParams.translationXUpperBound : 5,
      translationYLowerBound: props.jiggleParams.translationYLowerBound ? props.jiggleParams.translationYLowerBound : -5,
      translationYUpperBound: props.jiggleParams.translationYUpperBound ? props.jiggleParams.translationYUpperBound : 5,
    };
  }

  async submitJiggles() {
    this.setState({ blockSubmitting: true });
  }

  async goToNextRoute() {
    const response = await fetch(`${domain}:${port}/composer/api/route/${routeId}/next`);
    const json = await response.json();
    const nextRouteId = json['next_route'];
    const params = {
      route_id: nextRouteId,
      numberOfJiggledLSAs: this.state.numberOfJiggledLSAs,
      rotationLowerBound: this.state.rotationLowerBound,
      rotationUpperBound: this.state.rotationUpperBound,
      scaleLowerBound: this.state.scaleLowerBound,
      scaleUpperBound: this.state.scaleUpperBound,
      translationXLowerBound: this.state.translationXLowerBound,
      translationXUpperBound: this.state.translationXUpperBound,
      translationYLowerBound: this.state.translationYLowerBound,
      translationYUpperBound: this.state.translationYUpperBound
    }
    // Set the window location to the next route
    window.location.href = `/jiggle_vis?` + new URLSearchParams(params);

  }

  async getLSAs() {
    this.setState({ blockSubmitting: true });

    const params = {
      numberOfJiggledLSAs: this.state.numberOfJiggledLSAs,
      rotationLowerBound: this.state.rotationLowerBound,
      rotationUpperBound: this.state.rotationUpperBound,
      scaleLowerBound: this.state.scaleLowerBound,
      scaleUpperBound: this.state.scaleUpperBound,
      translationXLowerBound: this.state.translationXLowerBound,
      translationXUpperBound: this.state.translationXUpperBound,
      translationYLowerBound: this.state.translationYLowerBound,
      translationYUpperBound: this.state.translationYUpperBound
    }

    await fetch(`${domain}:${port}/jiggle_vis/api/route/${routeId}/lsa?` + new URLSearchParams(params))
      .then(res => res.json())
      .then(res => {
        this.state.onUpdateLSAs(res);
      });

    const routeIdParam = {
      route_id: routeId
    };

    const newParams = {...routeIdParam, ...params};
    
    if (window.history.pushState) {
      var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + new URLSearchParams(newParams);
      window.history.pushState({ path: newurl }, '', newurl);
    }

    this.setState({ blockSubmitting: false });
  }

  render() {
    const { blockSubmitting } = this.state;

    return (
      <aside>
        <Stack
          direction="column"
          spacing={2}
          sx={{ pt: '2rem', pb: '2rem' }}>
          <Typography variant="h5">
            Jiggling Test Tool
          </Typography>
          <Typography variant="body1">
            Try out different values and see how they result in different LSA-geometries (green: original, yellow: jiggled).
          </Typography>
          <Typography id="number-of-jiggled-lsas" gutterBottom>
            Number of jiggled LSAs: {this.state.numberOfJiggledLSAs}
          </Typography>
          <Slider
            value={this.state.numberOfJiggledLSAs}
            onChange={e => this.setState({ numberOfJiggledLSAs: e.target.value })}
            aria-labelledby="number-of-jiggled-lsas"
          />
          <Typography variant="h6">
            Rotation
          </Typography>
          <Grid container spacing={2} columns={16}>
            <Grid item xs={8}>
              <TextField id="rotation-lower-bound" type="number" label="Lower Bound" variant="outlined"
                value={this.state.rotationLowerBound} onChange={e => this.setState({ rotationLowerBound: e.target.value })} />
            </Grid>
            <Grid item xs={8}>
              <TextField id="rotation-upper-bound" type="number" label="Upper Bound" variant="outlined"
                value={this.state.rotationUpperBound} onChange={e => this.setState({ rotationUpperBound: e.target.value })} />
            </Grid>
          </Grid>
          <Typography variant="h6">
            Scale
          </Typography>
          <Grid container spacing={2} columns={16}>
            <Grid item xs={8}>
              <TextField id="scale-lower-bound" type="number" label="Lower Bound" variant="outlined"
                value={this.state.scaleLowerBound} onChange={e => this.setState({ scaleLowerBound: e.target.value })} />
            </Grid>
            <Grid item xs={8}>
              <TextField id="scale-upper-bound" type="number" label="Upper Bound" variant="outlined"
                value={this.state.scaleUpperBound} onChange={e => this.setState({ scaleUpperBound: e.target.value })} />
            </Grid>
          </Grid>
          <Typography variant="h6">
            Translation X
          </Typography>
          <Grid container spacing={2} columns={16}>
            <Grid item xs={8}>
              <TextField id="translation-x-lower-bound" type="number" label="Lower Bound" variant="outlined"
                value={this.state.translationXLowerBound} onChange={e => this.setState({ translationXLowerBound: e.target.value })} />
            </Grid>
            <Grid item xs={8}>
              <TextField id="translation-x-upper-bound" type="number" label="Upper Bound" variant="outlined"
                value={this.state.translationXUpperBound} onChange={e => this.setState({ translationXUpperBound: e.target.value })} />
            </Grid>
          </Grid>
          <Typography variant="h6">
            Translation Y
          </Typography>
          <Grid container spacing={2} columns={16}>
            <Grid item xs={8}>
              <TextField id="translation-y-lower-bound" type="number" label="Lower Bound" variant="outlined"
                value={this.state.translationYLowerBound} onChange={e => this.setState({ translationYLowerBound: e.target.value })} />
            </Grid>
            <Grid item xs={8}>
              <TextField id="translation-y-upper-bound" type="number" label="Upper Bound" variant="outlined"
                value={this.state.translationYUpperBound} onChange={e => this.setState({ translationYUpperBound: e.target.value })} />
            </Grid>
          </Grid>
          <Button
            disabled={blockSubmitting}
            variant="contained"
            onClick={() => this.getLSAs()}
            color="primary">
            Apply jiggles
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
