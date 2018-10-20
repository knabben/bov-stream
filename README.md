## BMF streamer

Real-time BMF Stock Portfolio analysis

<img src="https://raw.githubusercontent.com/knabben/blog/master/static/images/bov-screen.png" width="700px">

### Install

Create a virtualenv inside consumer folder

```
cd consumer
consumer$ pipenv shell
consumer$ pipenv install
consumer$ make company-fixture
```

### Run

It is composed of a:

* Producer, responsible to fetch tickets price from Yahoo and send through a specific Kafka topic
* Consumer, fetch the message and backtest on Zipline, returns are streamed through websocket
* Web interface, for visualization of events in realtime

```
make run-producer &
make run-consumer
```

### Visualizing in realtime

It comes with a UI for realtime visualization and best performance companies ordering:

```
make run-web
```

## GraphQL API

### Ibovespa Companies

An example on how to fetch the Ibovespa companies:

```
{
  companies {
    id
    name
    symbol
  }
}
```

A response can be:

```
{
  "data": {
    "companies": [
      {
        "symbol": "BBDC3",
        "name": "BRADESCO",
        "id": "4"
      },
      {
        "symbol": "BBDC4",
        "name": "BRADESCO",
        "id": "5"
      },
      {
        "symbol": "ELET3",
        "name": "ELETROBRAS",
        "id": "23"
      },
      ...
   }
}
```

### Fetch daily quotes

If you want to fetch the daily quotes starting now until now - days, use:

```
// id - company id
// days - end offset

companyDays(id: $id, days: $days) {
  date,
  open,
  high,
  low,
  close
}
```

### Subscribe for events

Returns and PNLs comes through subscription

```
subscription {
  money {
    id,
    pnl,
    portfolioValue,
    returns,
    timestamp
  }
}
```
