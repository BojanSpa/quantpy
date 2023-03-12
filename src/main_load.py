import json

from datetime import datetime
from tabulate import tabulate
from utils import datetime_extensions
from data.config import load_config
from data.provider import BinanceAssetType, BinanceDataProvider, get_all_parallel


if __name__ == '__main__':
    conf = load_config(section='BINANCE')
    provider = BinanceDataProvider(conf, BinanceAssetType.PERP, 'USDT')
    # get_all_parallel(provider)
    provider.get_all()