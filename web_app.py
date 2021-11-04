import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px

from backtest import algo
from main import CoinbaseWebsocket,  CoinbaseClient

client = CoinbaseClient()

pair = st.sidebar.text_input('Select Pair ex: BTC-USD', 'BTC-USD')
timeframe = st.sidebar.selectbox('Select Timeframe: (86400:1D, 21600:6H, 300:5m)', (86400, 21600, 300))

fast_ma_len = int(st.sidebar.number_input('Fast MA Length', 20))
slow_ma_len = int(st.sidebar.number_input('Slow MA Length', 50))

starting_balance = int(st.sidebar.number_input('Starting Balance', 1000))
risk_percentage = int(st.sidebar.number_input('Risk Percentage', 1))

data = algo(pair, timeframe, fast_ma_len, slow_ma_len, starting_balance, risk_percentage)

ohlc = data[['time', 'open', 'high', 'low', 'close']].copy()

fig = go.Figure(data=[go.Candlestick(
                x=data['time'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Candles')])

fig.add_trace(go.Scatter(x=data['time'], y=data['FastMA'], name='Fast Moving Average'))
fig.add_trace(go.Scatter(x=data['time'], y=data['SlowMA'], name='Slow Moving Average'))

fig.update_layout(width=1000, height=600)

st.header(f'{pair} Chart')
st.plotly_chart(fig)

balance_chart = go.Figure(data=go.Scatter(x=data['time'], y=data['Balance']))
balance_chart.update_layout(width=900, height=600)
st.header('Balance Chart')
st.plotly_chart(balance_chart)

buys = data[data['Entry/Exit'] > 0]
sells = data[data['Entry/Exit'] < 0]

st.markdown('Buys')
st.write(buys)

st.markdown('Sells')
st.write(sells)

if st.checkbox('Show Full DataFrame'):
    st.write(data)
