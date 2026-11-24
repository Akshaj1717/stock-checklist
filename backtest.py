import pandas as pd
import numpy as np


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
    curves = (1 + returns).cumprod() * starting

    stats = pd.DataFrame({
        "Final value": curves.iloc[-1],
        "Total return": curves.iloc[-1] / starting - 1,
        "Max drawdown": curves.apply(max_drawdown),
    })
    return curves, stats

def annualized_returns(close, periods=(1, 3, 5, 10)):
    """Average yearly return over the last N years, none if not enough data."""
    close = close.dropna()
    end_date, end_price = close.index[-1], close.iloc[-1]
    out = {}
    for years in periods:
        cutoff = end_date - pd.DateOffset(years=years)
        if close.index[0] > cutoff: # ticker doesn't have enough history
            out[f"{years}Y"] = None
            continue
        start_price = close.loc[cutoff:].iloc[0] # first trade on or after cutoff
        out[f"{years}Y"] = (end_price / start_price) ** (1 / years) - 1
    return pd.Series(out, dtype="float64")

def historical_outcomes(close, initial=2000, monthly=0, years=5):
    """For every past starting month, what the plan would have grown to.
    Returns a Series: index = start month, value = ending balance."""
    prices = close.resample("ME").last().dropna()
    n = years * 12

    start_price = prices
    end_price = prices.shift(-n)

    # sum of 1/price over the n months of contribution, aligned to the start month
    inv_sum = (1 / prices).rolling(n).sum().shift(-n + 1)

    final = end_price * (initial / start_price + monthly * inv_sum)
    return final.dropna()

def simulate_outcomes(close, initial=2000, monthly= 0, years=5,
                      n_sims=5000, block=12, seed=42):
     """Bootstrap: build n_sims possible futures by stitching together random
    `block`-month chunks of real past monthly returns. Returns ending balances."""
     prices = close.resample("ME").last().dropna()
     r = prices.pct_change().dropna().to_numpy()
     n = years * 12
     if len(r) < block * 2:
         return np.array([])  # not enough history to stitch together even two blocks

     rng = np.random.default_rng(seed)
     n_blocks = -(-n // block) # ceiling division
     starts = rng.integers(0, len(r) - block + 1, size=(n_sims, n_blocks))
     idx = (starts[:, :, None] + np.arange(block)).reshape(n_sims, -1)[:, :n]  # truncate to n months
     R = r[idx]

     growth = np.cumprod(1 + R, axis=1) # value of $1 invested at the start of each simulation
     g_end = growth[:, -1] # final growth factor for each simulation
     g_before = np.hstack([np.ones((n_sims, 1)), growth[:, :-1]]) # growth factor before each month
     # each deposit at month k grows by g_end / g_before[k]
     return g_end * (initial + monthly * (1 / g_before).sum(axis=1))

if __name__ == "__main__":
    import yfinance as yf
    close = yf.Ticker("VOO").history(period="10y")["Close"]
    curves, stats = run_200dma_backtest(close)
    print(stats)