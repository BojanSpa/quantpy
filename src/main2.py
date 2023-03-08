from data.config import load_config
from data.provider import DataBatchSize, DataProvider
from data.store import DataStore
from datetime import datetime


date_format = '%Y-%m-%d'

def init_load():
    config = load_config('config', 'BINANCE')
    from_date = datetime(2020, 1, 1)
    DataProvider(config).get_all(from_date, DataBatchSize.MONTHLY)


if __name__ == '__main__':
    init_load()