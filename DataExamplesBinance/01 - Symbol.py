import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
from Strategy import StrategyJustPrintsOHLCVAndState  # Trading System

# Historical/new bars of ticker
if __name__ == '__main__':  # Entry point when running this script
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'BTC' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Binance Storage
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # # 1. Historical 5-minute bars for the last 10 hours + Chart because offline/ timeframe M5
    # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # we take data for the last 10 hours
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)

    # 2. Historical 1-minute bars for the last hour + new live bars / timeframe M1
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # we take data for the last 1 hour
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)

    # # 3. Historical 1-hour bars for the week + Chart because offline / timeframe H1
    # from_date = dt.datetime.utcnow() - dt.timedelta(hours=24*7)  # we take data for the last week from the current time
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)

    cerebro.adddata(data)  # Adding data
    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
