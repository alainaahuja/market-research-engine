from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class BacktestInput:
    price_data: pd.DataFrame
    signals: pd.Series
    initial_capital: float = 10_000.0
    fee_rate: float = 0.0


@dataclass(frozen=True)
class TradeRecord:
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    return_pct: float


@dataclass(frozen=True)
class PerformanceMetrics:
    total_return: float
    cagr: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    trade_count: int


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: pd.Series
    returns: pd.Series
    positions: pd.Series
    trade_log: list[TradeRecord]
    metrics: PerformanceMetrics


@dataclass(frozen=True)
class StrategyDefinition:
    key: str
    display_name: str
    description: str


@dataclass(frozen=True)
class StrategyBacktestResult:
    strategy: StrategyDefinition
    result: BacktestResult


@dataclass(frozen=True)
class StrategyComparison:
    ticker: str
    price_data: pd.DataFrame
    strategy_results: list[StrategyBacktestResult] = field(default_factory=list)
