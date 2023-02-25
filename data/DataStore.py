import os
import pandas as pd
import tables as tb
import tstables
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timedelta


class DataStore:
    def save(self, symbol, file_path, store_directory, raw_directory):
        csv_file_path = file_path.replace('zip', 'csv')
        
        if (file_path.endswith('.zip')):
            self.__extract(file_path, raw_directory)
        
        data = pd.read_csv(csv_file_path)
        self.__sanitize(data)
        os.remove(csv_file_path)

        store_file_path = f'{store_directory}\\{symbol}.h5'
        store = tb.open_file(store_file_path, 'a')
        table = None

        symbol_group = f'/{symbol}'
        if store.__contains__(symbol_group) == False:
            table = store.create_ts('/', symbol, SymbolTableDescription)
        else:
            table_node = store.root.__getitem__(symbol_group)
            table = tstables.get_timeseries(table_node)

        table.append(data)
        store.close()


    def __extract(self, file_path, directory):
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(directory)

    def __sanitize(self, data):
        data.drop(columns = ['close_time', 'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'], inplace = True)

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