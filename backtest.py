import pandas as pd


def max_drawdown(curve):
    """Worst drop from a previous peak, e.g. -0.34 for -34%."""
    return (curve / curve.cummax() - 1).min()


def run_200dma_backtest(close, starting=10_000):
    """Compare holding vs. only holding while above the 200-day average.
    Takes a Series of closing prices, returns (curves, stats)."""
    daily_return = close.pct_change().fillna(0)

    signal = close > close.rolling(200).mean()
    position = signal.shift(1, fill_value=False)

    strategy_return = daily_return.where(position, 0)

    curves = pd.DataFrame({
        "Buy & hold": (1 + daily_return).cumprod() * starting,
        "200-day rule": (1 + strategy_return).cumprod() * starting,
    })

    stats = pd.DataFrame({
        "Final value": curves.iloc[-1],
        "Total return": curves.iloc[-1] / starting - 1,
        "Max drawdown": curves.apply(max_drawdown),
    })
    stats.loc["200-day rule", "Days invested"] = position.mean()

    return curves, stats


if __name__ == "__main__":
    import yfinance as yf
    close = yf.Ticker("VOO").history(period="10y")["Close"]
    curves, stats = run_200dma_backtest(close)
    print(stats)