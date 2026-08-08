# PROJECT.md - Part B Planning Notes

## Scope

FINS3645 Part B — Funds, Sentiment & App (Stations 3-4). 50% of course.
**Due: Friday Week 11.**

Builds on Part A (z5589978_projectA). The ETL, cleaning, and feature functions
from Part A are already copied into this folder's src/. Do not redo Station 1-2 work.

## Required output filenames (exact — markers and app use these)

| File | What it contains |
|------|-----------------|
| `results/data/fund_returns.csv` | Daily OOS returns, one column per fund, date index |
| `results/data/fund_weights.csv` | Long format: date, fund, ticker, weight |
| `results/data/sector_sentiment_index.csv` | Lagged sector sentiment, date index, one column per sector |
| `results/tables/performance_metrics.csv` | Ann. return, vol, Sharpe, max drawdown, per fund |

## Run order

```
python scripts/run_part_b.py       # generates all results/
streamlit run streamlit_app.py     # test locally before pushing
python scripts/check_handin.py     # all checks must pass
git status                         # confirm no .parquet or secrets committed
```

## Mandatory hand-in structure

```
z5589978_projectB/
  CLAUDE.md               ← filled in (this is graded)
  AGENTS.md               ← filled in (this is graded)
  README.md               ← how to run + what was built
  SUBMISSION_CHECKLIST.md ← ticked before zip
  PROJECT.md              ← this file (planning notes)
  streamlit_app.py        ← Streamlit app entry point
  requirements.txt        ← slim app deps (no nltk)
  requirements-dev.txt    ← dev-only (nltk, etc.)
  .streamlit/config.toml  ← Streamlit configuration
  src/                    ← Python modules
  scripts/                ← run_part_b.py, check_handin.py
  results/data/           ← four required CSVs above
  results/tables/         ← performance_metrics.csv + others
  results/figures/        ← PNG exhibits
  report/report.pdf       ← final report (Word source = report.docx)
  context/                ← provided data guide (do not edit)
  ai/                     ← prompt logs (this is graded)
```

## HD-band checklist (track progress here)

Mark each item [ ] = not started, [~] = in progress, [x] = done.

### Funds & Backtest (15% of Part B)
- [x] Equity-only funds × 4 methods (EW, MV, MS, RP) — starter code done
- [x] Crypto-only funds × 4 methods — starter code done
- [x] Combined equity+crypto funds × 4 methods — starter code done
- [ ] Walk-forward OOS confirmed: no look-ahead, weights from past data only
- [ ] First live date stated: 252 trading days after start (≈ 2021-01-04)
- [ ] Rebalance frequency stated: monthly (first trading day of each month)
- [ ] Risk-free rate stated: 0 (assumption)
- [ ] Annualisation stated: √252 for all funds (all on equity calendar)
- [ ] Fact sheets: growth of $1, ann. return, vol, Sharpe, max drawdown, weights
- [ ] Funds compared in a table and a figure

### Sentiment & Fusion (10% of Part B)
- [ ] VADER scores computed for all headlines (build time only, not in app)
- [ ] Extended finance lexicon applied (~80 terms, before/after comparison)
- [ ] Ticker-day sentiment averaged → sector-day sentiment
- [ ] Sentiment lagged by 1 trading day (confirmed: first row is NaN/0)
- [ ] Missing days: carry-forward then 0 (justified in report)
- [ ] sector_sentiment_index.csv saved
- [ ] Fusion: equity MS base vs. sentiment-tilted before/after comparison
- [ ] Negative/flat result explained honestly if sentiment doesn't improve Sharpe

### Innovation: Extended VADER Lexicon (30% Innovation criterion)
- [ ] FINANCE_LEXICON dict defined in src/sentiment.py (~80 terms)
- [ ] Polarity scores assigned and justified (positive/negative finance terms)
- [ ] sia.lexicon.update() applied after init
- [ ] Before/after comparison on headline corpus (% non-neutral, coverage)
- [ ] Effect on sector sentiment index documented
- [ ] Effect on fusion comparison documented
- [ ] Described with equation/formula in report Section 4

### App (15% of Part B)
- [x] streamlit_app.py created at folder root
- [x] Investor journey: compare funds → fact sheet → set allocation → sentiment
- [x] App reads only precomputed results/ CSVs (grep-verified: no nltk/finvader/
      VADER/backtest imports; only pathlib, pandas, streamlit, matplotlib, numpy)
- [x] App tested locally: all 4 pages pass headless AppTest, zero exceptions;
      My Allocation edge cases (0%, non-100%, mixed-inception blend) handled
- [x] Numbers cross-checked: all 12 funds' Sharpe reproduce performance_metrics.csv
- [x] Design system applied (branded hero header, metric cards, coherent palette)
- [x] .streamlit/config.toml present (CORS/XSRF conflict removed)
- [x] requirements.txt present (slim: no nltk/finvader); finvader/nltk in -dev only
- [x] Deprecated use_container_width migrated to width="stretch" (deploy-safe)
- [ ] GitHub repo initialised + pushed (local git prepared; gh CLI not installed —
      needs your GitHub auth to create + push the remote)
- [x] check_handin.py passes all [FAIL] checks (21 passed, only WARNs remain)
- [ ] **MY STEP**: create/push remote, make repo public + deploy to Streamlit Cloud

**Note:** the sentiment index the app currently reads is built with PLAIN VADER
(Stage 5 finVADER switch still pending). The Sentiment Analytics caption was
corrected to describe plain VADER truthfully — it no longer claims an "extended
finance lexicon (~80 terms)". If Stage 5 switches to finVADER, re-run
run_part_b.py and update that caption + this note.

### Report (10% + 15% criteria)
- [ ] Section 1: Funds and backtest design
- [ ] Section 2: OOS results and fact sheets
- [ ] Section 3: Sentiment index (plain VADER + extended lexicon)
- [ ] Section 4: Extensions/innovations (extended lexicon, before/after)
- [ ] Section 5: App and investor journey
- [ ] Section 6: Critical reflection — 3 concrete real-world recommendations
- [ ] All exhibits self-contained (caption, axes, units, sample period)
- [ ] All exhibits referenced and interpreted in text
- [ ] All economic interpretation rewritten in MY own words
- [ ] No AI-drafted prose submitted as mine
- [ ] Max ~5,000 words / 10 pages excl. appendix
- [ ] Exported to report/report.pdf

### AI Workflow (20% of Part B)
- [x] CLAUDE.md filled in (replaced placeholder)
- [x] AGENTS.md filled in (replaced placeholder)
- [x] Prompt log 01 created with verbatim kickoff prompt
- [ ] Every subsequent session logged (prompt + output + corrections)
- [ ] Log is curated: honest about errors and corrections
- [ ] Log is NOT a prompt dump: "what was wrong" and "corrections" sections filled in

## Proposed build order

1. **Verify starter pipeline runs** — run `python scripts/run_part_b.py` and confirm
   the 12 base funds complete without errors.
2. **Fix Figure 6 bug** in run_part_b.py (lines 344-350: x/y transposed + duplicate plot).
3. **Extended VADER lexicon** — add FINANCE_LEXICON to src/sentiment.py, run
   before/after comparison, regenerate sector_sentiment_index.csv.
4. **Streamlit app** — build streamlit_app.py with four-panel investor journey.
5. **Report** — draft each section, rewrite interpretation in my own words.
6. **GitHub + deploy** — AI sets up repo and pushes; I deploy via browser.

## Known issues to fix

- `run_part_b.py` lines 344–350, Figure 6 Panel A: first `ax.plot()` has x/y
  transposed (`.values` before `.index`), and "Base (Equity MS)" is plotted twice.
  Fix before running: remove lines 344–345, keep 349–351.
