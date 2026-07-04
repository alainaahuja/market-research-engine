from __future__ import annotations

import pandas as pd


def generate_moving_average_signals(
    price_data: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50,
) -> pd.Series:
    close = price_data["Close"]
    short_ma = close.rolling(window=short_window, min_periods=short_window).mean()
    long_ma = close.rolling(window=long_window, min_periods=long_window).mean()
    return (short_ma > long_ma).astype(float).fillna(0.0).rename("signal")
