from main import CoinbaseWebsocket, CoinbaseClient
import pandas as pd


pd.set_option('display.max_columns', 2000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 2000)

client = CoinbaseClient()
pos = client.position('BTC-USD')
print(pos)

