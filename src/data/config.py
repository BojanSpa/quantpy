from dataclasses import dataclass
from configparser import ConfigParser


@dataclass
class SectionName:
    general = 'GENERAL'
    binance = 'BINANCE'


@dataclass
class GeneralConfig:
    rawdir: str
    storedir: str


@dataclass
class BianceConfig(GeneralConfig):
    klines_uri: str
    spot_suburi: str
    perp_suburi: str
    coin_suburi: str
    klinesdir: str
    symbols: list
    timeframes: list
    date_format: str
    file_format: str

    def init(conf, section_name):
        rawdir = conf['GENERAL']['RawDir']
        storedir = conf['GENERAL']['StoreDir'] 
        section = conf[section_name]
        
        return BianceConfig(
            rawdir,
            storedir,
            section['KlinesUri'],
            section['SpotSubUri'],
            section['PerpSubUri'],
            section['CoinSubUri'],
            section['KlinesDir'],
            section['Symbols'].split(', '),
            section['Timeframes'].split(', '),
            '%Y-%m-%d',
            section['FileFormat'])


def load_config(name='config', section=None):
    config = __get(name)
    
    match section:
        case 'BINANCE':
            return BianceConfig.init(config, section)
        case None, _:
            raise Exception('Unknown config section')


def __get(name):
    config = ConfigParser()
    config.read(f'{name}.ini')
    return config