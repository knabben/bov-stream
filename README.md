Build
-----

Ensure dep is installed and run

```
$ make build
```

Fundamental
-----------

First run xt command to fill up the Companies database (fill_db), after run:

```
$ bov fundamental
```

Price Stream
------------

For technical analysis with real-time 1 minute resolution streamer via GRPC, run:

```
$ bov stream --tickers "IBOV,MGLU3,PETR4"
```
