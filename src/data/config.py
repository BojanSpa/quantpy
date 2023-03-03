from dataclasses import dataclass
from configparser import ConfigParser


@dataclass
class SectionName:
    general = 'GENERAL'
    binance = 'BINANCE'


@dataclass
class GeneralConfig:
    storedir: str

    def init(conf):
        return GeneralConfig(conf['StoreDirectory']) 


@dataclass
class DataLoaderConfig:
    base_uri: str
    symbols: list
    timeframes: list
    date_format: str
    file_format: str
    data_directory: str

    def init(conf):
        return DataLoaderConfig(
            conf['BaseUri'],
            conf['Symbols'].split(', '),
            conf['Timeframes'].split(', '),
            '%Y-%m-%d',
            conf['FileFormat'],
            conf['DataDirectory'])


def load_config(name: str, section_name: str):
    config = __get(name)
    section = config[section_name]

    match section_name:
        case 'GENERAL':
            return GeneralConfig.init(section)
        case 'BINANCE':
            return DataLoaderConfig.init(section)


def __get(name):
    config = ConfigParser()
    config.read(f'{name}.ini')
    return config