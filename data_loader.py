import requests
from logging import info
from dataclasses import dataclass
from configparser import ConfigParser
from datetime import datetime, timedelta

config_path = ''
futures_uri = 'https://data.binance.vision/?prefix=data/futures/um/daily/klines'
symbols = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT'
]

class DataLoader:
    time_frame = '1m'

    def __init__(self, conf):
        self.conf = conf

    def get_all(self):
        yesterday = datetime.now() - timedelta(days = 1)
        symbol = self.conf.symbols[0]
        file_name = self.__getFileName(symbol, yesterday)
        uri = self.__getFileUri(symbol, file_name)
        info(f'Loading file: {uri}')
        request = requests.get(uri)
        open(f'data\{file_name}', 'wb').write(request.content)

    def __getFileName(self, symbol, date):
        date_str = date.strftime(self.conf.date_format)
        file_name = self.conf.file_format
        file_name = file_name.replace('[[Symbol]]', symbol)
        file_name = file_name.replace('[[Timeframe]]', self.time_frame)
        file_name = file_name.replace('[[Date]]', date_str)
        return file_name

    def __getFileUri(self, symbol, file_name):
        return f'{self.conf.base_uri}/{symbol}/{self.time_frame}/{file_name}'

    
@dataclass
class DataLoaderConfig:
    base_uri: str
    symbols: list
    date_format: str
    file_format: str


if __name__ == '__main__':
    config = ConfigParser()
    config.sections()
    config.read('config.ini')
    
    binance_config = config['BINANCE']
    base_uri = binance_config['BaseUri']
    symbols_string = binance_config['Symbols']
    symbols = symbols_string.split(', ')
    date_format = '%Y-%m-%d'
    file_format = binance_config['FileFormat']

    config = DataLoaderConfig(base_uri, symbols, '%Y-%m-%d', file_format)
    data_loader = DataLoader(config)
    data_loader.get_all()