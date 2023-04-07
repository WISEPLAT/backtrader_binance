import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации
from Strategy import StrategyJustPrintsOHLCVAndState  # Торговая система

# Несколько временнЫх интервалов по одному тикеру: Получение из истории + live
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

    # 1. Исторические 5-минутные бары + 15-минутные за последние 10 часов + График т.к. оффлайн/ таймфрейм M5 + M15
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # берем данные за последние 5 часов
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по малому временнОму интервалу (должен идти первым)
    cerebro.adddata(data)  # Добавляем данные
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=15, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по большому временнОму интервалу

    # # 2. Исторические 1-минутные + 5-минутные бары за прошлый час + новые live бары / таймфрейм M1 + M5
    # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # берем данные за последний 1 час
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)  # Исторические данные по малому временнОму интервалу (должен идти первым)
    # cerebro.adddata(data)  # Добавляем данные
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=True)  # Исторические данные по большому временнОму интервалу

    # # 3. Исторические 1-часовые бары + 4-часовые за неделю + График т.к. оффлайн/ таймфрейм H1 + H4
    # from_date = dt.datetime.utcnow() - dt.timedelta(hours=24*7)  # берем данные за последнюю неделю от текущего времени
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по малому временнОму интервалу (должен идти первым)
    # cerebro.adddata(data)  # Добавляем данные
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=240, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по большому временнОму интервалу

    cerebro.adddata(data)  # Добавляем данные
    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
