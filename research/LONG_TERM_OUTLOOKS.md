# Long-Term Outlooks: design note (not built yet)

**Question:** "What is Investedia's longer-term thesis on this asset?" Fundamental and strategic, 1–12 months. Architecturally separate
from the event-driven Market Outlooks / Priority Signals (research/ENGINE-V4.md): own engine version line (`lt-v1`), own records file,
own outcome rule, own Track Record. Never mixed into short-term statistics.

## Data model (one record per thesis, frozen at creation; outcomes appended)
- ids: `outlook_id`, asset id (registry), engine (`lt-v1`), outcome rule (`lt-outcome-v1`), created / public / start time
- `horizon`: 1M | 3M | 6M | 12M (one thesis may carry several checkpoints, each judged separately)
- `stance`: positive | negative | neutral (relative to a stated benchmark), `confidence`, expected relative-return range
- `benchmark`: index or sector ETF the thesis is measured against (theses are relative by default)
- `drivers[]`: {factor: growth | margins | valuation | balance-sheet | competition | industry | management | capital-allocation | macro | risk | catalyst,
  value, as_of, source}; missing = explicit null
- `catalysts[]`: dated expected events (earnings dates, product cycles, regulatory decisions)
- `invalidation`: the conditions that would break the thesis (stated at creation)
- `inputs_snapshot`: fundamentals and estimates as of creation (no later restatements)
- outcomes per checkpoint: entry/exit prices, benchmark move, relative move, verdict, max drawdown along the way

## Evaluation (separate)
Relative return vs the stated benchmark at each checkpoint; hit rate of the stance; calibration by confidence bucket; compared with
naive baselines (sector momentum, consensus-rating direction, always-benchmark). Overlapping theses on the same asset count once per
checkpoint window. Forward only: any backtest before the language model's training cutoff is contaminated.

## Data still needed (none of it is in Investedia today)
- point-in-time fundamentals (income statement, balance sheet, cash flow) with filing dates: SEC XBRL company facts (free, US only) +
  a licensed provider for non-US issuers;
- consensus estimates and revisions history (EPS/revenue, forward years): licensed (e.g. LSEG/FactSet/S&P/Zacks/Finnhub paid tiers);
- valuation history (multiples) derived from the above + daily prices with corporate actions (split/dividend-adjusted, licensed for display);
- sector/industry classification with peers (registry has SEC SIC; a GICS-like licensed scheme is better);
- ownership, buybacks and issuance (SEC filings), management changes (8-K item 5.02), guidance history (8-K/press releases);
- macro series for exposure (FRED/ECB, free).

## Product wording
"Long-Term Outlook", "thesis", "expected relative performance": general research, never personalised advice, never "buy/sell".
