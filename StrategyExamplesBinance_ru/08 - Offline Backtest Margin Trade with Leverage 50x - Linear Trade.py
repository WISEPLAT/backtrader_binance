import datetime as dt
import backtrader as bt
import backtrader.analyzers as btanalyzers
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file

# https://www.backtrader.com/blog/posts/2019-08-29-fractional-sizes/fractional-sizes/
class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        """ Returns fractional size for cash operation for cryptocurrencies """
        return self.p.leverage * (cash / price)


class UnderOver(bt.Indicator):
    lines = ('underover',)
    params = dict(data2=20)
    plotinfo = dict(plot=True)

    def __init__(self):
        self.l.underover = self.data < self.p.data2             # data under data2 == 1


# Trading System
class SimpleSMAStrategy(bt.Strategy):
    """ Backtest strategy demonstration with SMA indicators """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
        ('leverage', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

        # creating indicators for each ticker
        self.sma1 = {}
        self.sma2 = {}
        self.sma3 = {}
        self.crossover = {}
        self.underover_sma = {}

        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]    # key name is ticker name
            self.sma1[ticker] = bt.indicators.SMA(self.datas[i], period=9)  # SMA1 indicator
            self.sma2[ticker] = bt.indicators.SMA(self.datas[i], period=30)  # SMA2 indicator
            self.sma3[ticker] = bt.indicators.SMA(self.datas[i], period=60)  # SMA3 indicator

            # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
            self.crossover[ticker] = bt.ind.CrossOver(self.sma1[ticker], self.sma2[ticker])  # crossover SMA1 and SMA2

            # signal 2 - when SMA3 is below SMA2
            self.underover_sma[ticker] = UnderOver(self.sma3[ticker].lines.sma, data2=self.sma2[ticker].lines.sma)


    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(bt.num2date(data.datetime[0]), ticker, _interval, data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0], _state, ))

                # signals to open position
                signal1 = self.crossover[ticker].lines.crossover[0]  # signal 1 - intersection of a fast SMA from bottom to top of a slow SMA
                signal2 = self.underover_sma[ticker]  # signal 2 - when SMA3 is below SMA2

                if not self.getposition(data):  # If there is no position
                    if signal1 == 1:
                        if signal2 == 1:
                            # buy
                            free_money = self.broker.getcash()
                            price = data.close[0]  # by closing price
                            size = (free_money * self.p.leverage / price) * 0.10  # 10% of available funds * leverage

                            print("-"*50)
                            print(f"\t - Let's buy {ticker}, size = {size} at price = {price}, depo: {self.broker.getcash()} {self.p.coin_target}")
                            self.orders[ticker] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                            print(f"\t - Order has been submitted to buy {ticker}, size={size}, price={price}")
                            print("-" * 50)

                else:  # If there is a position
                    if signal1 == 0 and signal2 == 0:
                        # sell
                        if self.orders[ticker]:
                            print("-" * 50)
                            print(f"\t - Let's sell by market {ticker}... size:{self.orders[ticker].size}")
                            self.orders[ticker] = self.close(data=data)  # Request to close a position at the market price
                            print(f"\t - Order has been submitted to sell by market {ticker}")
                            print("-" * 50)

    def notify_order(self, order):
        """Changing the status of the order"""
        ticker = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {ticker} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'\t*** BUY ORDER COMPLETED for {ticker} price: {order.executed.price:.2f}, size = {order.size}, cost: {order.executed.value:.2f}, comm: {order.executed.comm:.2f}, depo={self.cerebro.broker.getcash():.2f} {self.p.coin_target}')
            else:  # The order to sell
                self.log(f'\t*** SELL ORDER COMPLETED for {ticker} price: {order.executed.price:.2f}, size = {order.size}, cost: {order.executed.value:.2f}, comm: {order.executed.comm:.2f}, depo={self.cerebro.broker.getcash():.2f} {self.p.coin_target}')
                self.orders[ticker] = None  # Reset the order to enter the position

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, commission={abs(trade.pnl-trade.pnlcomm):.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if dt is None else dt  # date or date of the current bar
        print(f'{dt.strftime("%Y-%m-%d %H:%M:%S")} {txt}')  # Print the date and time with the specified text to the console


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    money = 2000  # money
    leverage = 50.0  # margin leverage x50

    cerebro.broker.setcash(money)  # Setting how much money
    cerebro.broker.addcommissioninfo(CommInfoFractional())  # set float size
    cerebro.broker.setcommission(commission=0.0015,  # Set the commission - 0.15% ... divide by 100 to remove %
                                 leverage=leverage, )  # Set leverage

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'BTC' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>
    symbol2 = 'ETH' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Binance Storage

    # # live connection to Binance - for Offline comment these two lines
    # broker = store.getbroker()
    # cerebro.setbroker(broker)

    # -----------------------------------------------------------
    # Attention! - Now it's Offline for testing strategies      #
    # -----------------------------------------------------------

    # # Historical 1-minute bars for 10 hours + new live bars / timeframe M1
    # timeframe = "M1"
    # from_date = dt.datetime.now() - dt.timedelta(minutes=60*10)
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars
    # # data2 = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol2, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars

    # Historical D1 bars for 365 days + new live bars / timeframe D1
    timeframe = "D1"
    from_date = dt.datetime.now() - dt.timedelta(days=365*3)
    data = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars
    data2 = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol2, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars

    cerebro.adddata(data)  # Adding data
    cerebro.adddata(data2)  # Adding data

    cerebro.addstrategy(SimpleSMAStrategy, coin_target=coin_target, timeframe=timeframe, leverage=leverage)  # Adding a trading system

    # Add Finance metrics of quality our strategy on historical data (backtest and results)
    cerebro.addanalyzer(btanalyzers.SQN, _name='SQN')
    cerebro.addanalyzer(btanalyzers.VWR, _name='VWR', fund=True)
    cerebro.addanalyzer(btanalyzers.TimeDrawDown, _name='TDD', fund=True, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='DD', fund=True)
    cerebro.addanalyzer(btanalyzers.Returns, _name='R', fund=True, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='AR', )
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='SR')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAnalyzer')

    result = cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart

    print()
    print("$"*77)
    # Print the final cash amount
    print('Was money: %.2f' % money)
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())  # Liquidation value of the portfolio
    print('Remaining available funds: %.2f' % cerebro.broker.getcash())
    print('Assets in the amount of: %.2f' % (cerebro.broker.getvalue() - cerebro.broker.getcash()))
    print()
    p = (cerebro.broker.getvalue() / money - 1) * 100
    print(f"{money:.2f} ==> {cerebro.broker.getvalue():.2f} ==> +{p:.2f}%")
    print()
    print('SQN: ', result[0].analyzers.SQN.get_analysis())
    print('VWR: ', result[0].analyzers.VWR.get_analysis())
    print('TDD: ', result[0].analyzers.TDD.get_analysis())
    print('DD: ', result[0].analyzers.DD.get_analysis())
    print('AR: ', result[0].analyzers.AR.get_analysis())
    print('Profitability: ', result[0].analyzers.R.get_analysis())
    print("$" * 77)
