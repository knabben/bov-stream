import pandas as pd
from fbprophet import Prophet

import pandas_datareader as web
from datetime import datetime, timedelta

days = 30

start = datetime(2010, 1, 1)
end = datetime.now() - timedelta(days=days)

stock = web.DataReader('BVMF:MGLU3', 'google', start, end)['Close']

df = pd.DataFrame({'ds': stock.index, 'y': stock.values})
m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=days)
forecast = m.predict(future)
data = forecast[['ds', 'yhat']].tail(days)

data.index = data['ds']
del data['ds']

nstart = end
nend = datetime.now()

stock = web.DataReader('BVMF:MGLU3', 'google', nstart, nend)['Close']

data1 = pd.concat([data, stock], axis=1).dropna()
data1.columns = ['Pred', 'Price']

data1['Ret_Pred'] = (data1['Pred'] / data1['Pred'].shift(1)) - 1
data1['Ret_Price'] = (data1['Price'] / data1['Price'].shift(1)) - 1

data1[['Pred', 'Price']].plot();
data1[['Ret_Pred', 'Ret_Price']].plot();
