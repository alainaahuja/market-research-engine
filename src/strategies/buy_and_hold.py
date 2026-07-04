from __future__ import annotations

import pandas as pd


def generate_buy_and_hold_signals(price_data: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=price_data.index, name="signal")
