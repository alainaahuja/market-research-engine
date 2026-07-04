from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.services.strategy_runner import run_strategy_comparison


def _mock_price_fetcher(**_: object) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=80, freq="D")
    closes = [100.0 + index for index in range(80)]
    return pd.DataFrame({"Close": closes}, index=dates)


def test_run_strategy_comparison_returns_all_requested_strategies() -> None:
    comparison = run_strategy_comparison(
        ticker="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=10_000.0,
        fee_rate=0.0,
        strategy_keys=["buy_and_hold", "moving_average", "momentum", "rsi"],
        price_fetcher=_mock_price_fetcher,
    )

    assert comparison.ticker == "AAPL"
    assert len(comparison.strategy_results) == 4
    assert [result.strategy.key for result in comparison.strategy_results] == [
        "buy_and_hold",
        "moving_average",
        "momentum",
        "rsi",
    ]


def test_run_strategy_comparison_rejects_unknown_strategy_keys() -> None:
    with pytest.raises(ValueError, match="Unsupported strategies"):
        run_strategy_comparison(
            ticker="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            initial_capital=10_000.0,
            fee_rate=0.0,
            strategy_keys=["unknown_strategy"],
            price_fetcher=_mock_price_fetcher,
        )


def test_run_strategy_comparison_rejects_too_short_date_ranges() -> None:
    def short_price_fetcher(**_: object) -> pd.DataFrame:
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        closes = [100.0 + index for index in range(10)]
        return pd.DataFrame({"Close": closes}, index=dates)

    with pytest.raises(ValueError, match="too short"):
        run_strategy_comparison(
            ticker="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            initial_capital=10_000.0,
            fee_rate=0.0,
            strategy_keys=["moving_average"],
            price_fetcher=short_price_fetcher,
        )
