import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
from Strategy import StrategyJustPrintsOHLCVAndState  # Trading System

# Multiple time intervals for one ticker: Getting a larger time interval from a smaller one (Resample)
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

    # # Historical 1-minute bars + 5-minute bars are obtained by Resample + M5 to control the last 1 hour + Chart because offline / timeframe M5 + resample M1 + M5 + M5
    # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # we take data for the last 10 hours
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for the smallest time interval
    # cerebro.adddata(data)  # Adding data
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name="resampled")  # You can add a larger time interval multiple of a smaller one (added automatically)
    # # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name="resampled").plotinfo.plot = False  # without output on the chart
    # # Adding data из Binance для проверки правильности работы Resample
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a large time interval

    # -------------------------------------------------------------------------------------------
    # Attention! - Data does not arrive synchronously on different TF, so there is a time shift #
    # - You can fix it, test it and push the changes!                                           #
    # -------------------------------------------------------------------------------------------

    # Historical M15, H1 are obtained by Resample + H1 for control + Chart because offline/ timeframe M15 + resample H1 + H1
    from_date = dt.datetime.utcnow().date().today()
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=15, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for the smallest time interval
    cerebro.adddata(data)  # Adding data
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="resampled",)  # You can add a larger time interval multiple of a smaller one (added automatically)
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="resampled", boundoff=1).plotinfo.plot = False  # without output on the chart
    # Adding data from Binance to verify the correct operation of Resample
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)  # Historical data for a large time interval

    cerebro.adddata(data)  # Adding data
    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
