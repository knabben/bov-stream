import React from 'react'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'


class CandleStick extends React.Component {

  renderCandlestick(data) {
    let fc = window.fc;
    let d3 = window.d3;
    const candlestickSeries = fc.seriesSvgCandlestick().bandwidth(3)
    const movingAverageSeries = fc.seriesSvgLine()
                                  .mainValue(d => d.ma).crossValue(d => d.date)

    const mergedSeries = fc.seriesSvgMulti()
      .series([movingAverageSeries, candlestickSeries])

    const xScale = fc.scaleDiscontinuous(d3.scaleTime())
                    .discontinuityProvider(fc.discontinuitySkipWeekends());

    const chart = fc.chartSvgCartesian(xScale, d3.scaleLinear())
                    .yOrient('left')
                    .plotArea(mergedSeries);

    const xExtent = fc.extentDate()
                      .accessors([d => d.date]).padUnit('domain')
                      .pad([864e5, 864e5])

    const yExtent = fc.extentLinear()
                      .accessors([d => d.high, d => d.low]).pad([0.1, 0.1])

    const ma = fc.indicatorMovingAverage().value(d => d.open)

    const maData = ma(data)
    const mergedData = data.map( (d, i) =>
      Object.assign({}, d, {
        ma: maData[i]
      })
    )

    chart.xDomain(xExtent(mergedData))
      .yDomain(yExtent(mergedData))

    d3.select('#candlestick')
      .datum(mergedData)
      .call(chart);
  }

  componentDidMount() {
    this.renderCandlestick(this.props.data)
  }

  componentWillReceiveProps(nextProps) {
    this.renderCandlestick(nextProps.data)
  }

  render() {
    return (
      <div>
        <div id="candlestick" />
      </div>
    )
  }
}

export default CandleStick
