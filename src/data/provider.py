import os
import requests

from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
from multiprocessing import Pool
from data.config import BianceConfig
from data.store import DataStore
  

class BinanceAssetType(Enum):
    SPOT = 'spot'
    PERP = 'um'
    COIN = 'cm'    


def get_all_parallel(provider):
    symbol_infos = provider.get_symbol_infos()
    with Pool() as pool:
        pool.map(provider.get_symbol_files, symbol_infos)


class BinanceDataProvider:
    timeframe = '1m'

    def __init__(self, conf: BianceConfig, asset_type, pair_type):
        self.conf = conf
        self.store = DataStore(conf)
        self.asset_type = asset_type
        self.pair_type = pair_type


    def get_all(self):
        symbol_infos = self.get_symbol_infos()
        for symbol_info in symbol_infos:
            self.get_symbol_files(symbol_info)


    def get_symbol_files(self, symbol_info):
        to_date = datetime.now() - timedelta(days=1)

        symbol = symbol_info['symbol']
        onboard_date = symbol_info['onboard_date']
        
        days_diff = (to_date - onboard_date).days
        days = list(range(days_diff+1))

        for days_back in reversed(days):
            date = to_date - timedelta(days=days_back)
            self.__get(symbol, date)
            

    def __get(self, symbol, date):
        rawdir = self.conf.rawdir
        klinesdir = self.conf.klinesdir

        symbolpath = f'{rawdir}{klinesdir}{self.asset_type.value}\\{symbol}'
        filename = self.__get_filename(symbol, date, self.conf.date_format)
        filepath = f'{symbolpath}\\{filename}'
        
        if Path(filepath).is_file(): return
        if not os.path.isdir(symbolpath): os.makedirs(symbolpath)

        uri = self.conf.klines_uri
        uri = uri.replace('[[ASSET_TYPE]]', self.__asset_suburi())
        uri = f'{uri}/{symbol}/{self.timeframe}/{filename}'
        
        print(f'Loading: {uri}')

        response = requests.get(uri)
        if (response.ok): 
            open(filepath, 'wb').write(response.content)
        else:
            print(f'Remote file not available')
    

    def get_symbol_infos(self):
        info_uri = self.__get_info_uri(self.asset_type)
        info_json = requests.get(info_uri).json()
        symbols_data = info_json['symbols']
        
        symbols = list(map(lambda item: {
            'symbol': item['symbol'],
            'onboard_date': datetime.fromts(item['onboardDate'])},
             symbols_data))

        symbols = [item for item in symbols if item['symbol'].endswith(self.pair_type)]

        return sorted(symbols, key=lambda item: item['symbol'])
        

    def __get_info_uri(self, asset_type):
        match asset_type:
            case BinanceAssetType.SPOT:
                return 'https://api.binance.com/api/v3/exchangeInfo'
            case BinanceAssetType.PERP:
                return 'https://fapi.binance.com/fapi/v1/exchangeInfo'
            case BinanceAssetType.COIN:
                return 'https://dapi.binance.com/dapi/v1/exchangeInfo'
            case None:
                raise Exception('Asset type not supported')
            case _,:
                raise Exception("Asset type '{_}' not supported")

    def __asset_suburi(self):
        match self.asset_type:
            case BinanceAssetType.SPOT: return self.conf.spot_suburi
            case BinanceAssetType.PERP: return self.conf.perp_suburi
            case BinanceAssetType.COIN: return self.conf.coin_suburi
            case _: raise Exception(f"Asset type '{self.asset_type}' is not supported")

    def __get_filename(self, symbol, date, dateformat):
        filename = self.conf.file_format
        filename = filename.replace('[[Symbol]]', symbol)
        filename = filename.replace('[[Timeframe]]', self.timeframe)
        filename = filename.replace('[[Date]]', date.strftime(dateformat))
        return filename