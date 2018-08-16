import signal
import time
import grpc

import numpy as np
import pandas as pd
from fbprophet import Prophet

from datetime import datetime
from concurrent import futures

import src_proto.data_pb2 as data
import src_proto.data_pb2_grpc as proto_grpc

price_df = pd.DataFrame({'symbol': [], 'ds': [], 'y': []})
days = 10


class Pricer(proto_grpc.RoutePriceServicer):

    def TraversePrice(self, request, context):
        global price_df

        translated_time = datetime.strptime(request.datetime, '%Y-%m-%d %H:%M')
        price = request.close
        symbol = request.symbol

        price_data = {
            "ds": [translated_time],
            "y": [price],
            "symbol": [symbol]
        }

        if not np.all(price_df.isin(price_data).any()):
            price_df = price_df.append(
                pd.DataFrame(price_data), ignore_index=True)

        return data.PredictedPrice()


def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pricer = Pricer()
    proto_grpc.add_RoutePriceServicer_to_server(pricer, server)
    server.add_insecure_port('localhost:10000')
    server.start()

    def handler(signum, frame):
        for symbol, index in price_df.groupby('symbol').groups.items():
            print("TICKER {}".format(symbol))
            symbol_price = price_df[price_df['symbol'] == symbol].sort_values('symbol')

            m = Prophet()
            m.fit(symbol_price)

            future = m.make_future_dataframe(periods=days)
            forecast = m.predict(future)

            print(forecast[['ds', 'yhat']])

    signal.signal(signal.SIGTERM, handler)

    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve_grpc()
