import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации
from Strategy import StrategyJustPrintsOHLCVAndState  # Торговая система

# Несколько тикеров для нескольких торговых систем по одному временнОму интервалу history + live
if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # базовый тикер, в котором будут осуществляться расчеты
    symbols = ('BTC', 'ETH')  # тикеры, по которым будем получать данные

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Хранилище Binance
    broker = store.getbroker()
    cerebro.setbroker(broker)

    for _symbol in symbols:  # Пробегаемся по всем тикерам

        symbol = _symbol + coin_target  # тикер, по которому будем получать данные в формате <КодТикераБазовыйТикер>

        # # 1. Исторические 5-минутные бары за последние 10 часов + График т.к. оффлайн/ таймфрейм M5
        # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # берем данные за последние 5 часов
        # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)

        # # 2. Исторические 1-минутные бары за прошлый час + новые live бары / таймфрейм M1
        # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # берем данные за последний 1 час
        # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)

        # 3. Исторические 1-часовые бары за неделю + График т.к. оффлайн/ таймфрейм H1
        from_date = dt.datetime.utcnow() - dt.timedelta(hours=24*7)  # берем данные за последнюю неделю от текущего времени
        data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)

        cerebro.adddata(data)  # Добавляем данные

    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
