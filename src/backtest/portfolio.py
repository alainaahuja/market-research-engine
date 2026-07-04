from __future__ import annotations

import pandas as pd


def calculate_strategy_returns(
    asset_returns: pd.Series, positions: pd.Series, fee_rate: float = 0.0
) -> pd.Series:
    if not asset_returns.index.equals(positions.index):
        raise ValueError("Asset returns and positions must share the same index.")
    if not 0.0 <= fee_rate <= 1.0:
        raise ValueError("Fee rate must be between 0.0 and 1.0.")

    gross_returns = positions * asset_returns
    turnover = positions.diff().abs().fillna(positions.abs())
    fees = turnover * fee_rate
    net_returns = gross_returns - fees
    return net_returns.rename("strategy_returns")


def build_equity_curve(
    returns: pd.Series, initial_capital: float
) -> pd.Series:
    if initial_capital <= 0:
        raise ValueError("Initial capital must be greater than zero.")

    equity_curve = initial_capital * (1.0 + returns.fillna(0.0)).cumprod()
    return equity_curve.rename("equity")
