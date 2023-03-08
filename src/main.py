import plotly.express as px

from dataclasses import asdict
from datetime import datetime
from tabulate import tabulate
from data.config import GeneralConfig, load_config
from data.provider import DataProvider
from data.store import DataStore
from testing.vector_backtesting import SmaCrossVectorStrategy, VectorBacktestConfig, VectorBacktester


def plot(data):
    fig = px.line(data, x=data.index, y=['creturns', 'c_strat_returns'], title='SMA Cross')
    fig.show()


def run_strategy():
    config = GeneralConfig('E:/store/')
    data = DataStore(config).load('BTCUSDT', '4h')

    strat = SmaCrossVectorStrategy(50, 200)
    data = strat.run(data)
    plot(data)


def run_backtest():
    config = load_config('config', 'BINANCE')
    
    test_config = VectorBacktestConfig(
        storedir=config.storedir,
        symbols=config.symbols,
        timeframes=config.timeframes
    )

    strategies = [
        SmaCrossVectorStrategy(10, 40),
        SmaCrossVectorStrategy(20, 80),
        SmaCrossVectorStrategy(30, 120),
        SmaCrossVectorStrategy(40, 160),
        SmaCrossVectorStrategy(50, 200)]

    tester = VectorBacktester(test_config, strategies)
    reports = tester.run()
    report_dicts = [asdict(report) for report in reports]
    print(tabulate(report_dicts, headers='keys'))


def init_load(load_only=False):
    config = load_config('config', 'BINANCE')
    from_date = datetime(2020, 1, 1)
    DataProvider(config).get_all(from_date, load_only)


def resample():
    config = load_config('config', 'GENERAL')
    DataStore().resample(config.storedir, 'ETHUSDT', '5min')


if __name__ == '__main__':
    # init_load(load_only=False)
    # resample()
    # run_strategy()
    run_backtest()    
    