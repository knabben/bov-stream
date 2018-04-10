import time
import grpc
from concurrent import futures

import src_proto.data_pb2 as data
import src_proto.data_pb2_grpc as proto_grpc


class Pricer(proto_grpc.RoutePriceServicer):

    def TraversePrice(self, request, context):
        print(request)
        return data.PredictedPrice(price=100.0)


def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_grpc.add_RoutePriceServicer_to_server(Pricer(), server)
    server.add_insecure_port('localhost:10000')
    server.start()

    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve_grpc()
