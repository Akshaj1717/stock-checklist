# 📊 Stock & ETF Checklist

**Live app:** https://stock-checklist-akshaj.streamlit.app/

Most beginner investors buy on hype and sell in a panic. This tool helps you invest with evidence instead. Enter any stock or ETF to check it against simple rules, see how it compares with an index fund, and see the realistic range of outcomes for your own investing plan, including how often a plan like yours has lost money.

![screenshot](screenshot.png)

## Features

**Checklist**
- Pass/fail results on price-based tests, each with the data behind it
- A score, plus the current price and the 52-week high and low

**Returns**
- **Choose a benchmark:** S&P 500 (VOO), total US market (VTI), Nasdaq 100 (QQQ), international stocks (VXUS), or bonds (BND)
- **Average yearly return** over 1, 3, 5, and 10 years compared with the benchmark, with a plain-English summary of how many periods the ticker won
- **What could your money become?** Enter a starting amount, a monthly contribution, and a number of years:
  - **Replay:** your plan run from every past starting month, showing the worst, typical, and best result and how often you would have lost money
  - **Simulated futures:** 5,000 possible outcomes built from the ticker's real past returns, showing bad, typical, and good cases and the chance of losing money
- **Long-history stand-ins:** young funds are extended back in time with an older fund that tracks the same index (for example, VOO with SPY back to 1993), so results include the dot-com crash and 2008

**Backtest**
- **200-day moving average rule** compared with buy and hold
- **Benchmark comparison:** the ticker compared with the chosen benchmark over shared dates
- Final value, total return, max drawdown, and a plain-English takeaway

## Findings

**Time in the market lowers the chance of losing money**

$2,000 invested in VOO with no monthly contributions, replayed from every starting month since 2010:

| Holding period | Worst | Typical | Best | Lost money |
|---|---:|---:|---:|---:|
| 1 year | $1,637 | $2,319 | $3,129 | 10% of periods |
| 10 years | $5,720 | $7,142 | $9,223 | 0% of periods |

**A strong decade can make history look safer than it is.** VOO only exists from 2010 onward, one of the best stretches in US market history, so its replay found no losing 10-year periods. Simulating futures from the same history with the years reshuffled gave a small but real chance of loss. Adding SPY's history from 1993 brings in the 2000s "lost decade":

> TODO: after deploying, add VOO 10-year results with long history: replay lost-money %, simulated lost-money %, worst case.

**The 200-day rule rarely beats holding**

| Ticker | Buy & hold | 200-day rule | Buy & hold max drawdown | 200-day rule max drawdown |
|--------|-----------:|-------------:|------------------------:|--------------------------:|
| VOO    | $36,658    | $27,128      | -34.0%                  | -19.6%                    |
| AAPL   | $92,794    | $43,394      | -38.5%                  | -35.3%                    |
| INTC   | $18,672    | $16,296      | -70.8%                  | -65.8%                    |

*$10,000 invested, Aug 2017 to Nov 2026.*

On the index fund, the rule gave up about a quarter of the final value but cut the worst drop by 14 points. On individual stocks, it lost most of the upside and barely reduced the drawdown.

**Picking individual stocks: a big win or a big loss**

| Ticker | Final value | VOO final value | Max drawdown | VOO max drawdown |
|--------|------------:|----------------:|-------------:|-----------------:|
| AAPL   | $135,958    | $40,818         | -38.5%       | -34.0%           |
| INTC   | $19,066     | $40,818         | -70.8%       | -34.0%           |

*$10,000 invested, Nov 2016 to Nov 2026.*

AAPL beat the index by about $95,000. INTC trailed it by about $21,750 and fell 71% at its worst.

**Watch out for survivorship bias:** backtesting a company you already know succeeded always looks good. An investor in 2016 could not have known whether AAPL or INTC would be the winner.

## Methodology

- **No look-ahead bias:** signals are computed from the day's close and acted on the next day (`shift(1)`).
- **Fair warm-up:** both backtest strategies start on the first day a 200-day average exists.
- **Date alignment:** benchmark comparisons use only the dates both tickers traded.
- **Annualized returns (CAGR):** `(end / start) ** (1 / years) - 1`, so compounding is accounted for. Periods longer than a ticker's history show "—".
- **Replay:** monthly prices. Each deposit buys shares at that month's price, and the ending value is total shares × ending price. All starting months are computed at once with rolling sums. Windows overlap, so 75 windows are not 75 independent results.
- **Block bootstrap simulation:** 5,000 paths built from random 12-month chunks of real monthly returns. Whole years are used so that streaks, like crashes and recoveries, stay intact. The random seed is fixed so results are repeatable.
- **Long-history stand-ins:** before a young fund's first day, the returns of an older fund that tracks the same index are used, rescaled so the two series join without a jump. Used only in the Returns tab, and always labeled. Stand-ins differ slightly in fees, for example SPY charges 0.09% a year and VOO 0.03%.
- **Data cleaning:** blank prices from the data source are dropped as they are loaded.
- **Assumptions:** prices are adjusted for dividends and splits. Cash earns 0%. There are no trading costs or taxes.

## Project structure

```
app.py         Streamlit interface: inputs, tabs, charts, takeaways
checks.py      Checklist tests; each is a function (info, hist) -> (status, detail), registered in TESTS
backtest.py    Backtests, benchmark comparison, annualized returns, replay, simulation, history splicing
main.py        Command-line runner for the checklist
```

## Run locally

```bash
git clone https://github.com/<your-username>/stock-checklist.git
cd stock-checklist
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Each `git push` to `main` redeploys the live app on Streamlit Community Cloud.

## Roadmap

- [x] Checklist with price-based tests
- [x] Deployed web app with continuous deployment
- [x] 200-day moving average backtest
- [x] Benchmark comparison with a choice of benchmark
- [x] 1, 3, 5, and 10-year annualized returns
- [x] Replay of every past starting month, with monthly contributions
- [x] Block bootstrap simulation of possible outcomes
- [x] Long-history stand-ins for young funds
- [ ] Volatility in plain English, and a normal pullback level for each stock
- [ ] Backtest of the pullback rule, with an adjustable threshold
- [ ] Valuation card (P/E, P/S, sector context)
- [ ] Summary report card
- [ ] Guess-first mode before comparisons
- [ ] Portfolio view, paper portfolio, and investing journal
- [ ] AI "explain this page"

## Disclaimer

This is an educational and analysis tool, not financial advice. Past performance, real or simulated, does not predict future results. Data comes from Yahoo Finance via `yfinance`.
