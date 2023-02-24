import requests
from DataStore import DataStore
from pathlib import Path
from datetime import datetime, timedelta


class DataLoader:
    time_frame = '1m'

    def __init__(self, conf):
        self.conf = conf
        self.store = DataStore()

    def load_all(self, from_date):
        yesterday = datetime.now() - timedelta(days = 1)
        days_diff = (yesterday - from_date).days
        # Increase for one day to capture from_date too
        days = list(range(days_diff + 1))

        for symbol in self.conf.symbols:
            for days_back in reversed(days):
                date = yesterday - timedelta(days = days_back)
                self.__load(symbol, date)
        

    def __load(self, symbol, date):
        file_name = self.__get_filename(symbol, date)
        file_path = f'{self.conf.data_directory}{file_name}'
        # Skip files which are already downloaded
        if Path(file_path).is_file():
            return
        
        uri = self.__get_uri(symbol, file_name)
        request = requests.get(uri)
        open(file_path, 'wb').write(request.content)
        self.store.save(file_path, self.conf.data_directory)


    def __get_filename(self, symbol, date):
        date_str = date.strftime(self.conf.date_format)
        file_name = self.conf.file_format
        file_name = file_name.replace('[[Symbol]]', symbol)
        file_name = file_name.replace('[[Timeframe]]', self.time_frame)
        file_name = file_name.replace('[[Date]]', date_str)
        return file_name


    def __get_uri(self, symbol, file_name):
        return f'{self.conf.base_uri}/{symbol}/{self.time_frame}/{file_name}'