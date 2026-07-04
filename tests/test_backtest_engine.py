import pandas as pd
import pytest

from src.backtest.engine import run_backtest
from src.models import BacktestInput


def _price_data(closes: list[float]) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    return pd.DataFrame({"Close": closes}, index=dates)


def test_signals_are_shifted_to_prevent_lookahead_bias() -> None:
    prices = _price_data([100.0, 110.0, 121.0])
    signals = pd.Series([0, 1, 1], index=prices.index, dtype=float)

    result = run_backtest(BacktestInput(price_data=prices, signals=signals))

    assert result.positions.tolist() == [0.0, 0.0, 1.0]
    assert result.returns.tolist() == pytest.approx([0.0, 0.0, 0.1], rel=1e-9)


def test_first_row_is_always_flat_after_signal_shift() -> None:
    prices = _price_data([100.0, 105.0, 110.0])
    signals = pd.Series([1, 1, 1], index=prices.index, dtype=float)

    result = run_backtest(BacktestInput(price_data=prices, signals=signals))

    assert result.positions.iloc[0] == 0.0


def test_always_flat_strategy_keeps_equity_constant() -> None:
    prices = _price_data([100.0, 102.0, 104.0, 106.0])
    signals = pd.Series([0, 0, 0, 0], index=prices.index, dtype=float)

    result = run_backtest(BacktestInput(price_data=prices, signals=signals))

    assert result.equity_curve.tolist() == [10000.0, 10000.0, 10000.0, 10000.0]
    assert result.metrics.trade_count == 0


def test_always_long_matches_buy_and_hold_after_initial_shift() -> None:
    prices = _price_data([100.0, 110.0, 121.0, 133.1])
    signals = pd.Series([1, 1, 1, 1], index=prices.index, dtype=float)

    result = run_backtest(BacktestInput(price_data=prices, signals=signals))

    assert result.positions.tolist() == [0.0, 1.0, 1.0, 1.0]
    assert pytest.approx(result.equity_curve.iloc[-1], rel=1e-9) == 13310.0


def test_fees_are_charged_once_per_position_change() -> None:
    prices = _price_data([100.0, 100.0, 100.0, 100.0])
    signals = pd.Series([0, 1, 0, 0], index=prices.index, dtype=float)

    result = run_backtest(
        BacktestInput(price_data=prices, signals=signals, initial_capital=1000.0, fee_rate=0.01)
    )

    assert result.positions.tolist() == [0.0, 0.0, 1.0, 0.0]
    assert result.returns.tolist() == [0.0, 0.0, -0.01, -0.01]
    assert pytest.approx(result.equity_curve.iloc[-1], rel=1e-9) == 980.1


def test_closed_trade_is_recorded_and_open_trade_is_ignored() -> None:
    prices = _price_data([100.0, 100.0, 110.0, 120.0, 115.0])
    signals = pd.Series([0, 1, 0, 1, 1], index=prices.index, dtype=float)

    result = run_backtest(BacktestInput(price_data=prices, signals=signals))

    assert len(result.trade_log) == 1
    trade = result.trade_log[0]
    assert trade.entry_date == prices.index[2]
    assert trade.exit_date == prices.index[3]
    assert trade.entry_price == 110.0
    assert trade.exit_price == 120.0
    assert pytest.approx(trade.return_pct, rel=1e-9) == (120.0 / 110.0) - 1.0


def test_missing_close_column_raises_validation_error() -> None:
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    prices = pd.DataFrame({"Open": [1.0, 2.0, 3.0]}, index=dates)
    signals = pd.Series([0, 0, 0], index=dates, dtype=float)

    with pytest.raises(ValueError, match="Close"):
        run_backtest(BacktestInput(price_data=prices, signals=signals))


def test_mismatched_signal_index_raises_validation_error() -> None:
    prices = _price_data([100.0, 101.0, 102.0])
    other_index = pd.date_range("2024-02-01", periods=3, freq="D")
    signals = pd.Series([0, 1, 1], index=other_index, dtype=float)

    with pytest.raises(ValueError, match="exactly match"):
        run_backtest(BacktestInput(price_data=prices, signals=signals))


def test_unsorted_index_raises_validation_error() -> None:
    dates = pd.to_datetime(["2024-01-02", "2024-01-01", "2024-01-03"])
    prices = pd.DataFrame({"Close": [101.0, 100.0, 102.0]}, index=dates)
    signals = pd.Series([0, 1, 1], index=dates, dtype=float)

    with pytest.raises(ValueError, match="sorted"):
        run_backtest(BacktestInput(price_data=prices, signals=signals))


def test_fee_rate_above_one_raises_validation_error() -> None:
    prices = _price_data([100.0, 101.0, 102.0])
    signals = pd.Series([0, 1, 1], index=prices.index, dtype=float)

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        run_backtest(
            BacktestInput(
                price_data=prices,
                signals=signals,
                fee_rate=1.01,
            )
        )
