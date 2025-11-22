import pandas as pd

def run_backtest(df, fee_bp=5):
    df = df.copy()

    # 1. create returns - returns defined as a percentage difference from yesterday's close
    df["ret"] = df["close"].pct_change().fillna(0)

    # 2. use signal from previous bar to trade this bar - based on the momentum that we found at the previous row, we'll trade today's row or not
    df["position"] = df["signal_raw"].shift(1).fillna(0) # TO REVIEW

    # 3. gross strategy return
    df["strategy_ret_gross"] = df["position"] * df["ret"]

    # 4. simple cost model: pay fee when position changes - when the momentum changes from -1, 1, 0 to something else, you will need to make a trade and incur fees because of that
    df["trade"] = df["position"].diff().abs().fillna(abs(df["position"].iloc[0])) # TO REVIEW
    cost_per_trade = fee_bp / 1e4
    df["cost"] = df["trade"] * cost_per_trade

    df["strategy_ret_net"] = df["strategy_ret_gross"] - df["cost"]

    # 5. equity curve (starting at 1.0)
    df["equity"] = (1 + df["strategy_ret_net"]).cumprod()

    return df
