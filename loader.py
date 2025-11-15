import ccxt
import time
from datetime import datetime, timezone
from typing import Optional

import os
from pathlib import Path
import pandas as pd

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

# print(fetch_ohlcv_once(get_exchange(), "BTC/USDT", "1h", None, 100).tail(10))

# turning timeframes into ms
def timeframe_to_ms(tf: str) -> int:
    if tf.endswith("m"):
        return int(tf[:-1]) * 60_000
    if tf.endswith("h"):
        return int(tf[:-1]) * 3_600_000
    if tf.endswith("d"):
        return int(tf[:-1]) * 86_400_000
    raise ValueError(f"Unsupported timeframe: {tf}")

# get chunk * limit candles all with 1 hour increments
def fetch_many(
    exchange_id="binance",
    symbol="BTC/USDT",
    timeframe="1h",
    start_utc="2024-01-01T00:00:00Z",
    chunks=5,
    limit=1000,
):
    exchange = get_exchange(exchange_id)
    tf_ms = timeframe_to_ms(timeframe)

    # convert start string → ms
    start_dt = datetime.fromisoformat(start_utc.replace("Z", "+00:00"))
    since_ms = int(start_dt.timestamp() * 1000)

    all_parts = []

    for i in range(chunks):
        df_chunk = fetch_ohlcv_once(exchange, symbol, timeframe, since=since_ms, limit=limit)
        if df_chunk.empty:
            print("empty chunk, stopping")
            break

        all_parts.append(df_chunk)

        last_ts = int(df_chunk["timestamp"].iloc[-1])
        since_ms = last_ts + tf_ms    # move pointer forward

        time.sleep(0.2)

    if not all_parts:
        return pd.DataFrame()

    # combine & dedupe
    combo = pd.concat(all_parts, ignore_index=True)
    combo = combo.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
    return combo

# print(fetch_many())

def symbol_to_path_part(symbol: str) -> str:
    # "BTC/USDT" -> "BTC-USDT"
    return symbol.replace("/", "-")

def get_output_path(root: Path, exchange_id: str, symbol: str, timeframe: str, month_str: str) -> Path:
    return root / exchange_id / symbol_to_path_part(symbol) / timeframe / f"{month_str}.parquet"

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def add_month_col(df: pd.DataFrame) -> pd.DataFrame:
    # assumes df["timestamp"] is ms
    df = df.copy()
    df["month"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m")
    return df

def save_monthly_parquet(
    df: pd.DataFrame,
    root: str | Path = "data",
    exchange_id: str = "binance",
    symbol: str = "BTC/USDT",
    timeframe: str = "1h"
):
    if df.empty:
        print("No data to save.")
        return

    root = Path(root)
    df = add_month_col(df)

    for month_str, chunk in df.groupby("month"):
        out_path = get_output_path(root, exchange_id, symbol, timeframe, month_str)
        ensure_dir(out_path.parent)

        # if file exists, read it and merge (so reruns don't duplicate)
        if out_path.exists():
            existing = pd.read_parquet(out_path)
            merged = (
                pd.concat([existing, chunk.drop(columns=["month"])], ignore_index=True)
                  .drop_duplicates(subset=["timestamp"])
                  .sort_values("timestamp")
            )
        else:
            merged = chunk.drop(columns=["month"]).sort_values("timestamp")

        merged.to_parquet(out_path, index=False)
        print(f"✅ Saved {len(merged)} rows → {out_path}")

def load_ohlcv(
    root: str | Path,
    exchange: str,
    symbol: str,
    timeframe: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    resample_rule: Optional[str] = None
) -> pd.DataFrame:
    """
    Load OHLCV data from Parquet files into a single DataFrame.

    Args:
        root: base data folder (e.g. "data")
        exchange: exchange id (e.g. "binance")
        symbol: market pair (e.g. "BTC/USDT")
        timeframe: timeframe folder (e.g. "1h")
        start, end: optional datetime strings ("2024-01-01", "2024-07-01T00:00Z")
        resample_rule: optional pandas resample rule (e.g. "5T", "1H", "1D")

    Returns:
        DataFrame with columns: timestamp, datetime, open, high, low, close, volume
    """
    root = Path(root)
    safe_symbol = symbol.replace("/", "-")
    folder = root / exchange / safe_symbol / timeframe
    if not folder.exists():
        raise FileNotFoundError(f"No data found at {folder}")

    # Read all Parquet files
    files = sorted(folder.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No Parquet files in {folder}")

    dfs = []
    for p in files:
        df = pd.read_parquet(p)
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")

    # Add readable datetime
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    # Filter by start/end if provided
    if start:
        start_dt = pd.to_datetime(start, utc=True)
        df = df[df["datetime"] >= start_dt]
    if end:
        end_dt = pd.to_datetime(end, utc=True)
        df = df[df["datetime"] <= end_dt]

    # Optional resampling
    if resample_rule:
        df = resample_ohlcv(df, rule=resample_rule)
        # df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    df = df.reset_index(drop=True)
    return df

def resample_ohlcv(df: pd.DataFrame, rule: str = "5T") -> pd.DataFrame:
    """
    Resample OHLCV DataFrame to a new timeframe.

    rule examples:
      "5T" = 5 minutes
      "1H" = 1 hour
      "1D" = 1 day
    """
    df = df.set_index("datetime")
    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "timestamp": "last",
    }
    out = df.resample(rule, label="right", closed="right").agg(agg).dropna()
    out = out.reset_index()
    return out



if __name__ == "__main__":
    df = fetch_many(
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        start_utc="2024-01-01T00:00:00Z",
        chunks=3,      # try 3 pages first
        limit=500
    )
    print(df.head())
    print(df.tail())
    print("rows fetched:", len(df))

    save_monthly_parquet(
        df,
        root="data",
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1h"
    )
