import * as React from 'react';
import * as ReactDOM from 'react-dom';

import IndexPage from './pages/IndexPage';
import MediaPage from './pages/MediaPage';

const mappings = {
  'root': <IndexPage/>,
  'media': <MediaPage/>
};

for (var id in mappings) {
  let element = document.getElementById(id);
  if (element) {
    ReactDOM.render(mappings[id], element as HTMLElement);
  }
}
