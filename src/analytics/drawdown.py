from __future__ import annotations

import pandas as pd


def calculate_drawdown(equity_curve: pd.Series) -> pd.Series:
    if equity_curve.empty:
        return equity_curve.copy()

    running_peak = equity_curve.cummax()
    drawdown = (equity_curve / running_peak) - 1.0
    return drawdown.rename("drawdown")
