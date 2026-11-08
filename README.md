# 📊 Stock & ETF Checklist

**Live app:** https://stock-checklist-akshaj.streamlit.app/

Most beginner investors buy on hype and sell in a panic. This tool helps you invest with evidence instead. Enter any stock or ETF to run it through a checklist of investing rules, backtest a trading rule against buy and hold, and see whether you would have been better off just buying the S&P 500.

## Features

**Checklist tab**
- Pass/fail results for a set of price-based tests, each with the data behind it
- A score and progress bar, plus the current price and the 52-week high and low
- A one-year price chart

**Backtest tab**
- **200-day moving average rule:** simulates owning the asset only while it trades above its 200-day average and holding cash otherwise, compared with buy and hold
- **Benchmark comparison:** buy and hold of the ticker compared with buy and hold of VOO (an S&P 500 ETF) over the dates both have data
- Growth-of-$10,000 charts, final value, total return, max drawdown, and time invested
- A plain-English takeaway for each comparison that explains the trade-off between return and risk

## Findings

**The 200-day rule rarely beats holding**

| Ticker | Buy & hold | 200-day rule | Buy & hold max drawdown | 200-day rule max drawdown |
|--------|-----------:|-------------:|------------------------:|--------------------------:|
| VOO    | $36,658    | $27,128      | -34.0%                  | -19.6%                    |
| AAPL   | $92,794    | $43,394      | -38.5%                  | -35.3%                    |
| INTC   | $18,672    | $16,296      | -70.8%                  | -65.8%                    |

*$10,000 invested, Aug 2017 to Nov 2026.*

On the index fund, the rule gave up about a quarter of the final value but cut the worst drop by 14 points, which can be worth it for an investor who might panic-sell. On individual stocks, it lost most of the upside and barely reduced the drawdown, because the price kept crossing the average and the rule kept selling before rebounds.

**Picking individual stocks: a big win or a big loss**

| Ticker | Final value | VOO final value | Max drawdown | VOO max drawdown |
|--------|------------:|----------------:|-------------:|-----------------:|
| AAPL   | $135,958    | $40,818         | -38.5%       | -34.0%           |
| INTC   | $19,066     | $40,818         | -70.8%       | -34.0%           |

*$10,000 invested, Nov 2016 to Nov 2026.*

AAPL beat the index by about $95,000. INTC trailed it by about $21,750 and fell 71% at its worst. The index landed in between with much smaller drawdowns.

**Watch out for survivorship bias:** backtesting a company you already know succeeded, like AAPL, always looks good. An investor in 2016 could not have known whether AAPL or INTC would be the winner.

## Methodology

- **No look-ahead bias:** a signal is computed from the day's close and only acted on the next day (`shift(1)`).
- **Fair warm-up:** both strategies start on the first day a 200-day average exists, so the rule is not penalized for sitting in cash while the average builds.
- **Date alignment:** benchmark comparisons use only the dates both tickers traded (`pd.concat(...).dropna()`), so newer funds are compared fairly.
- **Vectorized:** all calculations use pandas column operations (`rolling`, `shift`, `cumprod`, `cummax`) rather than day-by-day loops.
- **Assumptions:** prices are adjusted for dividends and splits. Cash earns 0%. There are no trading costs or taxes.

## Project structure

```
app.py         Streamlit interface: input, tabs, charts, takeaways
checks.py      Checklist tests; each is a function (info, hist) -> (status, detail), registered in TESTS
backtest.py    run_200dma_backtest(), compare_to_benchmark(), max_drawdown()
main.py        Command-line runner for the checklist
```

Adding a test takes one function in `checks.py` and one line in `TESTS`. The app picks it up automatically.

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
- [x] Benchmark comparison against VOO
- [ ] Portfolio view: holdings, weights, sector concentration, ETF overlap
- [ ] Multiple strategies to choose from and compare
- [ ] Interest on cash in backtests
- [ ] Investing journal: record why you bought, and review it later
- [ ] AI summaries of company filings

## Disclaimer

This is an educational and analysis tool, not financial advice. Past performance does not predict future results. Data comes from Yahoo Finance via `yfinance`.
