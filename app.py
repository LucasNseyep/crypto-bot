# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.data_reader import load_ohlcv
from src.core.momentum import add_momentum_signal
from src.core.backtest import run_backtest
from src.core.metrics import summarize_performance

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/backtest/momentum")
def backtest_momentum():
    df = load_ohlcv(
        root="data",
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        start="2024-01-01",
        end="2024-04-01",
    )
    df_sig = add_momentum_signal(df)
    bt = run_backtest(df_sig)
    metrics = summarize_performance(bt)

    equity_curve = [
        {"datetime": row.datetime.isoformat(), "equity": float(row.equity)}
        for row in bt[["datetime", "equity"]].itertuples(index=False)
    ]

    return {
        "equity_curve": equity_curve,
        "metrics": metrics,
    }
