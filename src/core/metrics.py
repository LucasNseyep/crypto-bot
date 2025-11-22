# src/core/metrics.py
import numpy as np
import pandas as pd

def compute_cagr(equity: pd.Series, periods_per_year: int = 252) -> float:
    """
    equity: series of equity values (starting at 1.0)
    periods_per_year: 252 for daily, ~365*24 for hourly, etc.
    """
    if equity.empty:
        return 0.0
    start = equity.iloc[0]
    end = equity.iloc[-1]
    n_periods = len(equity)
    if start <= 0 or n_periods <= 1:
        return 0.0
    years = n_periods / periods_per_year
    return (end / start) ** (1 / years) - 1

def compute_max_drawdown(equity: pd.Series) -> float:
    """
    Returns max drawdown as a negative number, e.g. -0.25 for -25%.
    """
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return dd.min()

def compute_sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Returns annualized Sharpe ratio (assuming 0% risk-free).
    """
    if returns.std() == 0 or len(returns) < 2:
        return 0.0
    mean = returns.mean()
    vol = returns.std()
    return np.sqrt(periods_per_year) * mean / vol

def compute_sortino(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Sortino ratio using downside deviation.
    """
    downside = returns[returns < 0]
    if downside.std() == 0 or len(downside) == 0:
        return 0.0
    mean = returns.mean()
    downside_vol = downside.std()
    return np.sqrt(periods_per_year) * mean / downside_vol

def summarize_performance(bt: pd.DataFrame) -> dict:
    """
    bt: result of run_backtest, must have columns:
        - 'datetime' (tz-aware)
        - 'strategy_ret_net'
        - 'equity'
    Returns a dict for API / React.
    """
    # daily returns for cleaner stats
    daily_ret = bt.resample("1D", on="datetime")["strategy_ret_net"].sum()

    cagr = compute_cagr(bt["equity"], periods_per_year=252)
    max_dd = compute_max_drawdown(bt["equity"])
    sharpe = compute_sharpe(daily_ret, periods_per_year=252)
    sortino = compute_sortino(daily_ret, periods_per_year=252)

    total_return = bt["equity"].iloc[-1] - 1.0

    return {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(max_dd),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
    }
