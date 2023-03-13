import os
import re
import pandas as pd
import pandas_ta as pdta
import tables as tb
import tstables as tst

from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, is_zipfile
from multiprocessing import Pool
from utils import datetime_extensions
from data.sanitizer import CsvSanitizer
from data.provider import AssetType


def create_all_parallel(provider, store):
    symbol_infos = provider.get_symbol_infos()
    symbols = symbol_infos.map(lambda si: si['symbol'])
    with Pool() as pool:
        pool.map(store.save_all, symbols)


class SymbolTableDescription(tb.IsDescription):
    timestamp = tb.Int64Col(pos = 0)
    open = tb.Float64Col(pos = 1)
    high = tb.Float64Col(pos = 2)
    low = tb.Float64Col(pos = 3)
    close = tb.Float64Col(pos = 4)
    volume = tb.Float64Col(pos = 5)
    log_return = tb.Float64Col(pos = 6)
    cum_return = tb.Float64Col(pos = 7)


def get_rawdatadir(conf, asset_type):
    rawdir = conf.rawdir
    klinesdir = conf.klinesdir
    assetdir = None

    match asset_type:
        case AssetType.SPOT:
            assetdir = 'spot'
        case AssetType.PERP:
            assetdir = 'um'
        case AssetType.COIN:
            assetdir = 'cm'

    return f'{rawdir}{klinesdir}{assetdir}\\[[RANGE]]\\'


class DataStore:
    csv_header = 'open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore'


    def __init__(self, conf, provider, asset_type):
        self.conf = conf
        self.provider = provider
        self.asset_type = asset_type
        self.rawdatadir = get_rawdatadir(conf, asset_type)
        self.sanitizer = CsvSanitizer()


    def create_all(self):
        symbol_infos = self.provider.get_symbol_infos()
        symbols = symbol_infos.map(lambda syminf: syminf['symbol'])
        
        for symbol in symbols:
            self.create_symbol_store(symbol)


    def create_symbol_store(self, symbol, symboldir=None):
        if symboldir is None: symboldir = self.__get_symboldir(symbol)
        
        datafiles = os.listdir(symboldir)
        if not datafiles:
            print("No files for symbol '{symbol}' found")
            return

        filesets = sorted(self.__get_filedates(symbol, datafiles), key=lambda fd: fd['date'])

        filerange_valid = self.__is_filerange_valid(filesets)
        if not filerange_valid:
            print("Range of datafiles incomplete")
            return

        
        

    def __get_filedates(self, symbol, datafiles):
        ext_len = 4
        il = len(symbol) + len('-1m-')
        ir = len(datafiles[0]) - ext_len
        format = self.conf.date_format_monthly

        for datafile in datafiles:
            filedate = datetime.strptime(datafile[il:ir], format) 
            yield {'date': filedate, 'file': datafile}


    def __is_filerange_valid(self, filesets):
        filedates = [fileset['date'] for fileset in filesets]

        min_date = min(filedates)
        max_date = max(filedates)
        months_diff = datetime.months_between(min_date, max_date)
        months = list(range(months_diff))
        
        expected_dates = []
        for months_back in reversed(months):
            expected_date = max_date - pd.DateOffset(months=months_back)
            expected_dates.append(expected_date)
            
        filedates.sort()
        expected_dates.sort()

        if (filedates == expected_dates): return True
        else: return False


    def __get_symboldir(self, symbol):
        symboldir = f'{self.rawdatadir}{symbol}\\'.replace('[[RANGE]]', 'monthly')
        if not os.path.isdir(symboldir): 
            raise Exception(f"Directory '{symboldir}' does not exist")
        return symboldir


    def save(self, symbol, filename, storedir, rawdir):
        if (filename.endswith('.zip')):
            if not is_zipfile(filename): return
            self.__extract(filename, rawdir)
            filename = filename.replace('zip', 'csv')
        
        sanitizer = CsvSanitizer()
        sanitizer.clean(filename, self.csv_header) 

        data = pd.read_csv(filename)
        self.__sanitize(data)
        os.remove(filename)

        store_file = f'{storedir}\\{symbol}.h5'
        store = tb.open_file(store_file, 'a')
        table = None

        symbol_group = f'/{symbol}'
        if store.__contains__(symbol_group) == False:
            table = store.create_ts('/', symbol, SymbolTableDescription)
        else:
            table_node = store.root.__getitem__(symbol_group)
            table = tst.get_timeseries(table_node)

        table.append(data)
        store.close()


    def load(self, symbol, timeframe = None, fromdate = None, todate = None, simple=False):
        file = self.__get_file(symbol, timeframe) 
        group = f'/{symbol}'
        node = file.root.__getitem__(group)
        table = tst.get_timeseries(node)

        if fromdate is None: fromdate = table.min_dt()
        if todate is None: todate = table.max_dt()

        data = table.read_range(fromdate, todate)
        if simple:
            data.drop(columns = ['open', 'high', 'low', 'volume'], inplace=True)

        return data


    def __get_file(self, symbol, timeframe):
        filename = f'{symbol}.h5'
        if timeframe is not None:
            filename = f'{symbol}_{timeframe}.h5'

        filepath = f'{self.conf.storedir}{filename}'

        if not Path(filepath).is_file():
            print(f"File '{filename}' not found, resampling...")
            self.resample(self.conf.storedir, symbol, timeframe)

        return tb.open_file(filepath, 'a')


    def resample(self, dir, symbol, timeframe):
        datafile = f'{dir}{symbol}.h5'
        store = tb.open_file(datafile, 'a')
        group = f'/{symbol}'

        node = store.root.__getitem__(group)
        table = tst.get_timeseries(node)
        
        fromdate = table.min_dt()
        todate = table.max_dt()

        data = table.read_range(fromdate, todate)
        args = { 
            'open': 'first', 
            'high': 'max', 
            'low': 'min', 
            'close': 'last',
            'volume': 'sum' }
        tf_data = data.resample(timeframe, label='right').agg(args)

        self.__calc_returns(tf_data)

        tf_storefile = f'{dir}\{symbol}_{timeframe}.h5'
        tf_store = tb.open_file(tf_storefile, 'a')
        tf_table = tf_store.create_ts('/', symbol, SymbolTableDescription)
        tf_table.append(tf_data)

        tf_store.close()
        store.close()
        print('Resampling done')

    
    def __calc_returns(self, data):
        data['log_return'] = pdta.log_return(data.close)
        data['cum_return'] = pdta.log_return(data.close, cumulative=True)


    def __extract(self, fn, dir):
        with ZipFile(fn, 'r') as zip_ref:
            zip_ref.extractall(dir)


    def __sanitize(self, data):
        data.drop(
            columns = ['close_time', 'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'], 
            inplace = True,
            errors = 'ignore')

        data['open_time'] = pd.to_datetime(data['open_time'], unit = 'ms')
        data['open'] = pd.to_numeric(data['open'])
        data['high'] = pd.to_numeric(data['high'])
        data['low'] = pd.to_numeric(data['low'])
        data['close'] = pd.to_numeric(data['close'])
        data['volume'] = pd.to_numeric(data['volume'])

        data.set_index('open_time', inplace = True)