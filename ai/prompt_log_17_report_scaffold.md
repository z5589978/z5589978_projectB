# Prompt Log 17 - Report Scaffold (report/OUTLINE.md)

**Session date:** 2026-08-12
**Task:** Build a very detailed, dot-point report scaffold (NOT prose) covering the
brief's 6 sections, from everything actually in the project. Interpretation left as
`[STUDENT TO WRITE]` placeholders; numbers cited to source files.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Build a Very Detailed Report Scaffold From Everything We've Actually Built
>
> No report exists yet (`report/` currently only has the brief PDF in it). I want a very detailed scaffold — not finished prose, a structured outline with dense dot-points — covering every section the brief requires, built from everything that's actually in this project: every `ai/` log, every `results/` file, `src/`, and `PROJECT.md`. This is a planning aid I'll write the real report from, not a draft to submit as-is.
>
> ## 0. Ground rule before you write anything
> **Dot-points and structure only. No flowing analytical prose, no written-out economic interpretation, no finished sentences of reasoning.** Every place that needs my own interpretation, judgement, or explanation of *why* a result looks the way it does must be an explicit placeholder like `[STUDENT TO WRITE: interpret why X, considering Y and Z]` — not a drafted paragraph I could accidentally submit unchanged. ... Where you list numbers or facts, cite the exact source file ...
>
> ## 1. Audit everything first — build yourself a master fact sheet
> [read every ai/prompt_log_01..16; PROJECT.md; src/portfolio.py, backtest.py, sentiment.py; every results/data, results/tables, results/lexicon, results/figures file — pull REAL numbers; context/DATA_GUIDE.md + project_context.md; the Part A report + ai/AI_NOTES.md — reference it, don't repeat Station 1-2.]
>
> ## 2. Build `report/OUTLINE.md` following the brief's exact 6-section structure
> [Title "AlphaBlend Investment Platform — Part B Report: Funds, Sentiment & App"; ~5,000 words/10 pages excl appendix; per-section word budgets. S1 funds+backtest design (252-day window, first live date, monthly rebalance, rf=0, 0 tx cost, no look-ahead; 5 methods incl HRP 3 steps + citation + synthetic-validation placeholder; 15 funds exceed the minimum = innovation; placeholder for design defence). S2 OOS results (full 15-row table from performance_metrics.csv; flag specific results w/ exact numbers + [STUDENT TO WRITE] interpretation; required exhibits checklist w/ filenames). S3 sentiment index (FinVADER-Extended composition; before/after numbers from before_after.csv incl the plain>finVADER nuance; sector construction + lag + missing-day rule; coverage table from sentiment_coverage.csv; Week 9 material — 0-100, aggregate, expanding-window z, bands; attribute index=Week9, tilt=brief, don't conflate). S4 innovations (30% — lexicon pipeline, external corpus disclosure, 10-agent rating, filter, idiom phrase-collapsing bug; the 204 vs 473 honest negative; HRP; fusion nuance from fusion_comparison.csv). S5 app (5 pages, design system, target user placeholder, results-only constraint, links placeholder). S6 reflection (what worked/didn't; slide-33 can/cannot; three [STUDENT TO WRITE] recommendation slots w/ candidate angles). Front matter/references/appendix.]
>
> ## 3. Deliverable — write to `report/OUTLINE.md`; don't touch report.docx/report.pdf.
> ## 4. Log it — this prompt verbatim + summary of what facts/numbers you pulled from each source file.
> Start with the audit in section 1.

---

## Facts/numbers pulled into OUTLINE.md, by source

- **`results/tables/performance_metrics.csv`** — all 15 rows verbatim into §2.1 table
  (ann_return, ann_vol, sharpe, max_drawdown, start_date, n_days). Key call-outs:
  Combined MS Sharpe 1.033 / ret 25.48%; Crypto MS Sharpe 0.224 / MaxDD −89.28%;
  Crypto MV Sharpe 1.047; HRP MaxDD Equity −16.94% / Combined −18.41% / Crypto −78.05%;
  Equity RP 0.724 > HRP 0.674 > MS 0.587. First live dates: equity/combined 2021-01-04
  (753 days), crypto 2020-09-10 (1208).
- **`results/tables/fusion_comparison.csv`** — base 0.587 / MaxDD −26.07% → tilt 0.602
  (+0.015) / MaxDD −26.66% (worse). Into §4.4 + §6.
- **`results/lexicon/before_after.csv`** — plain VADER 51.13%, finVADER 39.27%,
  FinVADER-Extended 47.17% non-neutral. Into §3.2 (with the plain>finVADER nuance).
- **`results/tables/sentiment_coverage.csv`** — stock 80%/SD12.81, sector 99%/SD7.30,
  aggregate 100%/SD2.86 (~4.5× noise reduction). Into §3.4.
- **`results/data/aggregate_sentiment_index.csv`** — 0–100 range 45.3–62.8; below 50 on
  1.7% of days (above on 98.3%); latest Extreme greed, z 2.25; span 2020-01-02→2023-12-29.
  Into §3.5.
- **lexicon counts** — 123 words (`kept_lexicon.csv`), 204 idioms (`kept_idioms.csv`),
  473 archived (`kept_idioms_473_round2.csv`). Into §3.1, §4.
- **`src/backtest.py`** — ESTIMATION_WINDOW 252, RF 0, ANNUALISE 252, monthly rebalance,
  window slice excludes day i. Into §1.1.
- **`src/portfolio.py`** — 5 methods incl `hierarchical_risk_parity()` 3-step mechanics.
  Into §1.2.
- **`src/sentiment.py`** — build_sector_sentiment (equal-ticker-weight, shift+1 lag,
  ffill→0), to_score_100, build_aggregate_sentiment, standardise_expanding, Z_BANDS.
  Into §3.
- **`ai/prompt_log_12`** — HRP synthetic validation (low-var 0.901 vs high-var 0.099;
  rank corr 1.00 vs risk_parity, not identical). Into §1.2 + appendix.
- **`ai/prompt_log_08`** — borderline idioms ("biggest analyst calls", "central bank",
  "rate hike", "cost cutting"). Into §4.2 + appendix.
- **`ai/prompt_log_09`** — index=Week9 vs tilt=brief attribution note. Into §3.6.
- **`ai/prompt_log_05/07/08/11`** — corpus sizes (2,154 idiom / 452 word articles),
  10-agent rating, filter thresholds, phrase-collapsing bug, 204↔473 revert. Into §4.
- **Part A** — report.pdf + ai/AI_NOTES.md confirmed present; referenced for target user
  / value proposition (§5.3) and Part A reference list (§References). NOT repeated.

## Deliverable
- Wrote **`report/OUTLINE.md`** (planning aid). Did NOT touch report.docx / report.pdf
  (neither exists yet; those are the student's to author).
- Every interpretation is a `[STUDENT TO WRITE]` placeholder; every number cites its file.
