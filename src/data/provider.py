import os
import requests
import pandas as pd

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

class BinanceDataTimeframe(Enum):
    DAILY = 'daily'
    MONTHLY = 'monthly'


def get_all_parallel(provider):
    symbol_infos = provider.get_symbol_infos()
    __get_all_monthly_parallel(provider, symbol_infos)
    # __get_all_daily_parallel(provider, symbol_infos)

def __get_all_monthly_parallel(provider, symbol_infos):
    with Pool() as pool:
        pool.map(provider.get_monthly_symbol_files, symbol_infos)

def __get_all_daily_parallel(provider, symbol_infos):
    with Pool() as pool:
        pool.map(provider.get_daily_symbol_files, symbol_infos)


class BinanceDataProvider:
    TF = '1m'
    START_DATE = datetime(2017, 1, 1)

    def __init__(self, conf: BianceConfig, asset_type, pair_type):
        self.conf = conf
        self.store = DataStore(conf)
        self.asset_type = asset_type
        self.pair_type = pair_type


    def get_all(self):
        symbol_infos = self.get_symbol_infos()
        for symbol_info in symbol_infos:
            self.get_monthly_symbol_files(symbol_info)
            # self.get_daily_symbol_files(symbol_info)


    def get_symbol_infos(self):
        info_uri = self.__get_info_uri(self.asset_type)
        info_json = requests.get(info_uri).json()
        symbols_data = info_json['symbols']
        
        symbols = list(map(lambda item: {
            'symbol': item['symbol'],
            'onboard_date': self.__get_onboard_date(item)},
             symbols_data))

        symbols = [item for item in symbols if item['symbol'].endswith(self.pair_type)]
        return sorted(symbols, key=lambda item: item['symbol'])


    def get_monthly_symbol_files(self, symbol_info):
        to_date = datetime.now() - pd.DateOffset(months=1)

        symbol = symbol_info['symbol']
        onboard_date = symbol_info['onboard_date']
        
        months_diff = datetime.diff_months(onboard_date, to_date)
        months = list(range(months_diff))

        for months_back in reversed(months):
            date = to_date - pd.DateOffset(months=months_back)
            self.__fetch_file(symbol, date, BinanceDataTimeframe.MONTHLY)


    def get_daily_symbol_files(self, symbol_info):
        to_date = datetime.now() - timedelta(days=1)

        symbol = symbol_info['symbol']
        onboard_date = symbol_info['onboard_date']
        
        days_diff = (to_date - onboard_date).days
        days = list(range(days_diff+1))

        for days_back in reversed(days):
            date = to_date - timedelta(days=days_back)
            self.__fetch_file(symbol, date, BinanceDataTimeframe.DAILY)
            

    def __fetch_file(self, symbol, date, data_timeframe):
        rawdir = self.conf.rawdir
        klinesdir = self.conf.klinesdir

        symbolpath = None
        filename = None
        uri = None
        
        if data_timeframe is BinanceDataTimeframe.MONTHLY:
            symbolpath = f'{rawdir}{klinesdir}{self.asset_type.value}\\monthly\\{symbol}'
            filename = self.__get_filename(symbol, date, self.conf.date_format_monthly)
            uri = self.conf.klines_uri_monthly
        else:
            symbolpath = f'{rawdir}{klinesdir}{self.asset_type.value}\\daily\\{symbol}'
            filename = self.__get_filename(symbol, date, self.conf.date_format_daily)
            uri = self.conf.klines_uri_daily

        filepath = f'{symbolpath}\\{filename}'
        
        if Path(filepath).is_file(): return
        if not os.path.isdir(symbolpath): os.makedirs(symbolpath)

        uri = uri.replace('[[ASSET_TYPE]]', self.__asset_suburi())
        uri = f'{uri}/{symbol}/{self.TF}/{filename}'
        
        print(f'Loading: {uri}')
        response = requests.get(uri)

        if (response.ok): 
            with open(filepath, 'wb') as datafile:
                datafile.write(response.content)
        else:
            print(f'Remote file not available')

    
    def __get_onboard_date(self, item):
        if 'onboardDate' in item.keys():
            return datetime.fromts(item['onboardDate'])
        else:
            return self.START_DATE
        

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
        filename = filename.replace('[[Timeframe]]', self.TF)
        filename = filename.replace('[[Date]]', date.strftime(dateformat))
        return filename