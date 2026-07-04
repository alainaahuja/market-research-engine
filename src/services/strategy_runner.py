from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pandas as pd

from src.backtest.engine import run_backtest
from src.data.market_data import fetch_price_history
from src.models import BacktestInput, StrategyBacktestResult, StrategyComparison
from src.strategies.catalog import (
    DEFAULT_STRATEGY_KEYS,
    STRATEGY_DEFINITIONS,
    STRATEGY_GENERATORS,
    STRATEGY_MIN_OBSERVATIONS,
)


def run_strategy_comparison(
    ticker: str,
    start_date: date,
    end_date: date,
    initial_capital: float,
    fee_rate: float,
    strategy_keys: list[str] | None = None,
    price_fetcher: Callable[..., pd.DataFrame] | None = None,
) -> StrategyComparison:
    selected_strategy_keys = strategy_keys or DEFAULT_STRATEGY_KEYS
    _validate_strategy_keys(selected_strategy_keys)

    fetcher = price_fetcher or fetch_price_history
    price_data = fetcher(ticker=ticker, start_date=start_date, end_date=end_date)
    if not isinstance(price_data, pd.DataFrame):
        raise ValueError("Price fetcher must return a pandas DataFrame.")
    _validate_price_history_length(price_data, selected_strategy_keys)

    strategy_results: list[StrategyBacktestResult] = []
    for strategy_key in selected_strategy_keys:
        result = run_backtest(
            BacktestInput(
                price_data=price_data,
                signals=STRATEGY_GENERATORS[strategy_key](price_data),
                initial_capital=initial_capital,
                fee_rate=fee_rate,
            )
        )
        strategy_results.append(
            StrategyBacktestResult(
                strategy=STRATEGY_DEFINITIONS[strategy_key],
                result=result,
            )
        )

    return StrategyComparison(
        ticker=ticker.strip().upper(),
        price_data=price_data,
        strategy_results=strategy_results,
    )


def _validate_strategy_keys(strategy_keys: list[str]) -> None:
    if not strategy_keys:
        raise ValueError("At least one strategy must be selected.")

    invalid_keys = [key for key in strategy_keys if key not in STRATEGY_DEFINITIONS]
    if invalid_keys:
        raise ValueError(f"Unsupported strategies requested: {', '.join(invalid_keys)}")


def _validate_price_history_length(
    price_data: pd.DataFrame, strategy_keys: list[str]
) -> None:
    observation_count = len(price_data)
    minimum_required = max(STRATEGY_MIN_OBSERVATIONS[key] for key in strategy_keys)
    if observation_count < minimum_required:
        raise ValueError(
            "Selected date range is too short for the chosen strategies. "
            f"Need at least {minimum_required} trading days, found {observation_count}."
        )
