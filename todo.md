# Data handling

	- [X] Download one sample daily 1m data
	- [X] Download for list of symbols
	- [X] Download from start date
	- [X] Unzip
	- [X] Skip existing
	- [X] Save as aggregated pandas storage file
	- [X] Basic resampling for any timeframe
	- [X] CSV Sanitizer
	- [X] Resample on demand 
	- [X] Fetch raw binance data in parallel
	- [O] Initial symbol storage as DataFrame with parallel execution
	- [ ] Resampling with parallel execution
    	- Own directory per data source (binance), asset type (spot/future), and symbol
    	- Resampling to default timeframes
    	- Overwrite flag
  
# Visualization

	- [X] Show basic candlestick chart
	- [X] Tabulated backtest result 
	- [X] Show equity
	- [X] Show drawdown

# Backtesting

	- [X] First simple backtest
	- [X] Basic VectorBacktester
	- [X] DMI tests basic
	- [X] Backtest multiple timeframes
	- [X] Backtest multiple symbols on multiple timeframes
	- [X] BUG: Returns vary for same symbol/tf after each strategy
    	- [X] Calculate returns at resampling

# Indicator

	- [X] Include pandas TA lib (https://github.com/twopirllc/pandas-ta)
	- [ ] Parameter range (One strategy instance per type)
	- [ ] Port moments indicator
	- [ ] Port hurst indicator
	- [ ] Port historic volatility indicator