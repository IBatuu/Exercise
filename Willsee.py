import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
import xlsxwriter
from config import IEX_Cloud_Api_Token
from config import IEX_SANDBOX_API_TOKEN
from config import Alpha_Vantage_Api_key
import json
from alpha_vantage.timeseries import TimeSeries
import time
from multiprocessing import Process
from threading import Thread
import itertools






df_columns = [
    'Ticker',
    'Daily Closes',
    'Daily Closes PCT CH',
    'Daily Volumes',
    'Daily Volumes PCT CH',
    'Hourly Closes',
    'Hourly Closes PCT CH',
    'Hourly Volumes',
    'Hourly Volumes PCT CH',
    'Buy Signal Daily',
    'Sell Signal Daily'

]


df = pd.DataFrame(columns=df_columns)
pd.set_option("display.max_rows", None, "display.max_columns", None)




stocks = pd.read_csv('sp_500_stocks.csv')

symbol = 'AAPL'

api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={Alpha_Vantage_Api_key}'
data_daily = requests.get(api_url).json()
#print(data_daily)

apii_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&outputsize=compact&apikey={Alpha_Vantage_Api_key}'
data_hourly = requests.get(apii_url).json()
#print(data_hourly)

"""apiii_url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=USD&apikey={Alpha_Vantage_Api_key}'
data_BTC = requests.get(apiii_url).json()
print(data_BTC)"""

def get_closes_daily():
    for data in data_daily['Time Series (Daily)']:
        c_data = data_daily['Time Series (Daily)'][data]['4. close']
        close_data.append(c_data)


close_data = []
get_closes_daily()

def get_volumes_daily():
    for data in data_daily['Time Series (Daily)']:
        v_data = data_daily['Time Series (Daily)'][data]['5. volume']
        volume_data.append(v_data)


volume_data = []
get_volumes_daily()

def get_closes_hourly():
    for data1H in data_hourly['Time Series (60min)']:
        c_data1h = data_hourly['Time Series (60min)'][data1H]['4. close']
        close_data1h.append(c_data1h)


close_data1h = []
get_closes_hourly()

def get_volumes_hourly():
    for data1H in data_hourly['Time Series (60min)']:
        v_data1h = data_hourly['Time Series (60min)'][data1H]['5. volume']
        volume_data1h.append(v_data1h)


volume_data1h = []
get_volumes_hourly()


#print(volume_data)







for (close1D, volume1D, close1h, volume1h) in zip(close_data, volume_data, close_data1h, volume_data1h):
    df = df.append(
        pd.Series(
            [
                symbol,
                close1D,
                'NA',
                volume1D,
                'NA',
                close1h,
                'NA',
                volume1h,
                'NA',
                'NA',
                'NA'
            ],
        index=df_columns),
        ignore_index=True
    )

df[['Daily Closes']] = df[['Daily Closes']].apply(pd.to_numeric)
df[['Daily Volumes']] = df[['Daily Volumes']].apply(pd.to_numeric)
df[['Hourly Closes']] = df[['Hourly Closes']].apply(pd.to_numeric)
df[['Hourly Volumes']] = df[['Hourly Volumes']].apply(pd.to_numeric)


#pd.to_numeric(df['Daily Closes'])
df_close = df[['Daily Closes']]
df_close = df_close.pct_change()*100
df.iloc[:,2:3] = df_close


#(df)
df_volume = df[['Daily Volumes']]
df_volume = df_volume.pct_change()*100
df.iloc[:,4:5] = df_volume
#print(df)

df_close1h = df[['Hourly Closes']]
df_close1h = df_close1h.pct_change()*100
df.iloc[:,6:7] = df_close1h

df_volume1h = df[['Hourly Volumes']]
df_volume1h = df_volume1h.pct_change()*100
df.iloc[:,8:9] = df_volume1h


df['Buy Signal Daily'] = (df['Daily Volumes PCT CH'] > 30) & (df['Daily Closes PCT CH'] > 3)
df['Sell Signal Daily'] = (df['Daily Volumes PCT CH'] > 30) & (df['Daily Closes PCT CH'] < -3)

print(df)


writer = pd.ExcelWriter('Vantage.xlsx', engine='xlsxwriter')
df.to_excel(writer, 'Vantagee', index=False)
writer.save()

