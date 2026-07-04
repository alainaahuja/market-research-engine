# Market Research Engine

Quant strategy workbench focused on single-ticker research, backtesting, and strategy comparison.

## What the app does

- Lets a user enter a stock ticker, date range, initial capital, fee rate, and a set of built-in strategies
- Downloads historical daily price data from Yahoo Finance using `yfinance`
- Generates strategy signals internally for:
  - Buy and Hold
  - Moving Average Crossover
  - RSI
  - Momentum
- Runs the backtest engine for each selected strategy
- Compares results in a Streamlit UI with:
  - price history
  - strategy metrics
  - equity curves
  - drawdown charts
  - a closed-trade log for one selected strategy at a time

## How it works

1. The user fills in the sidebar form and clicks `Run Backtest`.
2. The app fetches and caches adjusted closing-price history for the ticker and date range.
3. Each selected strategy generates raw daily signals from the downloaded price data.
4. The backtest engine shifts those signals forward by one bar before applying them, to avoid look-ahead bias.
5. The app computes per-strategy metrics and displays the results side by side.

## Current metrics

- Total return
- CAGR
- Annualized volatility
- Sharpe ratio
- Max drawdown
- Trade count

## Core assumptions

- Daily bars only
- Long-only strategies
- Single ticker per run
- Close-to-close return modeling
- No slippage model
- Fees are a simple proportional cost applied on position changes
- Open positions at the end of the sample are not counted as closed trades

## Structure

```text
app/
  streamlit_app.py
src/
  analytics/
  backtest/
  data/
  services/
  strategies/
  ui/
tests/
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app/streamlit_app.py
```

## Inputs

- Stock ticker
- Start date
- End date
- Initial capital
- Fee rate
- Strategy selection

## Important limitations

These are known v1 limitations and should be understood before trusting results too strongly.

### 1. Short date ranges can still produce misleading metrics

The app now blocks date ranges that are too short for the selected strategies' basic lookback windows, but that is only a partial guardrail.

- A range may still be long enough to pass strategy warm-up checks while being too short to support trustworthy annualized metrics.
- This is especially relevant for CAGR, volatility, and Sharpe ratio on short samples.
- Example: a strategy can technically run over a short period and still produce annualized metrics that look precise but are not robust.

### 2. The app does not validate that the dataset is large enough for "good" metrics

The app validates minimum strategy history, not statistical reliability.

- It does not currently warn when the sample size is too small for stable performance interpretation.
- A passing backtest is not the same thing as a reliable backtest.

### 3. Trade count and trade log exclude open positions

Only closed trades are included in the trade log and in `trade_count`.

- A strategy can end the backtest with an open position and still show `Trade Count = 0`.
- This is most noticeable for Buy and Hold or any strategy that enters and never exits before the sample ends.
- The UI does not currently explain this clearly enough.

### 4. Strategy comparisons can still encourage overconfidence

Even with the current safeguards:

- the built-in strategies use fixed parameters
- results are shown side by side without confidence intervals or robustness checks
- no out-of-sample validation is performed

The output should be treated as exploratory research, not decision-grade evidence.

### 5. Market data quality depends on Yahoo Finance

- The app relies on Yahoo Finance data availability and formatting.
- Missing or unusual data can still affect results.
- This app does not currently cross-check downloaded data against another source.

## Notes

- Historical prices are fetched from Yahoo Finance through `yfinance`
- Downloaded data is cached by ticker and date range to avoid unnecessary redownloads
- Signals are generated inside the app for the built-in strategies
- Strategy signals are shifted forward one bar inside the core engine to prevent look-ahead bias
- CAGR is based on elapsed calendar time rather than raw row count, which reduces distortion from weekends and holidays
