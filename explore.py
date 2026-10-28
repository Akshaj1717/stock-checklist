import yfinance as yf

ticker = yf.Ticker("VOO")
info = ticker.info               # dict of company stats
hist = ticker.history(period="1y")  # pandas DataFrame of daily prices

print(info.get("longName"))
print("Type:", info.get("quoteType"))      # "EQUITY" or "ETF"
print("P/E:", info.get("trailingPE"))
print("Debt/Equity:", info.get("debtToEquity"))
print("Profit margin:", info.get("profitMargins"))

print(hist.tail())               # last 5 days of prices
print("Latest close:", hist["Close"].iloc[-1])