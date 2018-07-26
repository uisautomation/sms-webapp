import './index.css';

import * as React from 'react';
import * as ReactDOM from 'react-dom';

import { BrowserRouter, Route } from 'react-router-dom'

import AnalyticsPage from './pages/AnalyticsPage';
import IndexPage from './pages/IndexPage';
import MediaPage from './pages/MediaPage';

ReactDOM.render(
  <BrowserRouter>
    <div>
      <Route exact={true} path="/" component={IndexPage} />
      <Route exact={true} path="/media/:pk" component={MediaPage} />
      <Route exact={true} path="/media/:pk/analytics" component={AnalyticsPage} />
    </div>
  </BrowserRouter>,
  document.getElementById('app')
);
