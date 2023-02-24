from DataLoaderConfig import DataLoaderConfig
from DataLoader import DataLoader
from configparser import ConfigParser

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

    config = DataLoaderConfig(base_uri, symbols, date_format, file_format)
    DataLoader(config).load_all()