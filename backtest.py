import yfinance as yf

symbol = "VOO"
hist = yf.Ticker(symbol).history(period="10y")
close = hist["Close"]

daily_return = close.pct_change() # how much price moved each day

ma_200 = close.rolling(200).mean() # 200 day moving average 
signal = close > ma_200 # if price is above 200 day moving average, signal is True

position = signal.shift(1).fillna(False) # shift signal by 1 day to avoid lookahead bias

strategy_return = daily_return.where(position, 0) # if position is True, use daily return, else 0

buy_hold = (1 + daily_return.fillna(0)).cumprod() # cumulative return of buy and hold strategy
strategy = (1 + strategy_return.fillna(0)).cumprod() # cumulative return of

print(f"{symbol}, last 10 years, $10,000 invested:")
print(f"  Buy and hold:      ${buy_hold.iloc[-1] * 10_000:,.0f}")
print(f"  200-day strategy:  ${strategy.iloc[-1] * 10_000:,.0f}")
print(f"  Days invested:     {position.mean():.0%}")