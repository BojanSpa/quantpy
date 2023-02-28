import requests
import os
from data_store import DataStore
from pathlib import Path
from datetime import datetime, timedelta


class DataLoader:
    time_frame = '1m'

    def __init__(self, conf):
        self.conf = conf
        self.store = DataStore()

    def load_all(self, from_date, load_only = False):
        to_date = datetime.now() - timedelta(days = 1)
        days_diff = (to_date - from_date).days
        # Increase for one day to capture from_date too
        days = list(range(days_diff + 1))

        for symbol in self.conf.symbols:
            for days_back in reversed(days):
                date = to_date - timedelta(days = days_back)
                self.__load(symbol, date, load_only)
        

    def __load(self, symbol, date, load_only):
        raw_directory = self.conf.data_directory
        symbol_directory = f'{raw_directory}raw\{symbol}'
        file_name = self.__get_filename(symbol, date)
        file_path = f'{symbol_directory}\\{file_name}'

        if not os.path.isdir(symbol_directory):
            os.makedirs(symbol_directory)


        # Download missing file
        if not Path(file_path).is_file():
            uri = self.__get_uri(symbol, file_name)
            print(f'Loading: {uri}')
            response = requests.get(uri)
            
            if (response.ok):
                open(file_path, 'wb').write(response.content)
            else:
                print(f'Remote file unavailable!')

        if not load_only:
            self.store.save(symbol, file_path, raw_directory, symbol_directory)


    def __get_filename(self, symbol, date):
        date_str = date.strftime(self.conf.date_format)
        file_name = self.conf.file_format
        file_name = file_name.replace('[[Symbol]]', symbol)
        file_name = file_name.replace('[[Timeframe]]', self.time_frame)
        file_name = file_name.replace('[[Date]]', date_str)
        return file_name


    def __get_uri(self, symbol, file_name):
        return f'{self.conf.base_uri}/{symbol}/{self.time_frame}/{file_name}'