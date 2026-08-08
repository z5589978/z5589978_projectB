# AGENTS.md - My AI coding assistant instructions (Part B)

This file is my own work and replaces the provided stub. It records the rules I
actually give my AI coding assistant (Claude Code) for Part B of FINS3645.

## What this project is

AlphaBlend — a prototype FinTech investment app offering systematically managed
multi-asset funds with news-sentiment analytics. Part B builds on the Part A data
foundation (z5589978_projectA) to deliver:

1. Walk-forward out-of-sample backtests across 12 funds (3 asset families ×
   4 optimisation methods).
2. A VADER-based sector news-sentiment index with an extended finance lexicon.
3. Sentiment-fusion extension that tilts equity fund weights by sector sentiment.
4. A deployed Streamlit app supporting the full investor journey.

Data loads exclusively through `src/data_access.py`. See `context/DATA_GUIDE.md`.

## Data provenance

- Equity prices: 50 US large-caps, 10 sectors, 2020-2023, adjClose for returns.
- Crypto prices: 10 coins, 2020-2023, cap at 2023-12-31 (10 stray 2024-01-01 rows).
- News headlines: 149,683 rows before dedup; deduplicate on ticker+date+title.
- All data loads via the provided ZIP helper — never commit .parquet files.

## Instructions I give my AI assistant

### What I ask Claude Code to do

- Write and debug Python (ETL, portfolio optimisation, sentiment, backtest, Streamlit).
- Generate figures according to the project style conventions below.
- Draft report sections as starting points — I always rewrite analysis and
  interpretation in my own words before submission.
- Log each session's prompts, outputs, and my corrections in `ai/prompt_log_NN_*.md`.

### What I always check myself

- No look-ahead: I trace the data flow from weights formation to return calculation
  manually to confirm t-period weights use only t-1 data.
- Annualisation factors: equity = √252, crypto = √365. For combined funds on the
  equity calendar, use √252 on the portfolio return series.
- Sentiment lag: I verify the first row of sector_sentiment_index.csv is NaN/zero,
  confirming the shift was applied.
- Performance numbers: I spot-check Sharpe ratios against plausible 2021-2023
  US equity and crypto out-of-sample benchmarks before accepting them.
- Solver convergence: I verify that min-variance, max-Sharpe, and risk-parity
  weights are materially different from equal-weight (silent stalls are a known issue).
- I run `python scripts/check_handin.py` after every code change.

### Rules the AI must follow

1. **No look-ahead bias anywhere** — in backtests, sentiment lag, or any feature.
2. **Required exact filenames** — results/data/fund_returns.csv,
   results/data/fund_weights.csv, results/data/sector_sentiment_index.csv,
   results/tables/performance_metrics.csv. Never rename these.
3. **App never recomputes or imports nltk** — streamlit_app.py only reads
   precomputed results/ CSVs. No VADER calls at runtime.
4. **No raw data committed** — no .parquet, no .zip, no source files in git.
5. **No secrets committed** — no .streamlit/secrets.toml with real values.
6. **Flag all AI-drafted prose** — mark any analysis or interpretation text with
   [HUMAN EDIT REQUIRED: rewrite in your own words] so I can rewrite before submission.
7. **Log every non-trivial session** — verbatim prompts, output summary, bugs found,
   corrections made. This is 20% of my mark.
8. **Verify before asserting** — if a function, file, or flag is named in a memory
   or plan, confirm it still exists before recommending it.

### Innovation: extended VADER finance lexicon

My primary extension is patching VADER's lexicon with ~80 finance-domain terms
(e.g. "hawkish", "tapering", "margin call", "short squeeze") and assigned polarity
scores. The goal is reducing false neutrals (currently ~50% of finance headlines with
plain VADER). Implementation: `FINANCE_LEXICON` dict in `src/sentiment.py`, applied
via `sia.lexicon.update(FINANCE_LEXICON)` after init. Run before/after comparison
to evidence the improvement. This is precomputed at build time; the app reads CSV.

### Figure conventions

- Style: clean, minimal spines (top and right removed), grid alpha 0.25.
- Colour palette: Navy #1F3A5F, Crimson #B23A48, Forest #2E7D32, Gold #C99700,
  Teal #007C89, Violet #6B5B95.
- Every figure: figure title + caption note line (source, period, key assumption).
- Axes: always labelled with units. Date axis formatted YYYY-MM where space allows.
- DPI: 150 for saved PNGs. Saved to results/figures/.
- Captions define variables, units, sample period, and the main object shown.

### Run order

```
python scripts/run_part_b.py       # build all results
streamlit run streamlit_app.py     # test locally
python scripts/check_handin.py     # pre-submit check
git status                         # confirm no data files staged
```

### Deployment (Station 4)

The AI assistant can commit, init a new GitHub repo, and push. The final deploy to
Streamlit Community Cloud requires my browser login — the AI will flag clearly
when it is my turn to complete that step.

## How I evaluate AI workflow quality (what the log should show)

- Prompts are verbatim, not paraphrased.
- Outputs are summarised honestly — including what was wrong.
- Corrections explain what I changed and why, in my own words.
- The log is curated: it shows where AI helped, where it failed, and what I did.
- The log is NOT a prompt dump — empty "what was wrong" and "corrections" sections
  indicate uncritical use, which is penalised under the rubric.
