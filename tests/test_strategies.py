from __future__ import annotations

import pandas as pd

from src.strategies.buy_and_hold import generate_buy_and_hold_signals
from src.strategies.momentum import generate_momentum_signals
from src.strategies.moving_average import generate_moving_average_signals
from src.strategies.rsi import generate_rsi_signals


def _price_data(closes: list[float]) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    return pd.DataFrame({"Close": closes}, index=dates)


def test_buy_and_hold_is_long_on_every_bar() -> None:
    prices = _price_data([100.0, 101.0, 102.0])

    signals = generate_buy_and_hold_signals(prices)

    assert signals.tolist() == [1.0, 1.0, 1.0]


def test_moving_average_signals_turn_on_after_short_crosses_long() -> None:
    prices = _price_data([10.0, 10.0, 10.0, 12.0, 14.0, 16.0])

    signals = generate_moving_average_signals(prices, short_window=2, long_window=3)

    assert signals.tolist() == [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]


def test_momentum_signals_turn_on_for_positive_lookback_return() -> None:
    prices = _price_data([100.0, 90.0, 110.0, 120.0])

    signals = generate_momentum_signals(prices, lookback=2)

    assert signals.tolist() == [0.0, 0.0, 1.0, 1.0]


def test_rsi_signals_enter_on_oversold_and_exit_on_overbought() -> None:
    prices = _price_data([100.0, 90.0, 80.0, 120.0, 140.0, 160.0])

    signals = generate_rsi_signals(
        prices,
        window=2,
        oversold=40.0,
        overbought=60.0,
    )

    assert signals.tolist()[2] == 1.0
    assert signals.tolist()[-1] == 0.0
