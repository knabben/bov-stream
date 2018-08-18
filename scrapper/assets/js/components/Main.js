import React from 'react'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'


const subscription = gql`
  subscription {
    money {
      id,
      pnl,
      portfolio_value,
      returns,
      timestamp
    }
  }
`

class Main extends React.Component {

  constructor(props) {
    super(props)
    this.higher_value = 100000
    this.higher_company = ""
    this.return_data = {}
  }

  componentWillMount() {
    this.subscribeMoney = this.props.data.subscribeToMore({
      document: subscription,
      updateQuery: (prev, { subscriptionData }) => {
        if (!subscriptionData.data) { return prev }
        const data = subscriptionData.data

        if (data.money['portfolio_value'] > this.higher_value) {
          this.higher_value = data.money['portfolio_value']
          this.higher_company = data.money['id']
        }

        this.return_data[data.money['id']] =  data.money
        return data
      }
    })
  }

  render() {

    const data = _.map(this.return_data, function(value, key) {
      const ts = new Date(parseInt(value.timestamp)).toLocaleDateString()
      const value_label = value.portfolio_value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
      return (
        <tr key={key}>
          <td><b>{key}</b></td>
          <td>{ts}</td>
          <td>{value.pnl}</td>
          <td>{value.returns}</td>
          <td className="value">
            { value.portfolio_value <= 100000 && 
              <span style={{color: "red"}}>
                <b>{value_label}</b>
              </span>
            }
            { value.portfolio_value > 100000 && 
            <span style={{color: "green"}}>
              <b>{value_label}</b>
            </span>
            }
          </td>
        </tr>
      )
    })

    return (
      <div>
      <div style={{textAlign: "right"}}>
      <b>HIGHER SCORE:</b> {this.higher_company} {this.higher_value}
      </div>
      <table width="80%" className="table table-striped">
        <thead>
          <tr>
            <th width="20%">Symbol</th>
            <th width="20%">Date</th>
            <th width="20%">PNL</th>
            <th width="20%">Return</th>
            <th width="20%">Portfolio</th>
          </tr>
        </thead>
        <tbody>
          {data}
        </tbody>
      </table>
      </div>
    )
  }
}

const query = gql`
  {
    money {
      id,
    }
  }
`

export default graphql(query)(Main)
