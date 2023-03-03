from config import load_config
from loader import DataProvider
from store import DataStore
from datetime import datetime


date_format = '%Y-%m-%d'

def init_load(load_only=False):
    config = load_config('config', 'BINANCE')
    from_date = datetime(2020, 1, 1)
    DataProvider(config).get_all(from_date, load_only)


def resample():
    config = load_config('config', 'GENERAL')
    DataStore().resample(config.storedir, 'ETHUSDT', '5min')


if __name__ == '__main__':
    init_load(load_only=False)
    # resample()