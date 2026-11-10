import streamlit as st
import yfinance as yf
from checks import TESTS
from backtest import annualized_returns, run_200dma_backtest, compare_to_benchmark
import pandas as pd

BENCHMARKS = {
    "VOO": "S&P 500: the 500 biggest US companies",
    "VTI": "Total US stock market",
    "QQQ": "Nasdaq 100: mostly large tech",
    "VXUS": "International stocks (outside the US)",
    "BND": "US bonds: the steadier, lower-return option",
}

st.set_page_config(page_title="Stock Checklist", page_icon="📊")
st.title("📊 Stock & ETF Checklist")
st.caption("An analysis tool, not financial advice.")

@st.cache_data(ttl=3600)
def load_full_history(symbol):
    return yf.Ticker(symbol).history(period="max")["Close"]


def last_n_years(close, years):
    return close.loc[close.index[-1] - pd.DateOffset(years=years):]

@st.cache_data(ttl=3600)
def load(symbol):
    t = yf.Ticker(symbol)
    return t.info, t.history(period="1y")

col_t, col_b = st.columns([1, 2])
symbol = col_t.text_input("Ticker", placeholder="e.g. AAPL").strip().upper()
bench = col_b.selectbox(
    "Compare against",
    options=list(BENCHMARKS),
    format_func=lambda t: f"{t}: {BENCHMARKS[t]}",
)

if symbol:
    info, hist = load(symbol)
    if hist.empty:
        st.error(f"No data found for {symbol}. Check the symbol.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["Checklist", "Returns", "Backtest"])
    with tab1:
        st.subheader(info.get("longName", symbol))
        st.line_chart(hist["Close"])

        icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
        results = []
        for name, test in TESTS.items():
            status, detail = test(info, hist)
            results.append((name, status, detail))

        for name, status, detail in results:
            st.write(f"{icons[status]} **{name}**: {detail.replace('$', '\\$')}")  

        scored = [status for name, status, detail in results if status != "n/a"]
        passed = scored.count("pass")

        st.subheader(f"Checklist: {passed}/{len(scored)} passed")
        c1, c2 ,c3 = st.columns(3)
        c1.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")
        c2.metric("52-week high", f"${hist['Close'].tail(252).max():.2f}")
        c3.metric("52-week low", f"${hist['Close'].tail(252).min():.2f}")
        if scored:
            st.progress(passed / len(scored))

    with tab2:
        full = load_full_history(symbol)
        bench_full = load_full_history(bench)

        if symbol == bench:
            st.caption("This is the benchmark, so the comparison is trivial.")

        table = pd.DataFrame({
            symbol: annualized_returns(full),
            bench: annualized_returns(bench_full),
        })
        table["Difference"] = table[symbol] - table[bench]
        st.dataframe(
            table.style
                .format("{:+.1%}", na_rep="—")
                .map(lambda v: "color: green" if v > 0 else "color: red" if v < 0 else "",
                    subset=["Difference"]))

        valid = table["Difference"].notna()
        wins = (table["Difference"][valid] > 0).sum()
        total = valid.sum()
        if symbol != bench and total:
            verb = "beat" if wins > total / 2 else "trailed"
            st.info(f"{symbol} {verb} {bench} in {wins if verb == 'beat' else total - wins} "
                    f"of {total} periods shown.")

    with tab3:
        st.write("**Rule:** only own it while the price is above its 200-day average; otherwise hold cash.")

        close_10y = last_n_years(load_full_history(symbol), 10)
        curves, stats = run_200dma_backtest(close_10y)

        if len(close_10y) < 400:
            st.warning("The backtest may be unreliable due to insufficient data (less than 400 trading days).")

        st.line_chart(curves)

        st.dataframe(stats.style.format({
            "Final value": "${:,.0f}",
            "Total return": "{:.1%}",
            "Max drawdown": "{:.1%}",
            "Days invested": "{:.0%}",
        }, na_rep="—"))

        bh = stats.loc["Buy & hold"]
        rule = stats.loc["200-day rule"]
        value_gap = bh["Final value"] - rule["Final value"]
        dd_gap = (rule["Max drawdown"] - bh["Max drawdown"]) * 100  # in points
        years = (curves.index[-1] - curves.index[0]).days / 365.25
        st.caption(f"Period: {curves.index[0]:%b %Y} – {curves.index[-1]:%b %Y} ({years:.1f} years)")

        if value_gap > 0:
            st.info(f"Buy & hold ended with **\\${value_gap:,.0f} more**. "
                    f"The 200-day rule's worst drop was **{dd_gap:.1f} points smaller**. "
                    f"The rule traded returns for a smoother ride.")
        else:
            st.info(f"The 200-day rule ended with **\\${-value_gap:,.0f} more** "
                    f"and a worst drop {dd_gap:.1f} points smaller than buy & hold.")
        
        st.divider()
        st.subheader(f"vs. just buying {bench}")

        if symbol == bench:
            st.caption("This is the benchmark, so the comparison is trivial.")
        else:
            bench_close = last_n_years(load_full_history(bench), 10)
            cmp_curves, cmp_stats = compare_to_benchmark(close_10y, bench_close)
            cmp_curves = cmp_curves.rename(columns={"This ticker": symbol, "Benchmark": bench})
            cmp_stats = cmp_stats.rename(index={"This ticker": symbol, "Benchmark": bench})
            cmp_years = (cmp_curves.index[-1] - cmp_curves.index[0]).days / 365.25
            dd_diff = (cmp_stats.loc[symbol, "Max drawdown"] - cmp_stats.loc[bench, "Max drawdown"]) * 100
            dd_word = "deeper" if dd_diff < 0 else "shallower"
            st.info(f"{symbol}'s worst drop was {abs(dd_diff):.1f} points {dd_word} than {bench}'s.")

            st.line_chart(cmp_curves)
            st.dataframe(cmp_stats.style.format({
                "Final value": "${:,.0f}",
                "Total return": "{:.1%}",
                "Max drawdown": "{:.1%}",
            }))

            st.caption(f"Period: {cmp_curves.index[0]:%b %Y} – {cmp_curves.index[-1]:%b %Y} ({cmp_years:.1f} years)")
            if cmp_stats.loc[symbol, "Final value"] > cmp_stats.loc[bench, "Final value"]:
                st.info(f"{symbol} outperformed {bench} by **\\${cmp_stats.loc[symbol, 'Final value'] - cmp_stats.loc[bench, 'Final value']:,.0f}** over the period.")
            else:
                st.info(f"{symbol} underperformed {bench} by **\\${cmp_stats.loc[bench, 'Final value'] - cmp_stats.loc[symbol, 'Final value']:,.0f}** over the period.")

    