from __future__ import annotations

import math

import pandas as pd

from src.analytics.drawdown import calculate_drawdown
from src.models import PerformanceMetrics


def calculate_performance_metrics(
    returns: pd.Series,
    equity_curve: pd.Series,
    trade_count: int,
    annualization_factor: int = 252,
    risk_free_rate: float = 0.0,
) -> PerformanceMetrics:
    clean_returns = returns.fillna(0.0)
    total_return = _calculate_total_return(equity_curve)
    cagr = _calculate_cagr(equity_curve, annualization_factor)
    annualized_volatility = _calculate_annualized_volatility(
        clean_returns, annualization_factor
    )
    sharpe_ratio = _calculate_sharpe_ratio(
        clean_returns,
        annualization_factor=annualization_factor,
        risk_free_rate=risk_free_rate,
    )
    max_drawdown = _calculate_max_drawdown(equity_curve)

    return PerformanceMetrics(
        total_return=total_return,
        cagr=cagr,
        annualized_volatility=annualized_volatility,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        trade_count=trade_count,
    )


def _calculate_total_return(equity_curve: pd.Series) -> float:
    if equity_curve.empty or equity_curve.iloc[0] == 0:
        return 0.0
    return float((equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1.0)


def _calculate_cagr(equity_curve: pd.Series, annualization_factor: int) -> float:
    if len(equity_curve) < 2 or equity_curve.iloc[0] <= 0 or equity_curve.iloc[-1] <= 0:
        return 0.0

    years = len(equity_curve) / annualization_factor
    if years <= 0:
        return 0.0
    return float((equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1.0 / years) - 1.0)


def _calculate_annualized_volatility(
    returns: pd.Series, annualization_factor: int
) -> float:
    if len(returns) < 2:
        return 0.0
    daily_volatility = returns.std(ddof=1)
    if pd.isna(daily_volatility):
        return 0.0
    return float(daily_volatility * math.sqrt(annualization_factor))


def _calculate_sharpe_ratio(
    returns: pd.Series,
    annualization_factor: int,
    risk_free_rate: float,
) -> float:
    if len(returns) < 2:
        return 0.0

    excess_daily_returns = returns - (risk_free_rate / annualization_factor)
    volatility = excess_daily_returns.std(ddof=1)
    if pd.isna(volatility) or volatility == 0:
        return 0.0

    return float(
        (excess_daily_returns.mean() / volatility) * math.sqrt(annualization_factor)
    )


def _calculate_max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    drawdown = calculate_drawdown(equity_curve)
    if drawdown.empty:
        return 0.0
    return float(drawdown.min())
