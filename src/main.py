from collections import OrderedDict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dataclasses import asdict
from datetime import datetime
from tabulate import tabulate
from data.config import GeneralConfig, load_config
from data.provider import DataProvider
from data.store import DataStore
from testing.vector_backtesting import SmaCrossVectorStrategy, DmiVectorStrategy, VectorBacktestConfig, VectorBacktester


def plot(data):
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig.add_trace(
        go.Scatter(x=data.index, y=data.close, name='Price', line=dict(color='darkblue'), mode='lines'), secondary_y=True)

    fig.add_trace(
        go.Bar(x=data.index, y=data.equity, name='Equity', marker_color='cadetblue', marker_line_width=0), secondary_y=False)

    fig.add_trace(
        go.Bar(x=data.index, y=data.drawdown, name='Drawdown', marker_color='palevioletred', marker_line_width=0), secondary_y=False)

    fig.update_yaxes(title_text="Equity/Drawdown", showgrid=False, secondary_y=False)
    fig.update_yaxes(title_text="Price", secondary_y=True)
    fig.update_layout(bargap=0, bargroupgap=0)

    fig.show()


def run_strategy():
    config = GeneralConfig('E:/store/')
    data = DataStore(config).load('BNBUSDT', '1h')

    # strat = DmiVectorStrategy(30)
    strat = SmaCrossVectorStrategy(30, 120)
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
        DmiVectorStrategy(10),
        DmiVectorStrategy(20),
        DmiVectorStrategy(30),
        DmiVectorStrategy(40),
        DmiVectorStrategy(50),
        SmaCrossVectorStrategy(10, 40),
        SmaCrossVectorStrategy(20, 80),
        SmaCrossVectorStrategy(30, 120),
        SmaCrossVectorStrategy(40, 160),
        SmaCrossVectorStrategy(50, 200)
    ]

    tester = VectorBacktester(test_config, strategies)
    strat_reports = tester.run_all()
    strat_reports = [asdict(report) for report in strat_reports]
    strat_reports = sorted(strat_reports, key=lambda item: item['equity'], reverse=True)

    print(tabulate(strat_reports, headers='keys'))


def init_load(load_only=False):
    config = load_config('config', 'BINANCE')
    from_date = datetime(2020, 1, 1)
    DataProvider(config).get_all(from_date, load_only)


def resample():
    config = load_config('config', 'GENERAL')
    DataStore().resample(config.storedir, 'ETHUSDT', '5min')


if __name__ == '__main__':
    run_backtest()
    # run_strategy()
    # init_load(load_only=False)
    # resample()
    