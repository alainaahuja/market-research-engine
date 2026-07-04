from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta

import pandas as pd

from src.analytics.drawdown import calculate_drawdown
from src.models import StrategyBacktestResult, StrategyComparison
from src.services.strategy_runner import run_strategy_comparison
from src.strategies.catalog import DEFAULT_STRATEGY_KEYS, STRATEGY_DEFINITIONS


def default_start_date() -> date:
    return date.today() - timedelta(days=365 * 3)


def default_end_date() -> date:
    return date.today()


def available_strategy_options() -> list[str]:
    return DEFAULT_STRATEGY_KEYS.copy()


def strategy_labels() -> dict[str, str]:
    return {
        strategy.key: strategy.display_name
        for strategy in STRATEGY_DEFINITIONS.values()
    }


def run_workbench(
    ticker: str,
    start_date: date,
    end_date: date,
    initial_capital: float,
    fee_rate: float,
    strategy_keys: list[str],
    price_fetcher=None,
) -> StrategyComparison:
    return run_strategy_comparison(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        fee_rate=fee_rate,
        strategy_keys=strategy_keys,
        price_fetcher=price_fetcher,
    )


def build_metrics_comparison_table(comparison: StrategyComparison) -> pd.DataFrame:
    rows = []
    for strategy_result in comparison.strategy_results:
        metrics = asdict(strategy_result.result.metrics)
        rows.append(
            {
                "Strategy": strategy_result.strategy.display_name,
                "Total Return": _format_percent(metrics["total_return"]),
                "CAGR": _format_percent(metrics["cagr"]),
                "Annualized Volatility": _format_percent(
                    metrics["annualized_volatility"]
                ),
                "Sharpe Ratio": f'{metrics["sharpe_ratio"]:.2f}',
                "Max Drawdown": _format_percent(metrics["max_drawdown"]),
                "Trade Count": metrics["trade_count"],
            }
        )
    return pd.DataFrame(rows)


def build_equity_chart_data(comparison: StrategyComparison) -> pd.DataFrame:
    return pd.DataFrame(
        {
            strategy_result.strategy.display_name: strategy_result.result.equity_curve
            for strategy_result in comparison.strategy_results
        }
    )


def build_drawdown_chart_data(comparison: StrategyComparison) -> pd.DataFrame:
    return pd.DataFrame(
        {
            strategy_result.strategy.display_name: calculate_drawdown(
                strategy_result.result.equity_curve
            )
            for strategy_result in comparison.strategy_results
        }
    )


def build_price_history_chart_data(comparison: StrategyComparison) -> pd.DataFrame:
    return comparison.price_data[["Close"]].rename(columns={"Close": comparison.ticker})


def select_strategy_result(
    comparison: StrategyComparison, strategy_name: str
) -> StrategyBacktestResult:
    for strategy_result in comparison.strategy_results:
        if strategy_result.strategy.display_name == strategy_name:
            return strategy_result
    raise ValueError(f"Unknown strategy result requested: {strategy_name}")


def build_trade_log_table(strategy_result: StrategyBacktestResult) -> pd.DataFrame:
    if not strategy_result.result.trade_log:
        return pd.DataFrame(
            columns=["Entry Date", "Exit Date", "Entry Price", "Exit Price", "Return"]
        )

    rows = []
    for trade in strategy_result.result.trade_log:
        rows.append(
            {
                "Entry Date": trade.entry_date.date().isoformat(),
                "Exit Date": trade.exit_date.date().isoformat(),
                "Entry Price": round(trade.entry_price, 4),
                "Exit Price": round(trade.exit_price, 4),
                "Return": _format_percent(trade.return_pct),
            }
        )
    return pd.DataFrame(rows)


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"
