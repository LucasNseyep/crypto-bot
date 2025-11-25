# Crypto Trading Project

A full-stack quantitative research environment for building, testing, and visualizing algorithmic crypto trading strategies.
The project includes a data layer, signal generation module, backtesting engine, performance analytics, and an interactive React dashboard for visualization.

## Project Overview

This project implements a complete research pipeline for crypto systematic trading:
* Data ingestion using OHLCV (Open–High–Low–Close–Volume) data.
* Feature engineering and signal generation (currently: momentum signal via SMA crossovers).
* Backtesting engine with simple cost modeling.
* Performance metrics including returns, equity curve, drawdown, Sharpe ratio, and summary statistics.
* FastAPI backend exposing /backtest/momentum for real-time backtests.
* React + Vite frontend that visualizes:
  * Equity curve over time
  * Strategy performance metrics
