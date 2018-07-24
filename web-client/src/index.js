import './index.css';
import React from 'react';
import ReactDOM from 'react-dom';
import ApolloClient from 'apollo-client'
import { Route } from 'react-router'
import { BrowserRouter } from 'react-router-dom'
import { createNetworkInterface, ApolloProvider } from 'react-apollo'
import Main from './components/Main';

const client = new ApolloClient({
  networkInterface: createNetworkInterface({
    uri: 'http://localhost:4000/graphql'
  }),
})

class Root extends React.Component {
  render() {
    return (
      <ApolloProvider client={client}>
        <BrowserRouter>
          <div>
            <Route exact path="/" component={Main} />
          </div>
        </BrowserRouter>
      </ApolloProvider>
    )
  }
}

ReactDOM.render(
    <Root />,
    document.getElementById('app')
);
