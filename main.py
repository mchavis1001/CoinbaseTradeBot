import json, hmac, hashlib, time, requests, base64

import os
from dotenv import load_dotenv

import websocket
from requests.auth import AuthBase
import pandas as pd
from typing import DefaultDict, Deque, List, Dict, Tuple, Optional, Any
import datetime
# from datetime import timedelta, datetime

from finta import TA

load_dotenv()
api_key = os.getenv('api_key')
secret = os.getenv('secret')
passphrase = os.getenv('passphrase')


def get_auth_headers(timestamp, message, api_key, secret_key, passphrase):
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    return {
        "Accept": "application/json",
        'Content-Type': 'Application/JSON',
        "cb-access-key": api_key,
        "cb-access-passphrase": passphrase,
        "cb-access-sign": signature_b64,
        "cb-access-timestamp": timestamp
    }


class CBProAuth(AuthBase):
    def __init__(self):
        self.api_key = os.getenv('api_key')
        self.secret_key = os.getenv('secret')
        self.passphrase = os.getenv('passphrase')

    def __call__(self, request):
        timestamp = str(time.time())
        if request.method == 'POST':
            request.body = request.body.decode()
        message = ''.join([timestamp, request.method,
                           request.path_url, (request.body or '')])
        request.headers.update(get_auth_headers(timestamp, message,
                                                self.api_key,
                                                self.secret_key,
                                                self.passphrase))
        return request


class CoinbaseClient:
    def __init__(self):
        self.auth = CBProAuth()
        self.url = 'https://api.exchange.coinbase.com/'

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        r = requests.get(self.url + path, auth=self.auth, params=params).json()
        return r

    def post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        r = requests.post(self.url + path, auth=self.auth, json=params).json()
        return r

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        r = requests.delete(self.url + path, auth=self.auth, params=params).json()
        return r

    def accounts(self):
        info = self.get('accounts')
        data = pd.DataFrame(data=info)
        return data

    def limit_order(self, side, size, pair, price):
        payload = {
            "type": 'limit',
            "side": side,
            "product_id": pair,
            "size": str(size),
            "price": str(price)
        }

        return self.post('orders', payload)

    def market_order(self, side, size, pair):
        payload = {
            "type": 'market',
            "side": side,
            "product_id": pair,
            "size": str(size),
        }

        return self.post('orders', payload)

    def stop_loss(self, size, price, side, product):
        info = self.post('orders',
                         {'type': 'stop',
                          'size': size,
                          'stop': 'loss',
                          'stop_price': price,
                          'side': side,
                          'product': product})
        return info

    def multi_tp_order(self, entry_size, entry_price, product,
                       take_profit_1, take_profit_2, take_profit_3, take_profit_4, take_profit_5):
        self.market_order("buy", entry_size, product)  # Entry
        self.limit_order("sell", entry_size * 0.2, product, take_profit_1)
        self.limit_order("sell", entry_size * 0.2, product, take_profit_2)
        self.limit_order("sell", entry_size * 0.2, product, take_profit_3)
        self.limit_order("sell", entry_size * 0.2, product, take_profit_4)
        self.limit_order("sell", entry_size * 0.2, product, take_profit_5)

    def cancel_orders(self, product: None):
        info = self.delete('orders', product)
        return info

    def list_orders(self):
        info = self.get('orders')
        data = pd.DataFrame(data=info)
        return data

    def list_fills(self):
        info = self.get('fills')
        data = pd.DataFrame(data=info)
        return data

    def products(self):
        info = self.get('products')
        data = pd.DataFrame(data=info)
        return data

    def single_product(self, pair):
        info = self.get(f'products/{pair}')
        return info

    def orderbook(self, pair, level):
        info = self.get(f'products/{pair}/book', level)
        data = pd.DataFrame(data=info)
        return data

    def ticker(self, pair):
        info = self.get(f'products/{pair}/ticker')
        data = pd.DataFrame(data=info)
        return data

    def trades(self, pair):
        info = self.get(f'products/{pair}/trades')
        data = pd.DataFrame(data=info)
        return data

    def product_stats(self, pair):
        info = self.get(f'products/{pair}/stats')
        return info

    def historical_data(self, pair, timeframe):
        from datetime import timedelta, datetime
        today = datetime.today().strftime('%Y-%m-%d')
        d = (datetime.today() - timedelta(seconds=300*timeframe))
        info = self.get(f'products/{pair}/candles', {'start': d.strftime('%Y-%m-%d'),
                                                     'end': today,
                                                     'granularity': timeframe})
        info_2 = self.get(f'products/{pair}/candles', {'start': (d - timedelta(seconds=300*timeframe)).strftime('%Y-%m-%d'),
                                                       'end': d.strftime('%Y-%m-%d'),
                                                       'granularity': timeframe})
        info_3 = self.get(f'products/{pair}/candles', {'start': (d - timedelta(seconds=600*timeframe)).strftime('%Y-%m-%d'),
                                                       'end': (d - timedelta(seconds=300*timeframe)).strftime('%Y-%m-%d'),
                                                       'granularity': timeframe})
        info_4 = self.get(f'products/{pair}/candles', {'start': (d - timedelta(seconds=900*timeframe)).strftime('%Y-%m-%d'),
                                                       'end': (d - timedelta(seconds=600*timeframe)).strftime('%Y-%m-%d'),
                                                       'granularity': timeframe})
        info_5 = self.get(f'products/{pair}/candles', {'start': (d - timedelta(seconds=1200*timeframe)).strftime('%Y-%m-%d'),
                                                       'end': (d - timedelta(seconds=900*timeframe)).strftime('%Y-%m-%d'),
                                                       'granularity': timeframe})
        joined = info + info_2 + info_3 + info_4 + info_5
        data = pd.DataFrame(data=joined, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        return data.sort_values(by=['time'])

    def data(self, pair, timeframe):
        info = self.get(f'products/{pair}/candles', {'granularity': timeframe})
        data = pd.DataFrame(data=info, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        for index, row in data.iterrows():
            data.loc[index, 'time'] = datetime.datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S')
        return data.sort_values(by=['time'])

    def total_balance(self):
        balances = self.accounts()
        balances['balance'] = balances['balance'].astype(float)
        balances = balances[balances['balance'] > 0]
        currency = balances['currency'].tolist()

        total = 0
        for coin in currency:
            try:
                if coin != 'USD' and coin != 'XRP':
                    last = self.product_stats(f'{coin}-USD')['last']
                    bal = balances[balances['currency'] == coin]['balance'].values[-1] * float(last)
                else:
                    bal = balances[balances['currency'] == coin]['balance'].values[-1]

            except Exception:
                bal = balances[balances['currency'] == coin]['balance'].values[-1]

            total += bal

        return total

    def position(self, pair):
        balances = self.accounts()
        balances['balance'] = balances['balance'].astype(float)
        balance = balances[balances['currency'] == pair[:-4]]['balance'].values[-1]

        return float(balance)


class CoinbaseWebsocket:
    def __init__(self):
        self.auth = CBProAuth()
        self.ws_url = 'wss://ws-feed.exchange.coinbase.com'
        self.channel = ''
        self.pairs = ''
        self.msgs = ''
        self.pair = ''
        self.data = ''

    def on_open(self, ws):
        print('opened')
        channel_data = {
            "type": "subscribe",
            "channels": [{"name": self.channel,
                          "product_ids": self.pairs}]
        }

        ws.send(json.dumps(channel_data))

    def on_close(self, ws):
        print('closed')

    def on_message(self, ws, message):
        # print('received a message')
        msg = json.loads(message)
        # pprint.pprint(json_message)
        if self.channel == 'ticker':
            price = float(msg['price'])
            if price > 61055:
                print(price)

    def run(self, channel, pairs):
        self.channel = channel
        self.pairs = pairs

        ws = websocket.WebSocketApp(self.ws_url, on_open=self.on_open, on_close=self.on_close, on_message=self.on_message)
        ws.run_forever()

    def stop_loss_updater(self, pairs):
        self.channel = 'ticker'
        self.pairs = pairs

        def on_message(ws, message):
            client = CoinbaseClient()

            msg = json.loads(message)
            pair = msg['product_id']

            df = client.data(pair, 86400)
            df['ATR'] = TA.ATR(df, 14)
            df['FastMA'] = TA.SMA(df, 20)
            df['SlowMA'] = TA.SMA(df, 50)

            fast_ma = df['FastMA'].iloc[-1]
            slow_ma = df['SlowMA'].iloc[-1]
            atr = df['ATR'].iloc[-1]

            balance = client.total_balance()
            risk = 0.01
            position = client.position(pair)
            entry_size = (balance * risk) / atr

            if fast_ma > slow_ma and position < (entry_size * 0.1):
                print(f'Buy {pair}')
            elif fast_ma < slow_ma and position > 0:
                print(f'Sell {pair}')

            # print(msg)

        ws = websocket.WebSocketApp(self.ws_url, on_open=self.on_open, on_close=self.on_close, on_message=on_message)
        ws.run_forever()




