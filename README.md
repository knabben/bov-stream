## GraphQL API

### Run

Run the phoenix server with:

```
make run-api  # phoenix server
make run-web  # react front-end
```

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

## Live streaming

### Build

Ensure dep is installed and run

```
$ make build
```

### Fundamental

First run xt command to fill up the Companies database (fill_db), after run:

```
$ bov fundamental
```

### Price Stream

For technical analysis with real-time 1 minute resolution streamer via GRPC, run:

```
$ bov stream --tickers "IBOV,MGLU3,PETR4"
```
