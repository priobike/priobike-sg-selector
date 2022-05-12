import React from "react";

import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Avatar from "@mui/material/Avatar";

import { purple } from "@mui/material/colors";


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class CrossingsBar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      crossings: [],
      selectedCrossing: null,
    };
  }

  componentDidMount() {
    // Fetch the crossings from the server
    fetch(`${domain}:${port}/composer/api/route/${routeId}/crossings`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          crossings: res,
        });
      });
  }

  selectCrossing = (crossing) => {
    this.setState({
      selectedCrossing: crossing.id,
    });

    const [ minX, minY, maxX, maxY ] = crossing.extent;
    const region = {
      minX: minX,
      minY: minY,
      maxX: maxX,
      maxY: maxY,
    };
    console.log(region);
    this.props.onShowRegion(region);
  };

  render() {
    return (
      <Stack direction="column" className="crossings-bar" spacing={1}>
        {this.state.crossings.map((crossing) => {
          return (
            <Chip
              key={crossing.id}
              onClick={() => this.selectCrossing(crossing)}
              color={this.state.selectedCrossing === crossing.id ? 'primary' : 'default'}
              avatar={<Avatar>{crossing.sgs}</Avatar>}
              style={{ margin: '0.5rem' }}
              size="small"
              label={crossing.id}
            />
          );
        })}
      </Stack>
    );
  }
}
