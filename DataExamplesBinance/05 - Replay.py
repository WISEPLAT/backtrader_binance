import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
from Strategy import StrategyJustPrintsOHLCVAndState  # Trading System

# Using a smaller time interval (Replay)
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

    # For the strategy, we use historical M1 bars, display the result on H1 + Chart because offline/ timeframe M5 + resample M1 + M5 + M5
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # we take data for the last 10 hours
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for the smallest time interval
    cerebro.adddata(data)  # Adding data
    cerebro.replaydata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="replayed")  # We see a large interval on the graph, we run the vehicle on a smaller one

    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
