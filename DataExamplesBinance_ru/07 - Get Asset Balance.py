from binance.client import Client
from ConfigBinance.Config import Config

client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)

asset = 'BTC'

balance = client.get_asset_balance(asset=asset)

print(f" - Balance for {asset} is {balance['free']}")