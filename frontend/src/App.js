import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Analytics from './analytics/analytics';
import Composer from './composer/composer';
import ComposerView from './composer_overview/composer_overview';
import JiggleVis from './jiggle-vis/jiggle-vis';
import ProjectionVis from './projection-vis/projection-vis';
import Demo from './demo/demo'
import MultiLaneAnalzer from './multi_lane_analyzer/multi_lane_analyzer'


export default class App extends React.Component {
  render() {
    return (
      <main>
        <BrowserRouter>
          <Routes>
            <Route path="/">
              <Route path="composer" element={<Composer />} />
              <Route path="composer/overview" element={<ComposerView />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="jiggle_vis" element={<JiggleVis />} />
              <Route path="projection_vis" element={<ProjectionVis />} />
              <Route path="demo" element={<Demo />} />
              <Route path="multi_lane_analyzer" element={<MultiLaneAnalzer />} />
              <Route index element={<div>Hello World!</div>}></Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </main>
    );
  }
}
