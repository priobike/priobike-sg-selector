import React from 'react';

import CrossingsBar from './components/bar';
import LSAMap from './components/map';
import LSASidebar from './components/sidebar';


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const lsaId = new URLSearchParams(window.location.search).get('lsa_id');
const showDuplicates = new URLSearchParams(window.location.search).get('show_duplicates');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class Composer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedLSAs: {},
      region: null,
    };
  }

  async componentDidMount() {
    // Fetch the route bindings from the server
    await fetch(`${domain}:${port}/composer/api/route/${routeId}/bindings?${new URLSearchParams({ show_duplicates: showDuplicates === "false" ? false : true })}`)
      .then(res => res.json())
      .then(res => {
        console.log(res)
        this.setState({
          selectedLSAs: res
        })
      });

    if (lsaId !== undefined && lsaId.length > 0) {
      await fetch(`${domain}:${port}/composer/api/lsa/${lsaId}/region`)
        .then(res => res.json())
        .then(res => {
          const region = {
            minX: res.min_x,
            minY: res.min_y,
            maxX: res.max_x,
            maxY: res.max_y,
          };
          this.onShowRegion(region);
        });
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.selectedLSAs !== this.props.selectedLSAs) {
      this.setState({
        selectedLSAs: this.props.selectedLSAs
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

  removeLsaFromSelectedLSAs = (allLSAs, lsaId) => {
    const { [lsaId]: _, ...rest } = allLSAs
    return { ...rest }
  }

  onRemove = (lsaId) => {
    this.setState((prevState) => ({
      selectedLSAs: this.removeLsaFromSelectedLSAs(prevState.selectedLSAs, lsaId),
    }));
  };

  onToggleConfirmed = (lsaId) => {
    this.setState((prevState) => {
      let lsas = structuredClone(prevState.selectedLSAs)
      lsas[lsaId].confirmed = !lsas[lsaId].confirmed
      console.log(lsas[lsaId])
      return {
        selectedLSAs: lsas
      }
    });
  };

  onClickLSA = (lsaId) => {
    this.setState((prevState) => {
      console.log(prevState.selectedLSAs[lsaId])
      if (prevState.selectedLSAs[lsaId] !== undefined && prevState.selectedLSAs[lsaId].confirmed) {
        // Remove the LSA the selectedLSAs (thus also remove confirmed state)
        return {
          selectedLSAs: this.removeLsaFromSelectedLSAs(prevState.selectedLSAs, lsaId)
        };
      }
      if (prevState.selectedLSAs[lsaId] !== undefined) {
        // Set confirmed state
        let lsas = structuredClone(prevState.selectedLSAs);
        lsas[lsaId].confirmed = !lsas[lsaId].confirmed
        return {
          selectedLSAs: lsas
        }
      }
      // Add lsa to selectedLSAs
      let lsas = structuredClone(prevState.selectedLSAs);
      lsas[lsaId] = {
        confirmed: false,
        corresponding_constellation: null,
        corresponding_route_error: null
      }

      return {
        selectedLSAs: lsas
      }
    });
  };

  render() {
    return (
      <main>
        <CrossingsBar onShowRegion={this.onShowRegion} />
        <LSAMap
          region={this.state.region}
          selectedLSAs={this.state.selectedLSAs}
          onClickLSA={this.onClickLSA} />
        <LSASidebar
          selectedLSAs={this.state.selectedLSAs}
          onRemove={this.onRemove}
          onToggleConfirmed={this.onToggleConfirmed}
          onShowRegion={this.onShowRegion} />
      </main>
    );
  }
}
