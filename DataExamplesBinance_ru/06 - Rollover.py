import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации
from Strategy import StrategyJustPrintsOHLCVAndState  # Торговая система

# Склейка истории тикера из файла и Binance (Rollover)
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

    tf = "1d"

    d1 = bt.feeds.GenericCSVData(  # Получаем историю из файла - в котором нет последних 5 дней
        dataname=f'{symbol}_{tf}_minus_5_days.csv',  # Файл для импорта из Binance. Создается из примера 01 - Symbol data to DF.py
        separator=',',  # Колонки разделены запятой
        dtformat='%Y-%m-%d',  # dtformat='%Y-%m-%d %H:%M:%S',  # Формат даты/времени YYYY-MM-DD HH:MM:SS
        openinterest=-1,  # Открытого интереса в файле нет
        sessionend=dt.time(0, 0),  # Для дневных данных и выше подставляется время окончания сессии. Чтобы совпадало с историей, нужно поставить закрытие на 00:00
    )

    from_date = dt.datetime.utcnow() - dt.timedelta(days=10)  # берем данные за последние 10 дней
    d2 = store.getdata(timeframe=bt.TimeFrame.Days, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по самому меньшему временному интервалу

    cerebro.rolloverdata(d1, d2, name=symbol)  # Склеенный тикер

    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
