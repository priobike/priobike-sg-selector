import React from 'react';

import LSAMap from './components/map';
import LSASidebar from './components/sidebar';


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;
const params = new URLSearchParams(window.location.search);

export default class JiggleVis extends React.Component {
  constructor(props) {
    super(props);

    let jiggleParams = {};
    for(const value of params.keys()) {
      if(value !== "route_id") {
        jiggleParams[value] = params.get(value);
      }
    }

    this.state = {
      LSAs: undefined,
      jiggleParams: jiggleParams
    };
  }

  componentDidMount() {
    // Fetch the route bindings from the server
    fetch(`${domain}:${port}/jiggle_vis/api/route/${routeId}/lsa?` + new URLSearchParams(this.state.jiggleParams))
      .then(res => res.json())
      .then(res => {
        this.setState({
          LSAs: res
        });
      });
  }

  updateLSAs = (lsas) => {
    this.setState({
      LSAs: lsas
    });
  }

  render() {
    return (
      <main>
        {this.state.LSAs !== undefined && <LSAMap LSAs={this.state.LSAs} />}
        <LSASidebar jiggleParams={this.state.jiggleParams} onUpdateLSAs={this.updateLSAs}/>
      </main>
    );
  }
}
