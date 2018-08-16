import numpy as np
import pandas as pd
import pandas_datareader as web

from collections import namedtuple
from datetime import datetime, timedelta

from bovespa.models import Company


def get_company_data(days=7, id=''):
    symbol = Company.objects.get(pk=id).symbol
    end = datetime.now().date()
    start = end - timedelta(days=int(days))

    stock_data = web.DataReader('BVMF:{}'.format(symbol), 'google', start, end)

    stock_days = []
    for i, (key, data) in enumerate(stock_data.T.iteritems()):
        data.dropna(axis=0, inplace=True)
        try:
            Stock = namedtuple('Stock', ['date', 'open', 'high', 'low', 'close'])
            Stock.date = str(key.date())
            Stock.open = data['Open']
            Stock.high = data['High']
            Stock.low = data['Low']
            Stock.close = data['Close']
            stock_days.append(Stock)
        except KeyError:
            continue
    return stock_days


def get_return_company(id, current_price, current_date, purchase_price,
                       purchase_date, quantity):
    symbol = Company.objects.get(pk=id).symbol

    start = datetime.strptime(purchase_date, '%m/%d/%Y')
    end = datetime.strptime(current_date, '%m/%d/%Y')

    stock_data = web.DataReader('BVMF:{}'.format(symbol), 'google', start, end)
    stock_return = pd.DataFrame({'Close': stock_data['Close']})

    if float(purchase_price) > 0:
        stock_return.iloc[0] = float(purchase_price)
    else:
        purchase_price = stock_return.iloc[0]

    if float(current_price) > 0:
        stock_return.iloc[-1] = float(current_price)

    stock_return['Return'] = (stock_return['Close'] / stock_return['Close'].shift(1)) - 1
    stock_return['Cumulative'] = stock_return['Return'].cumsum()
    stock_return['Value'] = stock_return['Cumulative'] * float(purchase_price) * quantity

    stock_cum_ret = []
    for i, (key, data) in enumerate(stock_return.T.iteritems()):
        data.fillna(0, inplace=True)
        try:
            Stock = namedtuple('Stock', ['date', 'close', 'ret', 'cumRet', 'value'])
            Stock.date = str(key.date())
            Stock.close = data['Close']
            Stock.ret = round(data['Return'], 4)
            Stock.cum_ret = round(data['Cumulative'] * 100, 4)
            Stock.value = round(data['Value'], 2)
            stock_cum_ret.append(Stock)
        except KeyError:
            continue
    return stock_cum_ret
