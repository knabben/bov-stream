import React from 'react'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import Select from 'react-select'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs'


class Main extends React.Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <div className="row">
        <div className="col-6 top-header"> </div>
      </div>
    )
  }
}

const query = gql`
  {
    companies {
      id
      name
      symbol
    }
  }
`
export default graphql(query)(Main)
