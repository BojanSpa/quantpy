from DataLoaderConfig import DataLoaderConfig
from DataLoader import DataLoader
from DataStore import DataStore
from configparser import ConfigParser
from datetime import datetime


date_format = '%Y-%m-%d'

def init_load():
    config = load_config()
    
    binance_config = config['BINANCE']
    base_uri = binance_config['BaseUri']
    symbols_string = binance_config['Symbols']
    symbols = symbols_string.split(', ')
    file_format = binance_config['FileFormat']
    data_directory = binance_config['DataDirectory']

    config = DataLoaderConfig(base_uri, symbols, date_format, file_format, data_directory)
    from_date = datetime(2022, 1, 1)
    DataLoader(config).load_all(from_date, load_only=False)


def resample():
    config = load_config()
    general_config = config['GENERAL']
    storedir = general_config['StoreDirectory']
    DataStore().resample(storedir, 'BTCUSDT', '15min')


def load_config():
    config = ConfigParser()
    config.sections()
    config.read('config.ini')
    return config



if __name__ == '__main__':
    init_load()
    #resample()