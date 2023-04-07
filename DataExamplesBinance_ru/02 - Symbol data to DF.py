import datetime as dt
import backtrader as bt
import pandas as pd
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации


# Торговая система
class StrategySaveOHLCVToDF(bt.Strategy):
    """Сохраняет OHLCV в DF"""
    params = (  # Параметры торговой системы
        ('coin_target', ''),  #
    )

    def __init__(self):
        self.df = {}
        self.df_tf = {}

    def start(self):
        for data in self.datas:  # Пробегаемся по всем запрошенным тикерам
            ticker = data._name
            self.df[ticker] = []
            self.df_tf[ticker] = self.broker._store.get_interval(data._timeframe, data._compression)

    def next(self):
        """Приход нового бара тикера"""
        for data in self.datas:  # Пробегаемся по всем запрошенным тикерам
            ticker = data._name
            try:
                status = data._state  # 0 - Live data, 1 - History data, 2 - None
                _interval = data.interval
            except Exception as e:
                if data.resampling == 1:
                    status = 22
                    _interval = self.broker._store.get_interval(data._timeframe, data._compression)
                    _interval = f"_{_interval}"
                else:
                    print("Error:", e)

            if status == 1:
                _state = "Resampled Data"
                if status == 1: _state = "False - History data"
                if status == 0: _state = "True - Live data"

                self.df[ticker].append([bt.num2date(data.datetime[0]), data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0]])

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


# Исторические/новые бары тикера
if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # базовый тикер, в котором будут осуществляться расчеты
    symbol = 'BTC' + coin_target  # тикер, по которому будем получать данные в формате <КодТикераБазовыйТикер>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Хранилище Binance
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # 1. Исторические D1 бары за 365 дней + График т.к. оффлайн/ таймфрейм D1
    from_date = dt.datetime.utcnow() - dt.timedelta(days=365)  # берем данные за 365 дней от текущего времени
    data = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)

    cerebro.adddata(data)  # Добавляем данные
    cerebro.addstrategy(StrategySaveOHLCVToDF, coin_target=coin_target)  # Добавляем торговую систему

    results = cerebro.run()  # Запуск торговой системы

    print(results[0].df)

    df = pd.DataFrame(results[0].df[symbol], columns=["datetime", "open", "high", "low", "close", "volume"])
    print(df)

    tf = results[0].df_tf[symbol]

    # save to file
    df.to_csv(f"{symbol}_{tf}.csv", index=False)

    # save to file
    df[:-5].to_csv(f"{symbol}_{tf}_minus_5_days.csv", index=False)

    cerebro.plot()  # Рисуем график
