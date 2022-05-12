import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Composer from './composer/composer';


export default class App extends React.Component {
  render() {
    return (
      <main>
        <BrowserRouter>
          <Routes>
            <Route path="/">
              <Route path="composer" element={<Composer />} />
              <Route index element={<div>Hello World!</div>}></Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </main>
    );
  }
}
