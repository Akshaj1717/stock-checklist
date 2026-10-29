import streamlit as st
import yfinance as yf
from checks import TESTS

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
    st.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")
    st.line_chart(hist["Close"])

    icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
    for name, test in TESTS.items():
        status, detail = test(info, hist)
        st.write(f"{icons[status]} **{name}**: {detail}")
