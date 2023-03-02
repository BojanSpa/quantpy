from pandas import DataFrame


class Signal:
    def provide(self, data: DataFrame):
        pass


class SmaCrossSignal(Signal):
    def __init__(self, short_sma, long_sma):
        self.short_sma
        self.long_sma

    def provide(self, data: DataFrame):
        pass


class Strategy:
    def __init__(self, signal: Signal):
        pass

    def execute(self, data: DataFrame):
        return self.signal.provide(data)





class Backtester:
    def __init__(self, data: DataFrame):
        self.data = data


    def execute(self, strategy: Strategy) -> DataFrame:
        return strategy.execute(self.data.copy())
