import React from 'react';

import LSAMap from './components/map';


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class Demo extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      LSAs: undefined
    };
  }

  componentDidMount() {
    // Fetch the signalgroups from the server
    fetch(`${domain}:${port}/demo/api/signalgroups`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          LSAs: res,
        });
      });
  }

  render() {
    return (
      <main>
        {this.state.LSAs !== undefined && <LSAMap LSAs={this.state.LSAs} />}
      </main>
    );
  }
}
