import React, { Component } from 'react'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import { Link } from 'react-router-dom'
import Select from 'react-select'
import * as d3 from 'd3'



class SimpleGraph extends Component {
  render() {
    if (this.props.data.loading) {
      return (<div>Loading...</div>)
    }

    const { companyDays } = this.props.data
    const parseDate = d3.timeParse("%Y-%m-%d %H:%M:%SZ");

    const chartData = companyDays.map((item) => ({
      open: item.open,
      close: item.close,
      high: item.high,
      low: item.low,
      date: parseDate(item.date)
    }))

    return (
      <div>
        <div className="row">
          <div className="main-data col-12">
          </div>
        </div>
      </div>
    )
  }
}

const fetchData = gql`
  query CompanyData($id: Int, $days: Int){
    companyDays(id: $id, days: $days) {
      date
      open
      high
      low
      close
    }
  }
`

export default graphql(fetchData, {
  options: (props) => {
    return {
      variables: {
        id: parseInt(props.symbol),
        days: props.days,
      }
    }
  }
})(SimpleGraph)
