import data.provider as dp

from datetime import datetime
from tabulate import tabulate
from utils import datetime_extensions
from data.config import load_config


if __name__ == '__main__':
    conf = load_config(section='BINANCE')
    provider = dp.BinanceDataProvider(conf, dp.BinanceAssetType.SPOT, 'USDT')
    dp.get_all_parallel(provider)
    # provider.get_all()