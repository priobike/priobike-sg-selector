import React from 'react';
import ListSubheader from '@mui/material/ListSubheader';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import Grid from '@mui/material/Grid';
import CableIcon from '@mui/icons-material/Cable';
import BrokenImageIcon from '@mui/icons-material/BrokenImage';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import EditRoadIcon from '@mui/icons-material/EditRoad';
import Typography from '@mui/material/Typography';
import SyncIcon from '@mui/icons-material/Sync';
import Button from '@mui/material/Button';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;
const mapData = new URLSearchParams(window.location.search).get('map_data');

export default class Composer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      allConstellations: [],
      expandedConstellations: [],
      allRouteErrors: [],
      expandedRouteErrors: [],
      bindingsForConstellations: {},
      bindingsForRouteErrors: {},
      errorBindingsInFiles: [],
      errorBindingsInDatabase: [],
      loading: false
    };
  }

  async componentDidMount() {
    this.setState({
      loading: true
    })
    // Fetch all constellations from the server
    await this.getConstellations();

    // Fetch all route errors from the server
    await this.getRouteErrors();
  }

  async componentDidUpdate(prevProps, prevState) {
    if (prevState.allConstellations !== this.state.allConstellations && this.state.allConstellations.length > 0) {
      let bindingsForConstellations = {};
      this.setState({
        loading: true
      })
      for (const constellation of this.state.allConstellations) {
        await fetch(`${domain}:${port}/composer/api/constellation/${constellation.pk}/stats`)
          .then(res => res.json())
          .then(res => {
            bindingsForConstellations[constellation.pk] = res
          });
      }
      this.setState({
        bindingsForConstellations: bindingsForConstellations,
      })

      await this.healthCheckBindingFiles();
      await this.healthCheckBindingsDatabase();

      this.setState({
        loading: false
      })
    }
    if (prevState.allRouteErrors !== this.state.allRouteErrors && this.state.allRouteErrors.length > 0) {
      let bindingsForRouteErrors = {};
      this.setState({
        loading: true
      })
      for (const routeError of this.state.allRouteErrors) {
        await fetch(`${domain}:${port}/composer/api/route_error/${routeError.pk}/stats`)
          .then(res => res.json())
          .then(res => {
            bindingsForRouteErrors[routeError.pk] = res
          });
      }
      this.setState({
        bindingsForRouteErrors: bindingsForRouteErrors
      })

      await this.healthCheckBindingFiles();
      await this.healthCheckBindingsDatabase();

      this.setState({
        loading: false
      })
    }
  }

  handleConstellationExpansionClick = (constellation) => {
    let expandedConstellations = this.state.expandedConstellations;
    if (expandedConstellations.includes(constellation)) {
      expandedConstellations = expandedConstellations.filter(item => item !== constellation);
    } else {
      expandedConstellations.push(constellation);
    }

    this.setState({
      expandedConstellations: expandedConstellations
    })
  };

  handleRouteErrorExpansionClick = (routeError) => {
    let expandedRouteErrors = this.state.expandedRouteErrors;
    if (expandedRouteErrors.includes(routeError)) {
      expandedRouteErrors = expandedRouteErrors.filter(item => item !== routeError);
    } else {
      expandedRouteErrors.push(routeError);
    }

    this.setState({
      expandedRouteErrors: expandedRouteErrors
    })
  };

  getUpdates = async () => {
    this.setState({
      loading: true
    })
    await this.getConstellations();
    await this.getRouteErrors();
    this.setState({
      loading: false
    })
  }

  getRouteErrors = async () => {
    // Fetch all route errors from the server
    await fetch(`${domain}:${port}/composer/api/route_error`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          allRouteErrors: res
        })
      });
  }

  getConstellations = async () => {
    // Fetch all constellations from the server
    await fetch(`${domain}:${port}/composer/api/constellation`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          allConstellations: res
        })
      });
  }

  healthCheckBindingFiles = async () => {
    await fetch(`${domain}:${port}/composer/api/health_check/bindings/files${mapData ? "?map_data=" + mapData : ""}`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          errorBindingsInFiles: res
        })
      });
  }

  healthCheckBindingsDatabase = async () => {
    await fetch(`${domain}:${port}/composer/api/health_check/bindings/database${mapData ? "?map_data=" + mapData : ""}`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          errorBindingsInDatabase: res
        })
      });
  }

  render() {
    const { allConstellations, allRouteErrors, expandedConstellations, expandedRouteErrors, bindingsForConstellations, bindingsForRouteErrors, errorBindingsInDatabase, errorBindingsInFiles } = this.state;
    return (
      <main>
        <Grid container spacing={2}>
          <Grid item xs={8}>
            <Typography variant="h4" component="h1">
              Overview of the created bindings ({mapData ? mapData : "osm"}):
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Button variant="contained" color="success" onClick={() => this.getUpdates()} fullWidth={true} startIcon={<SyncIcon />} disabled={this.state.loading}>
              Update
            </Button>
          </Grid>
        </Grid>
        <List
          sx={{ width: '100%', bgcolor: 'background.paper' }}
          component="nav"
          aria-labelledby="constellations"
          subheader={
            <ListSubheader component="div" id="constellations">
              Constellations
            </ListSubheader>
          }
        >
          {allConstellations.map((constellation) => {
            return [<ListItemButton divider={true} onClick={() => this.handleConstellationExpansionClick(constellation)}>
              <ListItemIcon>
                <EditRoadIcon />
              </ListItemIcon>
              <ListItemText primary={`${constellation.fields.custom_id} - Anzahl: ${bindingsForConstellations[constellation.pk] !== undefined ? bindingsForConstellations[constellation.pk].length : "0"} - ${constellation.fields.name}`} secondary={constellation.fields.description} />
              {expandedConstellations.includes(constellation) ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>,
            <Collapse in={expandedConstellations.includes(constellation)} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {bindingsForConstellations[constellation.pk] !== undefined && bindingsForConstellations[constellation.pk].map((binding) => {
                  return <ListItemButton divider={true} sx={{ pl: 4, backgroundColor: binding.fields.confirmed ? "#8bc34a" : "#ffeb3b" }} onClick={() => window.open(`../composer?route_id=${binding.fields.route}&lsa_id=${binding.fields.lsa}`, '_blank')}>
                    <ListItemIcon>
                      <CableIcon />
                    </ListItemIcon>
                    <ListItemText primary={`Route: ${binding.fields.route} - LSA: ${binding.fields.lsa}`} secondary={`Binding-ID: ${binding.pk}`} />
                  </ListItemButton>
                })
                }
              </List>
            </Collapse>
            ]
          })}
        </List>
        <List
          sx={{ width: '100%', bgcolor: 'background.paper' }}
          component="nav"
          aria-labelledby="route-errors"
          subheader={
            <ListSubheader component="div" id="route-errors">
              Route Errors
            </ListSubheader>
          }
        >
          {allRouteErrors.map((routeError) => {
            return [<ListItemButton divider={true} onClick={() => this.handleRouteErrorExpansionClick(routeError)}>
              <ListItemIcon>
                <BrokenImageIcon />
              </ListItemIcon>
              <ListItemText primary={`${routeError.fields.custom_id} - Anzahl: ${bindingsForRouteErrors[routeError.pk] !== undefined ? bindingsForRouteErrors[routeError.pk].length : "0"} - ${routeError.fields.name}`} secondary={routeError.fields.description} />
              {expandedRouteErrors.includes(routeError) ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>,
            <Collapse in={expandedRouteErrors.includes(routeError)} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {bindingsForRouteErrors[routeError.pk] !== undefined && bindingsForRouteErrors[routeError.pk].map((binding) => {
                  return <ListItemButton divider={true} sx={{ pl: 4, backgroundColor: binding.fields.confirmed ? "#8bc34a" : "#ffeb3b" }} onClick={() => window.open(`../composer?route_id=${binding.fields.route}&lsa_id=${binding.fields.lsa}`, '_blank')}>
                    <ListItemIcon>
                      <CableIcon />
                    </ListItemIcon>
                    <ListItemText primary={`Route: ${binding.fields.route} - LSA: ${binding.fields.lsa}`} secondary={`Binding-ID: ${binding.pk}`} />
                  </ListItemButton>
                })
                }
              </List>
            </Collapse>
            ]
          })}
        </List>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Button variant="contained" color="success" onClick={async () => {
              this.setState({
                loading: true
              })
              await this.healthCheckBindingFiles();
              this.setState({
                loading: false
              })
            }} fullWidth={true} startIcon={<HealthAndSafetyIcon />} disabled={this.state.loading}>
              Health-Check binding files
            </Button>
            <List
              sx={{ width: '100%', bgcolor: 'background.paper' }}
              component="nav"
              aria-labelledby="constellations"
              subheader={
                <ListSubheader component="div" id="constellations">
                  Bindings in .json files but not in database (or different in database)
                </ListSubheader>
              }
            >
              {errorBindingsInFiles.map((binding) => {
                return <ListItemButton divider={true} sx={{ backgroundColor: binding.present ? "#fff89c" : "#ff8080" }}>
                  <ListItemIcon>
                    <EditRoadIcon />
                  </ListItemIcon>
                  <ListItemText primary={`${binding.present ? "Different in database:" : "Not in database:"} Route: ${binding.binding.route} - LSA: ${binding.binding.lsa}`} secondary={`Binding-ID: ${binding.binding.id}`} />
                </ListItemButton>
              })}
            </List>
          </Grid>
          <Grid item xs={6}>
            <Button variant="contained" color="success" onClick={async () => {
              this.setState({
                loading: true
              })
              await this.healthCheckBindingsDatabase();
              this.setState({
                loading: false
              })
            }} fullWidth={true} startIcon={<HealthAndSafetyIcon />} disabled={this.state.loading}>
              Health-Check bindings in database
            </Button>
            <List
              sx={{ width: '100%', bgcolor: 'background.paper' }}
              component="nav"
              aria-labelledby="constellations"
              subheader={
                <ListSubheader component="div" id="constellations">
                  Bindings in database but not in .json files (or different in .json files)
                </ListSubheader>
              }
            >
              {errorBindingsInDatabase.map((binding) => {
                return <ListItemButton divider={true} sx={{ backgroundColor: binding.present ? "#fff89c" : "#ff8080" }}>
                  <ListItemIcon>
                    <EditRoadIcon />
                  </ListItemIcon>
                  <ListItemText primary={`${binding.present ? "Different in .json files:" : "Not in .json files:"} Route: ${binding.binding.route} - LSA: ${binding.binding.lsa}`} secondary={`Binding-ID: ${binding.binding.id}`} />
                </ListItemButton>
              })}
            </List>
          </Grid>
        </Grid>
      </main>
    );
  }
}
