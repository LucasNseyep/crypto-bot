from src.core.data_reader import load_ohlcv

df = load_ohlcv(
    root="data",
    exchange="binance",
    symbol="BTC/USDT",
    timeframe="1h",
    start="2024-01-01",
    end="2024-04-01",
)

print(df.head())
print(df.tail())
print(f"{len(df):,} rows loaded")

# Resample example
df_5h = load_ohlcv(
    root="data",
    exchange="binance",
    symbol="BTC/USDT",
    timeframe="1h",
    start="2024-01-01",
    end="2024-04-01",
    resample_rule="5h"
)
print(df_5h.head())
print(df_5h.tail())
print(f"{len(df_5h)} rows after resampling")
