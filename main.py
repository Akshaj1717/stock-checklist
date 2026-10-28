import yfinance as yf
from checks import near_52_week_high, positive_1y_return, above_200_day_average

TESTS = {
    "Near 52-week high": near_52_week_high,
    "Positive 1-year return": positive_1y_return,
    "Above 200-day average": above_200_day_average,
}

symbol = ["VOO", "QQQ", "AAPL"]
for s in symbol:
    ticker = yf.Ticker(s)
    info = ticker.info
    hist = ticker.history(period="1y")


icons = {"pass": "✅", "fail": "❌", "n/a": "➖"}
for name, test in TESTS.items():
    status, detail = test(info, hist)
    print(f"{icons[status]} {name}: {detail}")