import streamlit as st
import yfinance as yf
from main import TESTS

st.set_page_config(page_title="Stock Checklist", page_icon="📊")
st.title("📊 Stock & ETF Checklist")
st.caption("An analysis tool, not financial advice.")

@st.cache_data(ttl=3600)
def load(symbol):
    t = yf.Ticker(symbol)
    return t.info, t.history(period="1y")


symbol = st.text_input("Ticker", placeholder="e.g. VOO").strip().upper()

if symbol:
    info, hist = load(symbol)

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
    if scored:
        st.progress(passed / len(scored))

    icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
    for name, status, detail in results:
        st.write(f"{icons[status]} **{name}**: {detail}")   

c1, c2 ,c3 = st.columns(3)
c1.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")
c2.metric("52-week high", f"${hist['Close'].tail(252).max():.2f}")
c3.metric("52-week low", f"${hist['Close'].tail(252).min():.2f}")