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

### Innovation: FinVADER-Extended — mined + multi-agent-rated lexicon (30% criterion)
Supersedes the old "~80 hand-picked terms" plan. Base scorer moves from plain
VADER to finVADER (SentiBigNomics ×0.1 + Henry, 13,324 terms, −4…+4 scale), then
we layer our own mined words on top via a third `.lexicon.update()`.
- [x] Confirmed finVADER integration point (NLTK analyzer + .lexicon.update; the
      finvader() convenience function can't inject custom words)
- [x] Switch base scorer in src/sentiment.py to finVADER (+ FinVADER-Extension)
- [x] Mine 452 real financial-news articles (CNBC + MarketWatch + Reuters-via-GNews)
- [x] Curate per-article metadata → data/lexicon_extension/ (gitignored raw text)
- [x] Extract candidate words NOT already in finVADER's 13,324-term lexicon (828 → 150)
- [x] Cap candidates at 150 by frequency, proper nouns dropped; user confirmed
- [x] 10 independent agent rating passes on the −4…+4 VADER scale (raw archived)
- [x] Filter: |mean| ≥ 0.5 AND std < 2.0 → 20 survivors (user chose 0.5 floor;
      std never binds, max std 0.52 — documented)
- [x] Build FinVADER-Extended; scaled to 123 survivors across 2 mining rounds
      (round 1: 20/150; round 2: 103/409; cumulative 123/100 target reached)
- [x] USER CHECKPOINT: round-1 20-word set approved; round-2 borderline words flagged
- [x] Before/after: finVADER 39.3% → Extended 45.8% non-neutral (+6.54pts, 7,041 headlines)
- [x] Phrase-level idioms extension: 204 finance idioms mined + 10-agent-rated,
      applied via phrase-collapsing (VADER's native SPECIAL_CASE_IDIOMS is position-
      limited). Corpus grown 452→2,154 articles. scripts/lexicon/10-13.
- [x] Regenerate sector_sentiment_index.csv + fusion. With words+idioms the fusion
      turns POSITIVE: Equity MS Sharpe 0.587 → 0.602 (+0.015); before/after
      finVADER 39.3% → Extended 47.2% non-neutral (+7.90pts, 8,544 headlines)
- [x] Persistent audits: lexicon_evaluations.csv (559 words), idiom_evaluations.csv
      (400 phrases). kept_lexicon.csv (123) + kept_idioms.csv (204).
- [ ] Described with methodology + filtering equation in report Section 4 (report stage)

**Artifacts:** scripts/lexicon/01–04, results/lexicon/ (kept_lexicon.csv,
candidate_scores.csv, ratings_matrix.csv, before_after.csv, corpus_summary.csv,
ratings/*.json). Raw corpus gitignored under data/lexicon_extension/.

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
