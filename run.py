from live_bot import run
from main import CoinbaseWebsocket, CoinbaseClient
from threading import Thread

ws = CoinbaseWebsocket()
client = CoinbaseClient()
products = client.products()
usd_pairs = products[products['quote_currency'] == 'USD']['id'].values.tolist()

if __name__ == '__main__':
    # Thread(target=run).start()
    Thread(target=ws.stop_loss_updater(usd_pairs)).start()
