import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
from Strategy import StrategyJustPrintsOHLCVAndState  # Trading System

# Multiple time intervals for one ticker: Getting from history + live
if __name__ == '__main__':  # Entry point when running this script
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'BTC' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False,
        # tld="us",  # for US customers => to use the 'Binance.us' url
    )  # Binance Storage
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # 1. Historical 5-minute bars + 15-minute bars for the last 10 hours + Chart because offline/ timeframe M5 + M15
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # we take data for the last 10 hours
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a small time interval (should go first)
    cerebro.adddata(data)  # Adding data
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=15, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a large time interval

    # # 2. Historical 1-minute + 5-minute bars for the last hour + new live bars / timeframe M1 + M5
    # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # we take data for the last 1 hour
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)  # Historical data for a small time interval (should go first)
    # cerebro.adddata(data)  # Adding data
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=True)  # Historical data for a large time interval

    # # 3. Historical 1-hour bars + 4-hour bars for the week + Chart because offline/ timeframe H1 + H4
    # from_date = dt.datetime.utcnow() - dt.timedelta(hours=24*7)  # we take data for the last week from the current time
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a small time interval (should go first)
    # cerebro.adddata(data)  # Adding data
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=240, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a large time interval

    cerebro.adddata(data)  # Adding data
    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
