from dataclasses import dataclass
from configparser import ConfigParser
from typing import List


@dataclass
class SectionName:
    general = 'GENERAL'
    binance = 'BINANCE'


@dataclass
class GeneralConfig:
    storedir: str

    def init(conf):
        return GeneralConfig(conf['StoreDir']) 


@dataclass
class DataProviderConfig:
    storedir: str
    base_uri: str
    uri_spot_daily: str
    uri_spot_monthly: str
    file_format: str
    daily_date_format: str
    monthly_date_format: str
    symbols: List[str]
    source_timeframe: str
    resampling_timeframes: List[str]
    

    def init(conf):
        return DataProviderConfig(
            conf['StoreDir'],
            conf['BaseUri'],
            conf['UriSpotDaily'],
            conf['UriSpotMonthly'],
            conf['FileFormat'],
            conf['DailyDateFormat'],
            conf['MonthlyDateFormat'],
            conf['Symbols'].split(', '),
            conf['SourceTimeframe'],
            conf['ResamplingTimeframes'].split(', '))


def load_config(name: str, section_name: str):
    config = __get(name)
    section = config[section_name]

    match section_name:
        case 'GENERAL':
            return GeneralConfig.init(section)
        case 'BINANCE':
            return DataProviderConfig.init(section)
        case _:
            raise Exception(f'Section name {section_name} not available')


def __get(name):
    config = ConfigParser()
    config.read(f'{name}.ini')
    return config