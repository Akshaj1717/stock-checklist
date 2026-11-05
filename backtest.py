import pandas as pd


def max_drawdown(curve):
    """Worst drop from a previous peak, e.g. -0.34 for -34%."""
    return (curve / curve.cummax() - 1).min()


def run_200dma_backtest(close, starting=10_000):
    """Compare holding vs. only holding while above the 200-day average.
    Takes a Series of closing prices, returns (curves, stats)."""
    daily_return = close.pct_change().fillna(0)

    ma_200 = close.rolling(200).mean()
    signal = close > ma_200
    position = signal.shift(1, fill_value=False)

    # Start both strategies once the 200-day average exists
    start = ma_200.first_valid_index()
    daily_return = daily_return.loc[start:]
    position = position.loc[start:]

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
    stats.loc["Buy & hold", "Days invested"] = 1.0

    return curves, stats

def compare_to_benchmark(close, bench_close, starting=10_000):
    # Buy & hold this ticker vs. buy & hold the benchmark, over shared dates.
    prices = pd.concat({"This ticker": close, "Benchmark": bench_close}, axis=1).dropna()

    returns = prices.pct_change().fillna(0)
    cruves = (1 + returns).cumprod() * starting

    stats = pd.DataFrame({
        "Final value": curves.iloc[-1],
        "Total return": curves.iloc[-1] / starting - 1,
        "Max drawdown": curves.apply(max_drawdown),
    })
    return curves, stats


if __name__ == "__main__":
    import yfinance as yf
    close = yf.Ticker("VOO").history(period="10y")["Close"]
    curves, stats = run_200dma_backtest(close)
    print(stats)