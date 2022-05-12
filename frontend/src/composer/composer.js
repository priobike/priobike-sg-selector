import React from 'react';

import CrossingsBar from './components/bar';
import SGMap from './components/map';
import SGSidebar from './components/sidebar';


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class Composer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedSGs: [],
      confirmedSGs: [],
      region: null,
    };
  }

  componentDidMount() {
    // Fetch the route bindings from the server
    fetch(`${domain}:${port}/composer/api/route/${routeId}/bindings`)
      .then(res => res.json())
      .then(res => {
        this.setState({
          selectedSGs: res.sgIds,
          confirmedSGs: res.confirmed,
        });
      });
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
    if (prevProps.region !== this.props.region) {
      this.setState({
        region: this.props.region
      });
    }
  }

  onShowRegion = (region) => {
    this.setState({
      region: region,
    });
  };

  onRemove = (sgId) => {
    this.setState((prevState) => ({
      selectedSGs: prevState.selectedSGs.filter((sg) => sg !== sgId),
      confirmedSGs: prevState.confirmedSGs.filter((sg) => sg !== sgId),
    }));
  };

  onToggleConfirmed = (sgId) => {
    this.setState((prevState) => {
      // If the sg is already confirmed, remove it from the confirmed list
      if (prevState.confirmedSGs.includes(sgId)) {
        return {
          confirmedSGs: prevState.confirmedSGs.filter((sg) => sg !== sgId),
        };
      }
      // If the SG is not confirmed, add it to the confirmed list
      return {
        confirmedSGs: [...prevState.confirmedSGs, sgId],
      };
    });
  };

  onClickSG = (sgId) => {
    this.setState((prevState) => {
      if (prevState.selectedSGs.includes(sgId) && prevState.confirmedSGs.includes(sgId)) {
        // Remove the SG from the confirmed and selected lists
        return {
          selectedSGs: prevState.selectedSGs.filter((sg) => sg !== sgId),
          confirmedSGs: prevState.confirmedSGs.filter((sg) => sg !== sgId),
        };
      }
      if (prevState.selectedSGs.includes(sgId)) {
        // Promote the SG from the selected to the confirmed list
        return {
          confirmedSGs: [...prevState.confirmedSGs, sgId],
        }
      }
      return {
        // Add SG to selectedSGs
        selectedSGs: [...prevState.selectedSGs, sgId],
      };
    });
  };

  render() {
    return (
      <main>
        <CrossingsBar onShowRegion={this.onShowRegion}/>
        <SGMap
          region={this.state.region}
          selectedSGs={this.state.selectedSGs}
          confirmedSGs={this.state.confirmedSGs}
          onClickSG={this.onClickSG} />
        <SGSidebar
          selectedSGs={this.state.selectedSGs}
          confirmedSGs={this.state.confirmedSGs}
          onRemove={this.onRemove}
          onToggleConfirmed={this.onToggleConfirmed}
          onShowRegion={this.onShowRegion} />
      </main>
    );
  }
}
