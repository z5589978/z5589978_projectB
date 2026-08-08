# CLAUDE.md - Project B agent instructions

## What this project is

FINS3645 Part B: Funds, Sentiment & App for **AlphaBlend** — a prototype FinTech
investment product offering several systematically managed funds built from 50 US
equities (10 sectors) and 10 cryptocurrencies, with a news-sentiment analytics
layer. Part A (Stations 1-2) is complete in `../z5589978_projectA`. This folder
is Stations 3-4 only.

All data loads through `src/data_access.py`. Never commit raw `.parquet` or source
data files. See `context/DATA_GUIDE.md` and the project brief PDF for the full spec.

## Folder layout

```
src/            Python modules (etl.py, features.py, data_access.py [provided],
                backtest.py [provided], portfolio.py [provided], sentiment.py [provided])
scripts/        Runnable scripts (run_part_b.py, check_handin.py)
results/
  data/         fund_returns.csv, fund_weights.csv, sector_sentiment_index.csv
  tables/       performance_metrics.csv, fusion_comparison.csv
  figures/      PNG exhibits (cumret_by_family.png, drawdown_combined.png, ...)
report/         Word report (report.docx → export to report.pdf)
ai/             Prompt logs and AI notes (this is GRADED - 20% of Part B)
context/        Provided data guide (DO NOT EDIT)
.streamlit/     config.toml (no secrets.toml - never commit secrets)
streamlit_app.py  Streamlit app at the folder root (Station 4)
requirements.txt  App dependencies (slim: no nltk, no heavy packages)
requirements-dev.txt  Dev-only packages (nltk for building sentiment; not in app)
```

## Part B scope (Stations 3-4 only)

- Station 3: walk-forward OOS portfolio backtests (equity, crypto, combined × 4
  methods = 12 baseline funds) + extended VADER sentiment model + sentiment fusion.
- Station 4: Streamlit app serving the investor journey.

**Do NOT redo Station 1-2 work.** Reuse the ETL and feature functions from
Part A (already copied into src/etl.py and src/features.py in this folder).

## Required exact output filenames (markers and app read these)

- `results/data/fund_returns.csv`
- `results/data/fund_weights.csv`
- `results/data/sector_sentiment_index.csv`
- `results/tables/performance_metrics.csv`

Do not rename these. Additional outputs (e.g. `fusion_comparison.csv`) may use
any clear name.

## Run order

```
python scripts/run_part_b.py      # regenerate all results/
streamlit run streamlit_app.py    # test the app locally
python scripts/check_handin.py    # verify all required files are present
git status                        # confirm no stray data files committed
```

## App rules (Station 4 - read carefully)

1. `streamlit_app.py` must only READ precomputed artifacts from `results/`.
   It must NEVER recompute backtests, re-run the portfolio optimiser, or import
   nltk / invoke VADER at runtime. The Streamlit Community Cloud free tier cannot
   handle it, and it is a listed common mistake that loses marks.
2. Raw data (`.parquet`) must never be committed to the repo.
3. No secrets in the repo. Never create `.streamlit/secrets.toml` with real values.
4. Keep `requirements.txt` slim. nltk belongs in `requirements-dev.txt` only.
5. The app loads the data ZIP through `src/data_access.py` (cached). It does not
   need to download data at startup — the app reads `results/` CSVs.

## Coding rules

1. **No look-ahead bias.** Weights at time t are computed only from data up to t-1.
   Sentiment signals are lagged by ≥1 trading day before any use in fund weights.
2. **Annualisation**: equity funds → √252; crypto funds → √365. The combined fund
   is on the equity trading calendar, so also √252 for the portfolio return series.
3. **Calendar merge order**: compute crypto returns on the 365-day calendar FIRST,
   then left-merge onto equity trading dates. Do not merge price levels.
4. **News deduplication**: ticker + date + title (not ticker + date alone).
5. **Timezone**: news dates from tz-aware UTC → tz-naive before any merge.
6. **Outliers**: keep and document; do not delete real events.
7. **Sentiment lag**: the sector sentiment index is shifted forward by 1 trading day.
   Day-t portfolio decision uses sentiment from day t-1 or earlier.
8. **Missing sentiment days**: carry-forward (ffill) then fill leading NaN with 0
   (neutral). Justify this choice explicitly in the report.
9. Sanity-check that optimised weights actually differ from equal-weight across
   methods (silent solver stalls are a known failure mode on small covariance matrices).

## Innovation: extended VADER finance lexicon (planned)

The primary innovation for this project is extending VADER's default lexicon with
~80 finance-domain terms and hand-assigned sentiment polarity scores. This addresses
a known weakness: ~50% of finance headlines score neutral with plain VADER because
domain terms (e.g. "short squeeze", "margin call", "tapering", "hawkish") are absent
from the general lexicon. The extension will:
- Define a `FINANCE_LEXICON` dict mapping term → score in `src/sentiment.py`.
- Patch the SentimentIntensityAnalyzer after init (`.lexicon.update(...)`).
- Run before/after comparison on the headline corpus to show improvement in
  non-neutral coverage.
- Precompute all scores at build time; the app loads the precomputed CSV.

Flag clearly in the report and AI log anywhere this extension changes results.

## AI logging requirement

Every prompt I give you, every non-trivial output you produce, and every correction
I make must be appended to an `ai/prompt_log_NN_<task>.md` file in this format:

```
# Prompt Log NN - <task name>
**Session date:** YYYY-MM-DD
**Task:** one-line goal

## Prompt used (verbatim)
> the exact prompt, quoted

## AI output summary
what was generated

## What I checked / verified
spot-checks I ran

## What was wrong or risky
bugs, look-ahead, hallucinated APIs, wrong assumptions

## Corrections made
my fix, in my own words, with the reason
```

Do not paraphrase prompts. Log them word-for-word.

## How I check the assistant's output

- Run `python scripts/run_part_b.py` and verify it completes without errors and
  all four required CSVs are produced.
- Spot-check fund performance numbers: equity equal-weight OOS Sharpe should be
  plausible (~0.5-1.0 for 2021-2023 US equities out-of-sample).
- Verify no look-ahead: the first live backtest date must be at least 252 trading
  days after the first date in the returns panel.
- Verify sentiment lag: `sector_sentiment_index.csv` index must start with at
  least one NaN or zero row (the lag removes the first available signal).
- Run `python scripts/check_handin.py` before every commit.

## How I verify AI output

- Spot-check computed numbers against known market benchmarks or lecture figures.
- Re-derive key statistics independently before accepting them.
- Economic interpretation is always rewritten in my own words — AI drafts are
  starting points, not final prose. Flag all AI-drafted narrative so I can rewrite.
- Run `check_handin.py` after every code change.
- Where AI was wrong or I corrected something, record it explicitly in the prompt log.

## Writing rules

- Every figure and table is captioned (define variables, units, sample period, main object).
- Every exhibit is referenced and interpreted in the text — never drop raw plots.
- No hard-banned words from the repo academic-writing rules (delve, crucial, utilize, etc.).
- Report analysis and economic interpretation are in my own words. AI-generated
  reasoning submitted as my own is a penalty under the marking rubric.
- Use `[HUMAN EDIT REQUIRED: verify ...]` markers wherever a claim needs my review
  before the final submission.
- State magnitudes; replace vague words ("large", "significant") with numbers.
