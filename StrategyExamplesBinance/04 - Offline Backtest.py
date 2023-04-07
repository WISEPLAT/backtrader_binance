import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Configuration file


# Trading System
class RSIStrategy(bt.Strategy):
    """
    Live strategy demonstration with SMA, RSI indicators
    """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
        ('timeframe', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

        # creating indicators for each ticker
        self.sma1 = {}
        self.sma2 = {}
        self.rsi = {}
        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]    # key name is ticker name
            self.sma1[ticker] = bt.indicators.SMA(self.datas[i], period=8)  # SMA indicator
            self.sma2[ticker] = bt.indicators.SMA(self.datas[i], period=16)  # SMA indicator
            self.rsi[ticker] = bt.indicators.RSI(self.datas[i], period=14)  # RSI indicator

    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.p.timeframe

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # ticker timeframe
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))
                print(f'\t - {ticker} RSI : {self.rsi[ticker][0]}')

                coin_target = self.p.coin_target
                print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                # Very slow function! Because we are going through API to get those values...
                # symbol_balance, short_symbol_name = self.broker._store.get_symbol_balance(ticker)
                # print(f"\t - {ticker} current balance = {symbol_balance} {short_symbol_name}")

                order = self.orders[data._name]  # The order of ticker
                if order and order.status == bt.Order.Submitted:  # If the order is not on the exchange (sent to the broker)
                    return  # then we are waiting for the order to be placed on the exchange, we leave, we do not continue further
                if not self.getposition(data):  # If there is no position
                    if order and order.status == bt.Order.Accepted:  # If the order is on the exchange (accepted by the broker)
                        print(f"\t - Cancel the order {order.p.tradeid} to buy {data._name}")
                        # self.cancel(order)  # then cancel it

                    if self.rsi[ticker] < 30:  # Enter long
                        size = 0.0005  # min value to buy for BTC and ETH
                        if data._name == "ETHUSDT": size = 0.05

                        price = data.close[0]  # by closing price

                        print(f" - buy {ticker} size = {size} at price = {price}")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                        print(f"\t - The order has been submitted {self.orders[data._name].p.tradeid} to buy {data._name}")

                else:  # If there is a position
                    if self.rsi[ticker] > 70:
                        print("sell")
                        print(f"\t - Sell it by the market {data._name}...")
                        self.orders[data._name] = self.close()  # Request to close a position at the market price

    def notify_order(self, order):
        """Changing the status of the order"""
        order_data_name = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:  # The order to sell
                self.log(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            self.orders[order_data_name] = None  # Reset the order to enter the position

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    cerebro.broker.setcash(200000)  # Setting how much money
    cerebro.broker.setcommission(commission=0.0015)  # Set the commission - 0.15% ... divide by 100 to remove %

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

    # Historical 1-minute bars for 10 hours + new live bars / timeframe M1
    timeframe = "M1"
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60*10)
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars
    data2 = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol2, start_date=from_date, LiveBars=False)  # set True here - if you need to get live bars

    cerebro.adddata(data)  # Adding data
    cerebro.adddata(data2)  # Adding data

    cerebro.addstrategy(RSIStrategy, coin_target=coin_target, timeframe=timeframe)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
