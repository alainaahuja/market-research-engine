from __future__ import annotations

import pandas as pd


def generate_momentum_signals(
    price_data: pd.DataFrame,
    lookback: int = 20,
) -> pd.Series:
    close = price_data["Close"]
    momentum = close / close.shift(lookback) - 1.0
    return (momentum > 0).astype(float).fillna(0.0).rename("signal")
