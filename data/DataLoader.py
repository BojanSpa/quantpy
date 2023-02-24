import requests
from datetime import datetime, timedelta

class DataLoader:
    time_frame = '1m'

    def __init__(self, conf):
        self.conf = conf

    def load_all(self):
        yesterday = datetime.now() - timedelta(days = 1)
        for symbol in self.conf.symbols:
            self.__load(symbol, yesterday)
        
    def __load(self, symbol, date):
        file_name = self.__get_filename(symbol, date)
        uri = self.__get_uri(symbol, file_name)
        request = requests.get(uri)
        open(f'data\\raw\\{file_name}', 'wb').write(request.content)

    def __get_filename(self, symbol, date):
        date_str = date.strftime(self.conf.date_format)
        file_name = self.conf.file_format
        file_name = file_name.replace('[[Symbol]]', symbol)
        file_name = file_name.replace('[[Timeframe]]', self.time_frame)
        file_name = file_name.replace('[[Date]]', date_str)
        return file_name

    def __get_uri(self, symbol, file_name):
        return f'{self.conf.base_uri}/{symbol}/{self.time_frame}/{file_name}'