def near_52_week_high(info, hist):
    """Pass if price is in the top 25% of its 52-week range."""
    if hist is None or len(hist) < 200:
        return "n/a", "Not enough price history"

    last_year = hist["Close"].tail(252) # last 252 trading days
    low, high = last_year.min(), last_year.max()
    price = last_year.iloc[-1]

    position = (price - low) / (high - low)
    status = "pass" if position >= 0.75 else "fail"
    return status, f"Price is {position:.0%} of the way from 52-week low (${low:.2f}) to high (${high:.2f})"

def positive_1y_return(info, hist):
    """Pass if the price is higher than one year ago."""
    if hist is None or len(hist) < 200:
        return "n/a", "Not enough price history"

    change = hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1
    status = "pass" if change > 0 else "fail"
    return status, f"1-year price change: {change:.1%}"

def above_200_day_average(info, hist):
    """Pass if the price is above the 200-day moving average."""
    if hist is None or len(hist) < 200:
        return "n/a", "Not enough price history"

    avg_200 = hist["Close"].tail(200).mean()
    price = hist["Close"].iloc[-1]
    status = "pass" if price > avg_200 else "fail"
    return status, f"Price (${price:.2f}) is {'above' if status == 'pass' else 'below'} the 200-day average (${avg_200:.2f})"