from data.config import load_config
from data.provider import AssetType, PairType, BinanceDataProvider
from data.store import DataStore

if __name__ == '__main__':
    conf = load_config(section='BINANCE')
    provider = BinanceDataProvider(conf, AssetType.PERP, PairType.USDT)
    store = DataStore(conf, provider, AssetType.PERP)
    store.create_symbol_store('BTCUSDT')