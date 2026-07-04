from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.models import StrategyDefinition
from src.strategies.buy_and_hold import generate_buy_and_hold_signals
from src.strategies.momentum import generate_momentum_signals
from src.strategies.moving_average import generate_moving_average_signals
from src.strategies.rsi import generate_rsi_signals


StrategySignalGenerator = Callable[[pd.DataFrame], pd.Series]


STRATEGY_DEFINITIONS: dict[str, StrategyDefinition] = {
    "buy_and_hold": StrategyDefinition(
        key="buy_and_hold",
        display_name="Buy and Hold",
        description="Stay long for the full test window.",
    ),
    "moving_average": StrategyDefinition(
        key="moving_average",
        display_name="Moving Average Crossover",
        description="Go long when the short moving average is above the long moving average.",
    ),
    "rsi": StrategyDefinition(
        key="rsi",
        display_name="RSI",
        description="Enter on oversold conditions and exit on overbought conditions.",
    ),
    "momentum": StrategyDefinition(
        key="momentum",
        display_name="Momentum",
        description="Go long when trailing price momentum is positive.",
    ),
}


STRATEGY_GENERATORS: dict[str, StrategySignalGenerator] = {
    "buy_and_hold": generate_buy_and_hold_signals,
    "moving_average": generate_moving_average_signals,
    "rsi": generate_rsi_signals,
    "momentum": generate_momentum_signals,
}


DEFAULT_STRATEGY_KEYS: list[str] = [
    "buy_and_hold",
    "moving_average",
    "rsi",
    "momentum",
]


STRATEGY_MIN_OBSERVATIONS: dict[str, int] = {
    "buy_and_hold": 2,
    "moving_average": 50,
    "rsi": 15,
    "momentum": 21,
}
