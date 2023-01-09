import React from 'react';

import LSAMap from './components/map';


const domain = window.location.protocol + '//' + window.location.hostname;
const routeId = new URLSearchParams(window.location.search).get('route_id');
const lsaId = new URLSearchParams(window.location.search).get('lsa_id');
const method = new URLSearchParams(window.location.search).get('method');
const port = process.env.REACT_APP_BACKEND_PORT;

export default class ProjectionVis extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      LSAs: undefined,
      projectionConnections: undefined
    };
  }

  componentDidMount() {
    // Fetch the route bindings from the server
    fetch(`${domain}:${port}/projection_vis/api/route/${routeId}/lsa${lsaId !== null ? "/" + lsaId : "/None"}?${new URLSearchParams({ method: method !== null ? method : "new" })}`)
      .then(res => res.json())
      .then(res => {
        // Visualize how the points were projected (does not work for the extended projection because there it is not a point wise projection)
        if (method !== "extended") {
          let connectionGeoJson = {
            "type": "FeatureCollection",
            "features": []
          }
          for (const lsa_1 of res["features"]) {
            if (!lsa_1["properties"]["pk"].includes("-")) {
              const corresponding_projected_lsa = res["features"].filter(lsa_2 => lsa_2["properties"]["pk"].includes("-") && lsa_2["properties"]["pk"].replace("-", "") === lsa_1["properties"]["pk"])[0];
              for (const [index, coordinate] of lsa_1["geometry"]["coordinates"].entries()) {
                const point_1 = coordinate;
                const point_2 = corresponding_projected_lsa["geometry"]["coordinates"][index];
                connectionGeoJson["features"].push({
                  "type": "Feature",
                  "geometry": {
                    "type": "LineString",
                    "coordinates": [point_1, point_2]
                  }
                })
              }
            }
          }
          this.setState({
            projectionConnections: connectionGeoJson
          });
        } else {
          fetch(`${domain}:${port}/projection_vis/api/route/${routeId}/lsa${lsaId !== null ? "/" + lsaId : "/None"}/vis`)
            .then(res => res.json())
            .then(res => {
              console.log(res)
              this.setState({
                projectionConnections: res
              });
            });
        }

        this.setState({
          LSAs: res,
        });
      });
  }

  render() {
    return (
      <main>
        {this.state.LSAs !== undefined && <LSAMap LSAs={this.state.LSAs} projectionConnections={this.state.projectionConnections} />}
      </main>
    );
  }
}
