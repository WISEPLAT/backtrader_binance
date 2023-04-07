import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from ConfigBinance.Config import Config  # Файл конфигурации
from Strategy import StrategyJustPrintsOHLCVAndState  # Торговая система

# Несколько временнЫх интервалов по одному тикеру: Получение большего временнОго интервала из меньшего (Resample)
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

    # # Исторические 1-минутные бары + 5-минутные получаем путем Resample + M5 для контроля за последний 1 час + График т.к. оффлайн/ таймфрейм M5 + resample M1 + M5 + M5
    # from_date = dt.datetime.utcnow() - dt.timedelta(minutes=60)  # берем данные за последние 5 часов
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по самому меньшему временному интервалу
    # cerebro.adddata(data)  # Добавляем данные
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name="resampled")  # Можно добавить больший временной интервал кратный меньшему (добавляется автоматом)
    # # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name="resampled").plotinfo.plot = False  # без вывода на графике
    # # Добавляем данные из Binance для проверки правильности работы Resample
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=5, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по большому временнОму интервалу

    # --------------------------------------------------------------------------------------
    # Внимание! - Данные приходят не синхронно по разным ТФ, поэтому есть сдвиг по времени #
    # - Вы можете это поправить, протестить и запушить изменения!                          #
    # --------------------------------------------------------------------------------------

    # Исторические M15, H1 получаем путем Resample + H1 для контроля + График т.к. оффлайн/ таймфрейм M15 + resample H1 + H1
    from_date = dt.datetime.utcnow().date().today()
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=15, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по самому меньшему временному интервалу
    cerebro.adddata(data)  # Добавляем данные
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="resampled",)  # Можно добавить больший временной интервал кратный меньшему (добавляется автоматом)
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60, name="resampled", boundoff=1).plotinfo.plot = False  # без вывода на графике
    # Добавляем данные из Binance для проверки правильности работы Resample
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=60, dataname=symbol, start_date=from_date, LiveBars=False)  # Исторические данные по большому временнОму интервалу

    cerebro.adddata(data)  # Добавляем данные
    cerebro.addstrategy(StrategyJustPrintsOHLCVAndState, coin_target=coin_target)  # Добавляем торговую систему

    cerebro.run()  # Запуск торговой системы
    cerebro.plot()  # Рисуем график
