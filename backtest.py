from main import CoinbaseClient
from finta import TA
import pandas as pd
import datetime

pd.set_option('display.max_columns', 2000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 2000)

client = CoinbaseClient()
# 1D: 86400 6H: 21600, 5m: 300


def algo(pair, timeframe, fast_ma_length, slow_ma_length, starting_balance, risk_percent):
    data = client.historical_data(pair, timeframe)
    data['ATR'] = TA.ATR(data, 14)
    data['FastMA'] = TA.SMA(data, fast_ma_length)
    data['SlowMA'] = TA.SMA(data, slow_ma_length)

    buy = (data['FastMA'] > data['SlowMA'])
    sell = (data['FastMA'] < data['SlowMA'])

    data['Signal'] = 0.0
    data.loc[buy, 'Signal'] = 1
    data.loc[sell, 'Signal'] = -1
    data['Entry/Exit'] = data['Signal'].diff()

    pos = 0
    for index, row in data.iterrows():
        data.loc[index, 'time'] = datetime.datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S')

        data.loc[index, 'Buys/Sells'] = 0
        data.loc[index, 'Position'] = pos
        data.loc[index, 'Position ($)'] = pos * row['close']
        data.loc[index, 'Balance'] = data.loc[:index, 'Buys/Sells'].sum() + \
                                     data.loc[index, 'Position ($)'] + starting_balance

        if row['Entry/Exit'] == 2 or row['Entry/Exit'] == 1:
            pos += data.loc[index, 'Balance'] * (risk_percent/100) / row['ATR']
            data.loc[index, 'Buys/Sells'] = -pos * row['close']
        elif row['Entry/Exit'] == -2 and pos > 0:
            data.loc[index, 'Buys/Sells'] = pos * row['close']
            pos = 0
        else:
            data.loc[index, 'Buys/Sells'] = 0

    return data
