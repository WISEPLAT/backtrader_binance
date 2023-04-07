import backtrader as bt


class StrategyJustPrintsOHLCVAndState(bt.Strategy):
    """
    - Отображает статус подключения
    - При приходе нового бара отображает его цены/объем
    - Отображает статус - исторические бары или live
    """
    params = (  # Параметры торговой системы
        ('coin_target', ''),  #
    )

    def next(self):
        """Приход нового бара тикера"""
        for data in self.datas:  # Пробегаемся по всем запрошенным тикерам
            ticker = data._name
            status = 1
            _interval = self.broker._store.get_interval(data._timeframe, data._compression)
            try:
                status = data._state  # 0 - Live data, 1 - History data, 2 - None
                _interval = data.interval
            except Exception as e:
                if data.resampling == 1:
                    status = 22
                    _interval = self.broker._store.get_interval(data._timeframe, data._compression)
                    _interval = f"_{_interval}"
                else:
                    # print("Error:", e)
                    pass

            if status in [0, 1, 22]:
                _state = "Resampled Data"
                if status == 1: _state = "False - History data"
                if status == 0: _state = "True - Live data"

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
