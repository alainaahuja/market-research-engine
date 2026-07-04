import math

import pandas as pd
import pytest

from src.analytics.drawdown import calculate_drawdown
from src.analytics.metrics import calculate_performance_metrics


def test_total_return_and_equity_math_are_consistent() -> None:
    returns = pd.Series([0.0, 0.10, -0.05], dtype=float)
    equity = pd.Series([100.0, 110.0, 104.5], dtype=float)

    metrics = calculate_performance_metrics(returns=returns, equity_curve=equity, trade_count=2)

    assert pytest.approx(metrics.total_return, rel=1e-9) == 0.045


def test_max_drawdown_matches_known_curve() -> None:
    equity = pd.Series([100.0, 120.0, 90.0, 95.0], dtype=float)

    drawdown = calculate_drawdown(equity)
    metrics = calculate_performance_metrics(
        returns=pd.Series([0.0, 0.2, -0.25, 0.0555555556], dtype=float),
        equity_curve=equity,
        trade_count=1,
    )

    assert pytest.approx(drawdown.min(), rel=1e-9) == -0.25
    assert pytest.approx(metrics.max_drawdown, rel=1e-9) == -0.25


def test_cagr_and_volatility_on_deterministic_series() -> None:
    annualization_factor = 252
    returns = pd.Series([0.01] * annualization_factor, dtype=float)
    index = pd.bdate_range("2024-01-02", periods=annualization_factor)
    equity = pd.Series((100.0 * (1.0 + returns).cumprod()).to_numpy(), index=index)

    metrics = calculate_performance_metrics(
        returns=returns,
        equity_curve=equity,
        trade_count=1,
        annualization_factor=annualization_factor,
    )

    elapsed_years = (equity.index[-1] - equity.index[0]).days / 365.25
    expected_cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / elapsed_years) - 1.0)
    assert pytest.approx(metrics.cagr, rel=1e-9) == expected_cagr
    assert pytest.approx(metrics.annualized_volatility, abs=1e-12) == 0.0


def test_sharpe_is_zero_when_volatility_is_zero() -> None:
    returns = pd.Series([0.01, 0.01, 0.01], dtype=float)
    equity = pd.Series([100.0, 101.0, 102.01], dtype=float)

    metrics = calculate_performance_metrics(returns=returns, equity_curve=equity, trade_count=0)

    assert metrics.sharpe_ratio == 0.0


def test_degenerate_series_returns_zero_for_undefined_metrics() -> None:
    returns = pd.Series([0.0], dtype=float)
    equity = pd.Series([100.0], dtype=float)

    metrics = calculate_performance_metrics(returns=returns, equity_curve=equity, trade_count=0)

    assert metrics.cagr == 0.0
    assert metrics.annualized_volatility == 0.0
    assert metrics.sharpe_ratio == 0.0
    assert metrics.max_drawdown == 0.0
    assert metrics.trade_count == 0
