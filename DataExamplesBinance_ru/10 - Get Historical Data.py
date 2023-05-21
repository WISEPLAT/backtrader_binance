from binance.client import Client
from ConfigBinance.Config import Config
import pandas as pd

client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)

klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "2023-05-10")

df = pd.DataFrame(klines)
df.drop(df.columns[[6, 7, 8, 9, 10, 11]], axis=1, inplace=True)  # Удаление ненужных столбцов
df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
df['datetime'] = df['datetime'].values.astype(dtype='datetime64[ms]')
df['open'] = df['open'].values.astype(float)
df['high'] = df['high'].values.astype(float)
df['low'] = df['low'].values.astype(float)
df['close'] = df['close'].values.astype(float)
df['volume'] = df['volume'].values.astype(float)

# df = df[:-1]  # to skip last candle

print(df)
