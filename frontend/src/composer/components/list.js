import React from "react";

import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';

const domain = window.location.protocol + '//' + window.location.hostname;
const port = process.env.REACT_APP_BACKEND_PORT;

export default class SGList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedSGs: props.selectedSGs,
      confirmedSGs: props.confirmedSGs
    };
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

  onSelectSGText = (sgId) => {
    // Fetch the region of the SG from the server
    fetch(`${domain}:${port}/composer/api/sg/${sgId}/region`)
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
    const { selectedSGs, confirmedSGs } = this.state;
    const { onRemove, onToggleConfirmed } = this.props;

    return (
    <List>
    {selectedSGs.map((sgId) => {
      const labelId = `checkbox-list-label-${sgId}`;

      return (
      <ListItem
        key={sgId}
        secondaryAction={
          <IconButton
            edge="end"
            aria-label="comments"
            onClick={() => onRemove(sgId)}>
              <DeleteForeverIcon />
          </IconButton>
        }
        disablePadding
      >
        <ListItemButton role={undefined} dense>
          <ListItemIcon>
            <Checkbox
            style={{ color: confirmedSGs.includes(sgId) ? '#27ae60' : '#fed330' }}
            edge="start"
            checked={confirmedSGs.includes(sgId)}
            onChange={() => onToggleConfirmed(sgId)}
            tabIndex={-1}
            disableRipple
            inputProps={{ 'aria-labelledby': labelId }}/>
          </ListItemIcon>
          <ListItemText
            id={labelId}
            primary={`SG ${sgId}`}
            onClick={() => this.onSelectSGText(sgId)}/>
        </ListItemButton>
      </ListItem>
      );
    })}
    </List>
    );
  }
}
