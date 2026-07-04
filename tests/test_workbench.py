from __future__ import annotations

from datetime import date

import pandas as pd

from src.ui.workbench import (
    available_strategy_options,
    build_drawdown_chart_data,
    build_equity_chart_data,
    build_metrics_comparison_table,
    build_price_history_chart_data,
    build_trade_log_table,
    run_workbench,
    select_strategy_result,
)


def _mock_price_fetcher(**_: object) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=80, freq="D")
    closes = [100.0 + index for index in range(80)]
    return pd.DataFrame({"Close": closes}, index=dates)


def test_run_workbench_returns_strategy_comparison() -> None:
    comparison = run_workbench(
        ticker="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=10_000.0,
        fee_rate=0.0,
        strategy_keys=available_strategy_options(),
        price_fetcher=_mock_price_fetcher,
    )

    assert comparison.ticker == "MSFT"
    assert len(comparison.strategy_results) == 4


def test_build_metrics_comparison_table_includes_each_strategy() -> None:
    comparison = run_workbench(
        ticker="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=10_000.0,
        fee_rate=0.0,
        strategy_keys=["buy_and_hold", "momentum"],
        price_fetcher=_mock_price_fetcher,
    )

    table = build_metrics_comparison_table(comparison)

    assert table["Strategy"].tolist() == ["Buy and Hold", "Momentum"]


def test_chart_builders_return_multi_strategy_dataframes() -> None:
    comparison = run_workbench(
        ticker="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=10_000.0,
        fee_rate=0.0,
        strategy_keys=["buy_and_hold", "momentum"],
        price_fetcher=_mock_price_fetcher,
    )

    equity = build_equity_chart_data(comparison)
    drawdown = build_drawdown_chart_data(comparison)
    price_history = build_price_history_chart_data(comparison)

    assert list(equity.columns) == ["Buy and Hold", "Momentum"]
    assert list(drawdown.columns) == ["Buy and Hold", "Momentum"]
    assert list(price_history.columns) == ["MSFT"]


def test_trade_log_table_can_be_selected_per_strategy() -> None:
    comparison = run_workbench(
        ticker="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        initial_capital=10_000.0,
        fee_rate=0.0,
        strategy_keys=["buy_and_hold"],
        price_fetcher=_mock_price_fetcher,
    )

    selected = select_strategy_result(comparison, "Buy and Hold")
    trade_log_table = build_trade_log_table(selected)

    assert isinstance(trade_log_table, pd.DataFrame)
