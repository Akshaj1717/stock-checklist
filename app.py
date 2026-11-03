import streamlit as st
import yfinance as yf
from checks import TESTS
from backtest import run_200dma_backtest

st.set_page_config(page_title="Stock Checklist", page_icon="📊")
st.title("📊 Stock & ETF Checklist")
st.caption("An analysis tool, not financial advice.")

@st.cache_data(ttl=3600)
def load(symbol):
    t = yf.Ticker(symbol)
    return t.info, t.history(period="1y")

@st.cache_data(ttl=3600)
def load_long_history(symbol):
    return yf.Ticker(symbol).history(period="10y")["Close"]

symbol = st.text_input("Ticker", placeholder="e.g. VOO").strip().upper()

if symbol:
    info, hist = load(symbol)

    tab1, tab2 = st.tabs(["Checklist", "Backtest"])
    with tab1:
        if hist.empty:
            st.error(f"No data found for {symbol}. Check the symbol.")
            st.stop()

        st.subheader(info.get("longName", symbol))
        st.line_chart(hist["Close"])

        icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
        results = []
        for name, test in TESTS.items():
            status, detail = test(info, hist)
            results.append((name, status, detail))

        scored = [status for name, status, detail in results if status != "n/a"]
        passed = scored.count("pass")

        st.subheader(f"Checklist: {passed}/{len(scored)} passed")
        c1, c2 ,c3 = st.columns(3)
        c1.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")
        c2.metric("52-week high", f"${hist['Close'].tail(252).max():.2f}")
        c3.metric("52-week low", f"${hist['Close'].tail(252).min():.2f}")
        if scored:
            st.progress(passed / len(scored))

        icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
        for name, status, detail in results:
            st.write(f"{icons[status]} **{name}**: {detail.replace('$', '\\$')}")  

    with tab2:
        st.write("**Rule:** only own it while the price is above its 200-day average; otherwise hold cash.")

        close_10y = load_long_history(symbol)
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
        st.write(f"Buy & hold ended with \\${stats.loc['Buy & hold', 'Final value']:.0f}, while the 200DMA strategy ended with \\${stats.loc['200-day rule', 'Final value']:.0f}.")


    