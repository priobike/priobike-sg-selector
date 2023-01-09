import React from "react";

import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;

export default class LSAList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedLSAs: props.selectedLSAs,
      all_constellations: undefined,
      all_route_errors: undefined,
    };
  }

  componentDidUpdate(prevProps) {
    if (prevProps.selectedLSAs !== this.props.selectedLSAs) {
      this.setState({
        selectedLSAs: this.props.selectedLSAs
      });
    }
  }

  componentDidMount() {
    // Fetch all possible route errors from the server
    fetch(`${domain}:${port}/composer/api/route_error`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          all_route_errors: res
        })
      });

    // Fetch all possible constellations from the server
    fetch(`${domain}:${port}/composer/api/constellation`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          all_constellations: res
        })
      });
  }

  onSelectLSAText = (lsaId) => {
    // Fetch the region of the LSA from the server
    fetch(`${domain}:${port}/composer/api/lsa/${lsaId}/region`)
      .then(res => res.json())
      .then(res => {
        const region = {
          minX: res.min_x,
          minY: res.min_y,
          maxX: res.max_x,
          maxY: res.max_y,
        };
        this.props.onShowRegion(region);
      });
  }

  render() {
    const { selectedLSAs, all_constellations, all_route_errors } = this.state;
    const { onRemove, onToggleConfirmed, handleConstellationChange, handleErrorChange } = this.props;

    return (
      <List>

        {Object.keys(selectedLSAs).map((lsaId) => {
          const labelId = `checkbox-list-label-${lsaId}`;

          return (
            <div>


              <ListItem
                key={lsaId}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="comments"
                    onClick={() => onRemove(lsaId)}>
                    <DeleteForeverIcon />
                  </IconButton>
                }
                disablePadding
              >
                <ListItemButton role={undefined} dense>
                  <ListItemIcon>
                    <Checkbox
                      style={{ color: selectedLSAs[lsaId].confirmed ? '#27ae60' : '#fed330' }}
                      edge="start"
                      checked={selectedLSAs[lsaId].confirmed}
                      onChange={() => onToggleConfirmed(lsaId)}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }} />
                  </ListItemIcon>
                  <ListItemText
                    id={labelId}
                    primary={`LSA ${lsaId}`}
                    onClick={() => this.onSelectLSAText(lsaId)} />
                </ListItemButton>
              </ListItem>
              <List>
                <ListItem>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel id="route_error-select-label">Route Error</InputLabel>
                    <Select
                      labelId="route_error-select-label"
                      id="route_error-select"
                      value={selectedLSAs[lsaId].corresponding_route_error}
                      label="Route Error"
                      onChange={e => handleErrorChange(e, lsaId)}
                    >
                      <MenuItem value={undefined}>
                        <em>None</em>
                      </MenuItem>
                      {all_route_errors && all_route_errors.map((route_error) => {
                        return <MenuItem value={route_error.pk}>{route_error.fields.name}</MenuItem>
                      })}
                    </Select>
                  </FormControl>
                </ListItem>
                <ListItem>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel id="constellation-select-label">Constellation</InputLabel>
                    <Select
                      labelId="constellation-select-label"
                      id="constellation-select"
                      value={selectedLSAs[lsaId].corresponding_constellation}
                      label="Constellation"
                      onChange={e => handleConstellationChange(e, lsaId)}
                    >
                      <MenuItem value={undefined}>
                        <em>None</em>
                      </MenuItem>
                      {all_constellations && all_constellations.map((constellation) => {
                        return <MenuItem value={constellation.pk}>{constellation.fields.name}</MenuItem>
                      })}
                    </Select>
                  </FormControl>
                </ListItem>
              </List>


            </div>
          );
        })}
      </List>
    );
  }
}
