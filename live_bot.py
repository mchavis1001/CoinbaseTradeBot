from main import CoinbaseWebsocket,  CoinbaseClient
from finta import TA
import pandas as pd
import time

client = CoinbaseClient()


def data(pair):
    df = client.data(pair, 86400)
    df['ATR'] = TA.ATR(df, 14)
    df['FastMA'] = TA.SMA(df, 20)
    df['SlowMA'] = TA.SMA(df, 50)

    return df


def ma_algo(pair):
    d = data(pair)
    fast_ma = d['FastMA'].iloc[-1]
    slow_ma = d['SlowMA'].iloc[-1]
    atr = d['ATR'].iloc[-1]
    time = d['time'].iloc[-1]

    balance = client.total_balance()
    risk = 0.01
    position = client.position(pair)

    entry_size = (balance * risk) / atr
    entry = d['close'].iloc[-1]
    stop_loss = entry - atr
    tp1 = entry + atr
    tp2 = entry + (atr * 2)
    tp3 = entry + (atr * 3)
    tp4 = entry + (atr * 5)
    tp5 = entry + (atr * 10)

    if fast_ma > slow_ma and position < entry_size * 0.1:
        print(f'Buy {entry_size} {pair} at {entry} {time}')
        # client.multi_tp_order(entry_size, entry, pair, tp1, tp2, tp3, tp4, tp5)

    elif fast_ma < slow_ma:
        print(f'Sell {entry_size} {pair} at {entry} {time}')
        # client.cancel_orders(pair)
        # client.market_order('sell', position, pair)


def atr_bands(pair):
    df = data(pair)


def run():
    products = client.products()
    usd_pairs = products[products['quote_currency'] == 'USD']['id'].values

    while True:
        for pair in usd_pairs:
            try:
                ma_algo(pair)
            except Exception as e:
                print(e, pair)

        # time.sleep(5)


run()
