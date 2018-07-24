import React from 'react'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import Select from 'react-select'
import SimpleGraph from './SimpleGraph'
import 'react-tabs/style/react-tabs.css';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs'


class Main extends React.Component {
  constructor(props) {
    super(props)
    this.onChange = this.onChange.bind(this)
    this.state = {
      symbol: "10",
      days: 30,
    }
  }

 renderDaysOptions() {
    return [
      {value: 30, label: `30 days`, name: 'days'},
      {value: 90, label: `90 days`, name: 'days'},
      {value: 120, label: `120 days`, name: 'days'},
      {value: 365, label: `365 days`, name: 'days'}
    ]
  }

 renderSelectOptions() {
    return this.props.data.companies.map((item) => ({
      name: 'symbol', value: item.id, label: `${item.symbol} - ${item.name}`
    }))
  }

  onChange(event) {
    const name = event.name
    const value = event.value

    this.setState({
      [name]: value
    })
  }

  render() {
    if (this.props.data.loading) {
      return (<div>Loading...</div>)
    }

    return (
      <div className="row">
        <div className="col-6 top-header">
          <label>
            Symbol
          </label>
          <Select
            name="symbol"
            options={this.renderSelectOptions()}
            onChange={this.onChange}
            value={this.state.symbol}
            clearable={false}
            placeholder='Pick a stock and select the time period'
          />
        </div>
        <div className="col-6 top-header">
          <label>
            Days
          </label>
          <Select
            name="days"
            options={this.renderDaysOptions()}
            onChange={this.onChange}
            value={this.state.days}
            clearable={false}
          />
        </div>

        <div className="col-12">
          <Tabs>
            <TabList>
              <Tab>Single security</Tab>
            </TabList>
            <TabPanel>
              <SimpleGraph {...this.state} />
            </TabPanel>
          </Tabs>
        </div>
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
