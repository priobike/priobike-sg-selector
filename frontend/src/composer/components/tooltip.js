import ReactDOMServer from 'react-dom/server';
import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';


class Tooltip extends React.Component {
  render() {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" component="div">
            SG {this.props.data.pk}
          </Typography>
          <Typography sx={{ fontSize: 14 }} color="text.secondary">
            {this.props.data.fields.lane_type}, SG {this.props.data.fields.signal_group_id}
          </Typography>
        </CardContent>
      </Card>
    );
  }
}

export default class SGTooltipSource {
  constructor() {
    this.cache = undefined;
  }

  render({object}) {
    if (!object) return object && {};
    const sgId = object.properties.sg;
    if (this.cache !== undefined && this.cache.id === sgId) {
      const data = this.cache.data; // Cached data
      const element = <Tooltip data={data} />;
      return object && {
        html: ReactDOMServer.renderToString(element),
        style: { background: 'transparent' }
      };
    }

    const domain = window.location.protocol + '//' + window.location.hostname;
    fetch(`${domain}:${process.env.REACT_APP_BACKEND_PORT}/composer/api/sg/${sgId}/metadata`)
      .then(response => response.json())
      .then(data => {
        this.cache = {
          id: sgId,
          data: data,
        };
      });

    const element = <Card>
      <CardContent>
        <CircularProgress />
      </CardContent>
    </Card>;

    return object && {
      html: ReactDOMServer.renderToString(element),
      style: { background: 'transparent' }
    };
  }
}
