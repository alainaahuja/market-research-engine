from __future__ import annotations

import pandas as pd


def generate_rsi_signals(
    price_data: pd.DataFrame,
    window: int = 14,
    oversold: float = 30.0,
    overbought: float = 70.0,
) -> pd.Series:
    close = price_data["Close"]
    delta = close.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)

    average_gain = gains.rolling(window=window, min_periods=window).mean()
    average_loss = losses.rolling(window=window, min_periods=window).mean()
    relative_strength = average_gain / average_loss.replace(0.0, pd.NA)
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))

    current_signal = 0.0
    signal_values: list[float] = []
    for value in rsi.fillna(50.0):
        if value < oversold:
            current_signal = 1.0
        elif value > overbought:
            current_signal = 0.0
        signal_values.append(current_signal)

    return pd.Series(signal_values, index=price_data.index, name="signal")
