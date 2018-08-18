import "phoenix_html"

import React from 'react';
import ReactDOM from 'react-dom';

import { Route } from 'react-router'
import { BrowserRouter } from 'react-router-dom'

import Main from './components/Main';

import { ApolloClient } from 'apollo-client'

import { ApolloLink } from 'apollo-link'
import { ApolloProvider } from 'react-apollo'
import { hasSubscription } from "@jumpn/utils-graphql";

import {createHttpLink} from "apollo-link-http";

import * as AbsintheSocket from "@absinthe/socket";
import {InMemoryCache} from "apollo-cache-inmemory";
import { createAbsintheSocketLink } from "@absinthe/socket-apollo-link";
import { Socket as PhoenixSocket } from "phoenix";


const absintheSocketLink = createAbsintheSocketLink(AbsintheSocket.create(
  new PhoenixSocket("ws://localhost:4000/socket")
))

const link = new ApolloLink.split(
  operation => hasSubscription(operation.query),
  absintheSocketLink,
  createHttpLink({uri: "/graphql"})
)

const client = new ApolloClient({
  link,
  cache: new InMemoryCache()
})

class Root extends React.Component {
  render() {
    return (
      <div>
        <ApolloProvider client={client}>
          <BrowserRouter>
            <div>
              <Route exact path="/" component={Main} />
            </div>
          </BrowserRouter>
        </ApolloProvider>
      </div>
    )
  }
}

ReactDOM.render(<Root />, document.getElementById("main"));

