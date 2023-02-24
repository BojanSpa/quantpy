from dataclasses import dataclass

@dataclass
class DataLoaderConfig:
    base_uri: str
    symbols: list
    date_format: str
    file_format: str