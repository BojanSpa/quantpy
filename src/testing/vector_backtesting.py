import gc
import numpy as np
import pandas as pd
import pandas_ta as pdta
from typing import List
from dataclasses import dataclass
from data.store import DataStore


@dataclass
class VectorBacktestConfig:
    storedir: str
    symbols: List[str]
    timeframes: List[str]


@dataclass
class VectorStrategyReport:
    name: str
    params: str
    symbol: str
    tf: str
    cum_returns: float
    cum_strat_returns: float
    equity: float


class VectorStrategy:
    name: str
    args: str

    def run(self, data):
        self.__clear(data)


    def calc_equity(self, data, init_equity):
        data['equity'] = data.cum_strat_return * init_equity

    def calc_drawdown(self, data):
        data['max_equity'] = data.equity.cummax()
        data['drawdown'] = (data.max_equity - data.equity) * (-1)

    def __clear(self, data):
        data.drop(columns=['position', 'strat_return', 'cum_strat_return', 'equity', 'max_equity', 'drawdown'], errors='ignore')


class SmaCrossVectorStrategy(VectorStrategy):
    name = 'SMA_Cross'
    fast: int
    slow: int

    def __init__(self, fast, slow):
        self.fast = fast
        self.slow = slow
        self.args = f"{self.fast}_{self.slow}"


    def run(self, data, init_equity=1000):
        super().run(data)

        data['ma_fast'] = data.close.rolling(self.fast).mean()
        data['ma_slow'] = data.close.rolling(self.slow).mean()

        data['position'] = np.where(data.ma_fast > data.ma_slow, 1, -1)
        data.dropna(inplace=True)

        data['strat_return'] = data.position.shift(1) * data.log_return
        data['cum_strat_return'] = data.strat_return.cumsum().apply(np.exp)

        super().calc_equity(data, init_equity)
        super().calc_drawdown(data)

        return data


class DmiVectorStrategy(VectorStrategy):
    name = 'DM'

    def __init__(self, length):
        self.length = length
        self.args = length
        pass


    def run(self, data: pd.DataFrame, init_equity=1000):
        super().run(data)

        data[['dm_p', 'dm_n']] = pdta.dm(data.high, data.low, self.length)
        data['position'] = np.where(data.dm_p > data.dm_n, 1, -1)
        data.dropna(inplace=True)

        data['strat_return'] = data.position.shift(1) * data.log_return
        data['cum_strat_return'] = data.strat_return.cumsum().apply(np.exp)

        super().calc_equity(data, init_equity)
        super().calc_drawdown(data)

        return data  


class VectorBacktester:
    def __init__(self, config: VectorBacktestConfig, strategies: List[VectorStrategy]):
        self.config = config
        self.strategies = strategies

    
    def run_all(self, simple=False):
        symbols = self.config.symbols
        timeframes = self.config.timeframes

        for symbol in symbols:
            for timeframe in timeframes:
                data = DataStore(self.config).load(symbol, timeframe, simple=simple)
                
                for strategy in self.strategies:
                    yield self.run(symbol, timeframe, strategy, data)

                self.__release(data)


    def run(self, symbol, timeframe, strategy, data):
        data = strategy.run(data)
        lrow = data.iloc[-1]

        return VectorStrategyReport(
            strategy.name,
            strategy.args,
            symbol,
            timeframe,
            lrow.cum_return, 
            lrow.cum_strat_return,
            lrow.equity)


    def __release(self, data):
        del data
        gc.collect()