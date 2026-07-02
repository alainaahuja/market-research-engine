from __future__ import annotations

import pandas as pd


def generate_positions(raw_signals: pd.Series, price_index: pd.Index) -> pd.Series:
    """Shift raw signals forward one bar to avoid look-ahead bias."""
    if raw_signals is None:
        raise ValueError("Signals are required.")
    if raw_signals.index.hasnans or price_index.hasnans:
        raise ValueError("Indexes must not contain missing values.")
    if not raw_signals.index.equals(price_index):
        raise ValueError("Signal index must exactly match the price index.")

    invalid_values = set(raw_signals.dropna().unique()) - {0, 1}
    if invalid_values:
        raise ValueError("Signals must contain only binary values: 0 or 1.")

    shifted = raw_signals.shift(1).fillna(0).astype(float)
    shifted.index = price_index
    return shifted.rename("position")
