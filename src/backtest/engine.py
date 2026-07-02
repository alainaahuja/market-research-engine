from __future__ import annotations

import pandas as pd

from src.analytics.metrics import calculate_performance_metrics
from src.backtest.portfolio import build_equity_curve, calculate_strategy_returns
from src.backtest.signals import generate_positions
from src.models import BacktestInput, BacktestResult, TradeRecord


def run_backtest(backtest_input: BacktestInput) -> BacktestResult:
    price_data = _validate_price_data(backtest_input.price_data)
    raw_signals = backtest_input.signals

    positions = generate_positions(raw_signals, price_data.index)
    asset_returns = price_data["Close"].pct_change().fillna(0.0).rename("asset_returns")
    strategy_returns = calculate_strategy_returns(
        asset_returns=asset_returns,
        positions=positions,
        fee_rate=backtest_input.fee_rate,
    )
    equity_curve = build_equity_curve(
        returns=strategy_returns,
        initial_capital=backtest_input.initial_capital,
    )
    trade_log = _build_trade_log(price_data["Close"], positions)
    metrics = calculate_performance_metrics(
        returns=strategy_returns,
        equity_curve=equity_curve,
        trade_count=len(trade_log),
    )

    return BacktestResult(
        equity_curve=equity_curve,
        returns=strategy_returns,
        positions=positions,
        trade_log=trade_log,
        metrics=metrics,
    )


def _validate_price_data(price_data: pd.DataFrame) -> pd.DataFrame:
    if "Close" not in price_data.columns:
        raise ValueError("Price data must include a 'Close' column.")
    if price_data.empty:
        raise ValueError("Price data cannot be empty.")
    if price_data.index.hasnans:
        raise ValueError("Price index must not contain missing values.")
    if not price_data.index.is_monotonic_increasing:
        raise ValueError("Price index must be sorted in ascending order.")

    return price_data.copy()


def _build_trade_log(close_prices: pd.Series, positions: pd.Series) -> list[TradeRecord]:
    trades: list[TradeRecord] = []
    entry_date: pd.Timestamp | None = None
    entry_price: float | None = None

    transitions = positions.diff().fillna(positions)
    for timestamp, change in transitions.items():
        if change == 1:
            entry_date = timestamp
            entry_price = float(close_prices.loc[timestamp])
        elif change == -1 and entry_date is not None and entry_price is not None:
            exit_price = float(close_prices.loc[timestamp])
            trades.append(
                TradeRecord(
                    entry_date=entry_date,
                    exit_date=timestamp,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    return_pct=(exit_price / entry_price) - 1.0,
                )
            )
            entry_date = None
            entry_price = None

    return trades
