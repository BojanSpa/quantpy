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
class BinanceConfig(GeneralConfig):
    klines_uri_monthly: str
    klines_uri_daily: str
    spot_suburi: str
    perp_suburi: str
    coin_suburi: str
    klinesdir: str
    symbols: list
    timeframes: list
    date_format_monthly: str
    date_format_daily: str
    file_format: str

    def init(conf, section_name):
        rawdir = conf['GENERAL']['RawDir']
        storedir = conf['GENERAL']['StoreDir'] 
        section = conf[section_name]
        
        return BinanceConfig(
            rawdir,
            storedir,
            section['KlinesUriMonthly'],
            section['KlinesUriDaily'],
            section['SpotSubUri'],
            section['PerpSubUri'],
            section['CoinSubUri'],
            section['KlinesDir'],
            section['Symbols'].split(', '),
            section['Timeframes'].split(', '),
            '%Y-%m',
            '%Y-%m-%d',
            section['FileFormat'])


def load_config(name='config', section=None):
    config = __get(name)
    match section:
        case 'BINANCE':
            return BinanceConfig.init(config, section)
        case None, _:
            raise Exception('Unknown config section')


def __get(name):
    config = ConfigParser()
    config.read(f'{name}.ini')
    return config