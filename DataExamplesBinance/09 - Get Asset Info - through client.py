import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config
from decimal import Decimal

cerebro = bt.Cerebro(quicknotify=True)

cerebro.broker.setcash(100000)  # Setting how much money
cerebro.broker.setcommission(commission=0.0015)  # Set the commission - 0.15% ... divide by 100 to remove %

coin_target = 'USDT'  # the base ticker in which calculations will be performed
symbols = ('BTC', 'ETH', 'BNB')  # tickers for which we will receive data

store = BinanceStore(
    api_key=Config.BINANCE_API_KEY,
    api_secret=Config.BINANCE_API_SECRET,
    coin_target=coin_target,
    testnet=False)  # Binance Storage

client = store.binance  # !!!

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

