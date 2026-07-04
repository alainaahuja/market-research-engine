from __future__ import annotations

import streamlit as st

from bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from src.ui.workbench import (
    available_strategy_options,
    build_drawdown_chart_data,
    build_equity_chart_data,
    build_metrics_comparison_table,
    build_price_history_chart_data,
    build_trade_log_table,
    default_end_date,
    default_start_date,
    run_workbench,
    select_strategy_result,
    strategy_labels,
)


st.set_page_config(page_title="Quant Strategy Workbench", layout="wide")
st.title("Quant Strategy Workbench")
st.caption("Compare simple long-only backtests across a small set of built-in strategies.")

if "comparison" not in st.session_state:
    st.session_state.comparison = None
if "run_error" not in st.session_state:
    st.session_state.run_error = None


with st.sidebar.form("backtest_inputs"):
    st.header("Backtest Inputs")
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
    start_date = st.date_input("Start date", value=default_start_date())
    end_date = st.date_input("End date", value=default_end_date())
    initial_capital = st.number_input(
        "Initial capital",
        min_value=1_000.0,
        value=10_000.0,
        step=1_000.0,
    )
    fee_rate = st.number_input(
        "Fee rate",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.001,
        format="%.4f",
        help="Proportional fee applied each time the position changes.",
    )
    labels = strategy_labels()
    strategy_keys = st.multiselect(
        "Strategies",
        options=available_strategy_options(),
        default=available_strategy_options(),
        format_func=lambda key: labels[key],
    )
    run_clicked = st.form_submit_button(
        "Run Backtest", type="primary", use_container_width=True
    )


if run_clicked:
    try:
        st.session_state.comparison = run_workbench(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            fee_rate=fee_rate,
            strategy_keys=strategy_keys,
        )
        st.session_state.run_error = None
    except (RuntimeError, ValueError) as error:
        st.session_state.comparison = None
        st.session_state.run_error = str(error)

if st.session_state.run_error:
    st.error(st.session_state.run_error)
elif st.session_state.comparison is None:
    st.info("Enter a ticker and date range, then run the strategy comparison.")
else:
    comparison = st.session_state.comparison
    st.subheader("Price History")
    st.line_chart(build_price_history_chart_data(comparison))

    st.subheader("Strategy Metrics")
    st.dataframe(
        build_metrics_comparison_table(comparison),
        hide_index=True,
        use_container_width=True,
    )

    equity_col, drawdown_col = st.columns(2)
    with equity_col:
        st.subheader("Equity Curves")
        st.line_chart(build_equity_chart_data(comparison))
    with drawdown_col:
        st.subheader("Drawdowns")
        st.line_chart(build_drawdown_chart_data(comparison))

    strategy_names = [
        strategy_result.strategy.display_name
        for strategy_result in comparison.strategy_results
    ]
    selected_strategy_name = st.selectbox(
        "Trade Log Strategy",
        options=strategy_names,
    )
    selected_strategy = select_strategy_result(comparison, selected_strategy_name)

    st.subheader(f"Closed Trades: {selected_strategy_name}")
    trade_log_table = build_trade_log_table(selected_strategy)
    if trade_log_table.empty:
        st.write("No closed trades were generated for this strategy.")
    else:
        st.dataframe(trade_log_table, hide_index=True, use_container_width=True)
