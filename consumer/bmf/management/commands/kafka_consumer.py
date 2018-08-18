import json
import pytz
import time
import zipline
import websocket
import pandas as pd

from zipline.api import order, record, symbol, set_benchmark

from io import StringIO
from multiprocessing import Process
from websocket import create_connection

from pandas import DataFrame, Panel
from kafka import KafkaConsumer

from django.conf import settings
from datetime import datetime, timedelta, timezone

from bmf.models import Company
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Kafka Consumer and zipline treatment'

    def send_websocket(self, perf, company):
        ws = create_connection("ws://127.0.0.1:4000/socket/websocket")
        ws.send(json.dumps({'topic': 'money:1', 'event': 'phx_join', 'ref': 1, 'payload': {}}))
        payload = json.loads(perf.tail(1)[['pnl', 'portfolio_value', 'returns']].T.to_json())

        transaction = perf[perf['transactions'].map(lambda x: x != [])].index
        if not transaction.empty:
            payload['transaction'] = str(transaction.values[0])
        data = json.dumps({'topic': 'money:1', 'event': 'money', 'ref': 1, 'payload': {company: payload}})
        print(data)
        ws.send(data)
        ws.close()

    def parse_kafka(self, company):
        print("Listening {0}".format(company))
        consumer = KafkaConsumer(company, bootstrap_servers=settings.BOOTSTRAP_SERVER)
        df = DataFrame()
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=30)
        columns = ['open', 'high', 'low', 'close','volume']
        print("Starting consuming...")

        for msg in consumer:
            df = df.append(pd.read_csv(
                StringIO(msg.value.decode('utf-8')),
                header=None, index_col=0, names=columns)
            )

            df.index = pd.to_datetime(df.index, utc=True)
            df.drop_duplicates(inplace=True)
            panel = Panel({company: df})
            panel.minor_axis = columns

            def initialize(context):
                context.has_ordered = False
                context.asset = symbol(company)

            def handle_data(context, data):
                if not context.has_ordered:
                    order(symbol(company), 1000)
                context.has_ordered = True

            try:
                perf = zipline.run_algorithm(
                    start=min(df.index),
                    end=max(df.index),
                    initialize=initialize,
                    capital_base=100000,
                    handle_data=handle_data,
                    data=panel
                )
                self.send_websocket(perf, company)
            except Exception as e:
                print(e)
                df = DataFrame()

    def handle(self, *args, **options):
        for company in Company.objects.filter(ibovespa=True)[:10]:
            Process(target=self.parse_kafka, args=(company.symbol,)).start()
