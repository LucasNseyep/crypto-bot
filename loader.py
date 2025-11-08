import ccxt
import pandas as pd
import time
from datetime import datetime, timezone

def get_exchange(exchange_id="binance"):
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class({"enableRateLimit": True})

def fetch_ohlcv_once(exchange, symbol: str, timeframe: str, since: int | None = None, limit: int = 500) -> pd.DataFrame:
    """
    Fetch ONE chunk of OHLCV and return as DataFrame.
    since: ms since epoch (UTC). If None, exchange returns latest candles.
    """
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    if df.empty:
        return df
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return df

print(fetch_ohlcv_once(get_exchange(), "BTC/USDT", "1h", None, 100).tail(10))


# def timeframe_to_ms(tf: str) -> int:
#     if tf.endswith("m"):
#         return int(tf[:-1]) * 60_000
#     if tf.endswith("h"):
#         return int(tf[:-1]) * 3_600_000
#     if tf.endswith("d"):
#         return int(tf[:-1]) * 86_400_000
#     raise ValueError(f"Unsupported timeframe: {tf}")
