from __future__ import annotations

from functools import lru_cache
from datetime import date, timedelta

import pandas as pd


def fetch_price_history(
    ticker: str,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if not ticker.strip():
        raise ValueError("Ticker is required.")
    if start_date > end_date:
        raise ValueError("Start date must be on or before end date.")

    normalized = _download_price_history_cached(
        ticker.strip().upper(),
        start_date.isoformat(),
        (end_date + timedelta(days=1)).isoformat(),
    )
    if normalized.empty:
        raise ValueError(f"No usable closing-price data found for ticker '{ticker.strip().upper()}'.")
    return normalized.copy()


@lru_cache(maxsize=128)
def _download_price_history_cached(
    ticker: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as error:
        raise RuntimeError(
            "yfinance is required to fetch market data. Install dependencies from requirements.txt."
        ) from error

    history = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )
    if history.empty:
        raise ValueError(f"No historical data found for ticker '{ticker}'.")

    return _normalize_history(history)


def _normalize_history(history: pd.DataFrame) -> pd.DataFrame:
    normalized = history.copy()
    if isinstance(normalized.columns, pd.MultiIndex):
        normalized.columns = normalized.columns.get_level_values(0)

    if "Close" not in normalized.columns:
        raise ValueError("Downloaded price data is missing a 'Close' column.")

    price_data = normalized[["Close"]].copy()
    price_data.index = pd.to_datetime(price_data.index).tz_localize(None)
    price_data.index.name = "Date"
    price_data["Close"] = pd.to_numeric(price_data["Close"], errors="coerce")
    return price_data.dropna(subset=["Close"]).sort_index()
