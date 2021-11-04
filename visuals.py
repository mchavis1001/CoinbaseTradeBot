from backtest import algo
import plotly.graph_objects as go

data = algo()

ohlc = data[['time', 'open', 'high', 'low', 'close']].copy()

fig = go.Figure(data=[go.Candlestick(x=data['time'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'])])

# fig.add_trace(go.Scatter(x=data['time'], y=data['ATR_UPPER']))
# fig.add_trace(go.Scatter(x=data['time'], y=data['ATR_LOWER']))
fig.add_trace(go.Scatter(x=data['time'], y=data['FastMA']))


fig.show()
