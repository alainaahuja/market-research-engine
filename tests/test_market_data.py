from __future__ import annotations

import sys
from types import SimpleNamespace

import pandas as pd

from src.data import market_data


def test_fetch_price_history_caches_by_ticker_and_date_range(monkeypatch) -> None:
    call_count = {"count": 0}

    def fake_download(*args, **kwargs) -> pd.DataFrame:
        call_count["count"] += 1
        dates = pd.date_range("2024-01-01", periods=3, freq="D")
        return pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=dates)

    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=fake_download))
    market_data._download_price_history_cached.cache_clear()

    first = market_data.fetch_price_history(
        ticker="AAPL",
        start_date=pd.Timestamp("2024-01-01").date(),
        end_date=pd.Timestamp("2024-01-03").date(),
    )
    second = market_data.fetch_price_history(
        ticker="AAPL",
        start_date=pd.Timestamp("2024-01-01").date(),
        end_date=pd.Timestamp("2024-01-03").date(),
    )

    assert call_count["count"] == 1
    assert first.equals(second)
    assert first is not second
