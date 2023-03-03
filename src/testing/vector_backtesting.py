import gc
import pandas as pd
import numpy as np
from dataclasses import dataclass
from data.store import DataStore


@dataclass
class VectorBacktestConfig:
    storedir: str
    symbols: list[str]
    timeframes: list[str]



@dataclass
class VectorStrategyReport:
    name: str
    returns: float
    strat_returns: float



class VectorStrategy:
    name: str


    def __init__(self, args):
        self.args = args


    def run(self, data):
        pass


    def __calc_returns(self, data):
        data['returns'] = np.log(data.close / data.close.shift(1))
        data['creturns'] = data.returns.cumsum().apply(np.exp)



class SmaVectorStrategy(VectorStrategy):
    def __init__(self, args):
        super().__init__(self, args)
        self.name = f'SMA_Cross_{args.fast}_{args.slow}'


    def run(self, data):
        ma_fast = self.args.fast
        ma_slow = self.args.slow

        super().__calc_returns(data)

        data['ma_fast'] = data.close.rolling(ma_fast).mean()
        data['ma_slow'] = data.close.rolling(ma_slow).mean()

        data['position'] = np.where(data.ma_fast > data.ma_slow, 1, -1)
        data.dropna(implace=True)

        data['strat_returns'] = data.position.shift(1) * data.returns
        data['c_strat_returns'] = data.strategy.cumsum().apply(np.exp)

        return VectorStrategyReport(
            self.name, 
            data.returns, 
            data.c_strat_returns)



class VectorBacktester:
    def __init__(self, config: VectorBacktestConfig, strategies: list[VectorStrategy]):
        self.config = config
        self.strategies = strategies

    
    def run(self, simple=True) -> list[VectorStrategyReport]:
        reports: list[VectorStrategyReport]

        for symbol in self.config.symbols:
            for tf in self.config.timeframes:
                data = DataStore(self.config).load(symbol, tf)
                if simple: 
                    data.drop(columns = ['open', 'high', 'low', 'volume'], inplace=True)

                for strategy in self.strategies:
                    self.__run_strategy(data, strategy)

                report = self.__run_strategy(data)
                reports.append(report)

                self.__release(data)

        return reports



    def __run_strategy(self, data, strategy) -> VectorStrategyReport:
        self.__calc_returns(data)
        report = strategy.run(data)
        return report


    def __release(self, data):
        del data
        gc.collect()