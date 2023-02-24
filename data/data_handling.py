from DataLoaderConfig import DataLoaderConfig
from DataLoader import DataLoader
from configparser import ConfigParser
from datetime import datetime


date_format = '%Y-%m-%d'

if __name__ == '__main__':
    config = ConfigParser()
    config.sections()
    config.read('config.ini')
    
    binance_config = config['BINANCE']
    base_uri = binance_config['BaseUri']
    symbols_string = binance_config['Symbols']
    symbols = symbols_string.split(', ')
    file_format = binance_config['FileFormat']
    data_directory = binance_config['DataDirectory']

    config = DataLoaderConfig(base_uri, symbols, date_format, file_format, data_directory)
    from_date = datetime(2023, 2, 22)
    DataLoader(config).load_all(from_date)