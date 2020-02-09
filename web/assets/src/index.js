import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import css from "../css/app.css"
import "phoenix_html"


ReactDOM.render(<App />, document.getElementById('root'));
serviceWorker.unregister();
