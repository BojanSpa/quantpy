import os
import pandas as pd
import tables as tb
import tstables as tst

from zipfile import ZipFile, is_zipfile
from data.config import GeneralConfig
from data.sanitizer import CsvSanitizer


class DataStore:
    csv_header = 'open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore'


    def __init__(self, config):
        self.config = config


    def save(self, sym, fn, storedir, rawdir):
        if (fn.endswith('.zip')):
            if not is_zipfile(fn): return
            self.__extract(fn, rawdir)
            fn = fn.replace('zip', 'csv')
        
        sanitizer = CsvSanitizer()
        sanitizer.clean(fn, self.csv_header) 

        data = pd.read_csv(fn)
        self.__sanitize(data)
        os.remove(fn)

        store_file = f'{storedir}\\{sym}.h5'
        store = tb.open_file(store_file, 'a')
        table = None

        symbol_group = f'/{sym}'
        if store.__contains__(symbol_group) == False:
            table = store.create_ts('/', sym, SymbolTableDescription)
        else:
            table_node = store.root.__getitem__(symbol_group)
            table = tst.get_timeseries(table_node)

        table.append(data)
        store.close()


    def load(self, symbol, tf = None, fd = None, td = None):
        if tf is not None: 
            tf = f'_{tf}'
        else:
            tf = ''

        fn = f'{self.config.storedir}{symbol}{tf}.h5'
        file = tb.open_file(fn, 'a')
        group = f'/{symbol}'
        node = file.root.__getitem__(group)
        table = tst.get_timeseries(node)

        if fd is None: fd = table.min_dt()
        if td is None: td = table.max_dt()

        return table.read_range(fd, td)


    def resample(self, dir, sym, tf):
        datafile = f'{dir}{sym}.h5'
        store = tb.open_file(datafile, 'a')
        group = f'/{sym}'

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
        tf_data = data.resample(tf, label = 'right').agg(args)

        tf_storefile = f'{dir}\{sym}_{tf}.h5'
        tf_store = tb.open_file(tf_storefile, 'a')
        tf_table = tf_store.create_ts('/', sym, SymbolTableDescription)
        tf_table.append(tf_data)

        tf_store.close()
        store.close()


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


class SymbolTableDescription(tb.IsDescription):
    timestamp = tb.Int64Col(pos = 0)
    open = tb.Float64Col(pos = 1)
    high = tb.Float64Col(pos = 2)
    low = tb.Float64Col(pos = 3)
    close = tb.Float64Col(pos = 4)
    volume = tb.Float64Col(pos = 5)