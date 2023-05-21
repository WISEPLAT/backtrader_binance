from binance.client import Client
from ConfigBinance.Config import Config
from decimal import Decimal

client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)

asset = 'BTC'

balance = client.get_asset_balance(asset=asset)

print(f" - Balance for {asset} is {balance['free']}")

info = client.get_symbol_info('ETHUSDT')
print(info)

info = client.get_symbol_info('BTCUSDT')
print(info)

info = client.get_symbol_info('BNBUSDT')
print(info)
print(info['filters'])

tickers = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', ]
info = {}
for ticker in tickers:
    info[ticker] = {}
    for _filter in client.get_symbol_info(ticker)['filters']:
        if _filter['filterType'] == 'PRICE_FILTER': info[ticker]["minPrice"] = Decimal(_filter['minPrice'])
        if _filter['filterType'] == 'LOT_SIZE': info[ticker]["minQty"] = Decimal(_filter['minQty'])
        if _filter['filterType'] == 'LOT_SIZE': info[ticker]["stepSize"] = Decimal(_filter['stepSize'])
        if _filter['filterType'] == 'LOT_SIZE': info[ticker]["step_num"] = _filter['stepSize'].find('1') - 2
        if _filter['filterType'] == 'PRICE_FILTER': info[ticker]["f_nums"] = _filter['minPrice'].find('1') - 1
print(info)

