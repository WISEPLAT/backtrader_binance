import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации
from Strategy import StrategyJustPrintsOHLCVAndState  # Торговая система

# Использование меньшего временнОго интервала (Replay)
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

    # Для стратегии используем исторические M1 бары, отображаем результат на H1 + График т.к. оффлайн/ таймфрейм M5 + resample M1 + M5 + M5
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=10*60)  # берем данные за последние 5 часов
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по самому меньшему временному интервалу
    cerebro.adddata(data)  # Добавляем данные
    cerebro.replaydata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="replayed")  # На графике видим большой интервал, прогоняем ТС на меньшем

    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
