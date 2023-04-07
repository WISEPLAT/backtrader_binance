import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации


# Торговая система
class RSIStrategy(bt.Strategy):
    """
    Демонстрация live стратегии с индикаторами SMA, RSI
    """
    params = (  # Параметры торговой системы
        ('coin_target', ''),
    )

    def __init__(self):
        """Инициализация, добавление индикаторов для каждого тикера"""
        self.orders = {}  # Организовываем заявки в виде справочника, конкретно для этой стратегии один тикер - одна активная заявка
        for d in self.datas:  # Пробегаемся по всем тикерам
            self.orders[d._name] = None  # Заявки по тикеру пока нет

        # создаем индикаторы для каждого тикера
        self.sma1 = {}
        self.sma2 = {}
        self.rsi = {}
        for i in range(len(self.datas)):
            ticker = list(self.dnames.keys())[i]    # key name is ticker name
            self.sma1[ticker] = bt.indicators.SMA(self.datas[i], period=8)  # SMA indicator
            self.sma2[ticker] = bt.indicators.SMA(self.datas[i], period=16)  # SMA indicator
            self.rsi[ticker] = bt.indicators.RSI(self.datas[i], period=14)  # RSI indicator

    def next(self):
        """Приход нового бара тикера"""
        for data in self.datas:  # Пробегаемся по всем запрошенным барам всех тикеров
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.broker._store.get_interval(data._timeframe, data._compression)

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # таймфрейм тикера
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
                symbol_balance, short_symbol_name = self.broker._store.get_symbol_balance(ticker)
                print(f"\t - {ticker} current balance = {symbol_balance} {short_symbol_name}")

                order = self.orders[data._name]  # Заявка тикера
                if order and order.status == bt.Order.Submitted:  # Если заявка не на бирже (отправлена брокеру)
                    return  # то ждем постановки заявки на бирже, выходим, дальше не продолжаем
                if not self.getposition(data):  # Если позиции нет
                    if order and order.status == bt.Order.Accepted:  # Если заявка на бирже (принята брокером)
                        print(f"\t - Снимаем заявку {order.binance_order['orderId']} на покупку {data._name}")
                        self.cancel(order)  # то снимаем ее

                    if self.rsi[ticker] < 60:  # Enter long
                        size = 0.0007  # min value to buy for BTC and ETH
                        if data._name == "XMRETH": size = 0.1
                        if data._name == "BNBETH": size = 0.1
                        price = self.broker._store.format_price(ticker, data.low[0] * 0.95)  # На 5% ниже min цены
                        print(f" - buy {ticker} size = {size} at price = {price}")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                        print(f"\t - Выставлена заявка {self.orders[data._name].binance_order['orderId']} на покупку {data._name}")

                else:  # Если позиция есть
                    if self.rsi[ticker] > 75:
                        print("sell")
                        print(f"\t - Продаем по рынку {data._name}...")
                        self.orders[data._name] = self.close()  # Заявка на закрытие позиции по рыночной цене

    def notify_order(self, order):
        """Изменение статуса заявки"""
        order_data_name = order.data._name  # Имя тикера из заявки
        self.log(f'Заявка номер {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Покупка" if order.isbuy() else "Продажа"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # Если заявка полностью исполнена
            if order.isbuy():  # Заявка на покупку
                self.log(f'Покупка {order_data_name} @{order.executed.price:.2f}, Цена {order.executed.value:.2f}, Комиссия {order.executed.comm:.2f}')
            else:  # Заявка на продажу
                self.log(f'Продажа {order_data_name} @{order.executed.price:.2f}, Цена {order.executed.value:.2f}, Комиссия {order.executed.comm:.2f}')
            self.orders[order_data_name] = None  # Сбрасываем заявку на вход в позицию

    def notify_trade(self, trade):
        """Изменение статуса позиции"""
        if trade.isclosed:  # Если позиция закрыта
            self.log(f'Прибыль по закрытой позиции {trade.getdataname()} Общая={trade.pnl:.2f}, Без комиссии={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # Заданная дата или дата текущего бара
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Выводим дату и время с заданным текстом на консоль


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'ETH'  # базовый тикер, в котором будут осуществляться расчеты
    symbol = 'BNB' + coin_target  # тикер, по которому будем получать данные в формате <КодТикераБазовыйТикер>
    symbol2 = 'XMR' + coin_target  # тикер, по которому будем получать данные в формате <КодТикераБазовыйТикер>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Хранилище Binance

    # live подключение к Binance - для Offline закомментировать эти две строки
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # Исторические 1-минутные бары за прошлый час + новые live бары / таймфрейм M1
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)
    data2 = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol2, start_date=from_date, LiveBars=True)

    cerebro.adddata(data)  # Добавляем данные
    cerebro.adddata(data2)  # Добавляем данные

    cerebro.addstrategy(RSIStrategy, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
