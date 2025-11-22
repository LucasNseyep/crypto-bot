import pandas as pd

def add_momentum_signal(df, fast=20, slow=50):
    df = df.copy()
    df["sma_fast"] = df["close"].rolling(fast).mean()
    df["sma_slow"] = df["close"].rolling(slow).mean()

    # signal: +1 long, 0 flat (you can also do -1 short if you want)
    df["signal_raw"] = 0
    df.loc[df["sma_fast"] > df["sma_slow"], "signal_raw"] = 1
    df.loc[df["sma_fast"] < df["sma_slow"], "signal_raw"] = -1

    return df
