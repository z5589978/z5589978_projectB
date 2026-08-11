# Prompt Log 11 - Revert to the 204-Idiom Lexicon

**Session date:** 2026-08-12
**Task:** Revert the idiom lexicon from 473 (round 2) back to the 204-idiom round-1
set, which gave the best fusion result, and refresh everything downstream + the app.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Revert to the 204-Idiom Lexicon, Then Refresh the App's Fear & Greed Index
>
> Per `ai/prompt_log_08_idioms.md`: round 1 (204 idioms) gave the best fusion result — Equity MS Sharpe 0.587 → 0.602, +0.015. Round 2 added 269 more (473 total) and the fusion benefit *diluted* to +0.005. I want to go back to the 204-idiom version that actually worked best, then make sure everything downstream — including the app's fear & greed index — reflects that.
>
> ## 1. Recover the round-1-only (204) idiom set, don't just guess
> [check git for a post-round-1 commit where kept_idioms.csv has exactly 204 rows and check it out; else reconstruct from idiom_round1_agent_XX.json by re-applying |mean|>=0.5 & std<2.0 and confirm 204, stopping on any mismatch. Archive, don't delete, the 473 version.]
>
> ## 2. Rebuild the lexicon and regenerate everything downstream
> [point src/sentiment.py idiom loading at the 204 set; re-run scoring, ticker/sector/aggregate sentiment, coverage (confirm idiom-count-independent), tilt+fusion, fund backtest, and dependent figures.]
>
> ## 3. Sanity-check against the original round-1 numbers
> [confirm regenerated fusion reproduces 0.587->0.602 (+0.015) and non-neutral coverage improves from finVADER 39.3% by roughly the round-1 amount; flag meaningful drift.]
>
> ## 4. Refresh the app's fear & greed index to match
> [aggregate/sector 0-100/z/band regenerate from reverted scores; "what we built" text must say 204 idioms not 473; fusion/Sharpe numbers must reflect the reverted result.]
>
> ## 5. Test and verify
> [streamlit run + walk pages, numbers match performance_metrics/fusion_comparison; check_handin; commit incl. archived 473 file and push.]
>
> ## 6. Log it
> [log verbatim prompt, how the 204 was recovered, regenerated vs original numbers, app changes; be honest that 473 was tried first and reverted for a documented evidence-based reason.]
>
> Start with step 1 now.

---

## Step 1 — how the 204 set was recovered (two independent sources agree)

- Git: commit **b76d51e** ("Add 204 finance idioms", post-round-1, before round 2's
  dfa7c9b) has `kept_idioms.csv` with **exactly 204 rows**. Checked it out into place.
- Cross-check: independently reconstructed round-1 survivors from
  `idiom_evaluations.csv` (round==1, |mean|>=0.5 & std<2.0) = **204**, and the phrase
  set is **identical** to the git-recovered file (`sets identical: True`). Confident.
- Archived the 473 version to `results/lexicon/kept_idioms_473_round2.csv` (not deleted
  — the dilution finding is a reportable result).
- No code change needed: `src/sentiment.py` already loads idioms from
  `results/lexicon/kept_idioms.csv`; confirmed it now loads 204 (words still 123).

## Step 2/3 — regenerated numbers vs the original round-1 numbers

| Metric | Original round-1 (log 08) | Regenerated (204) | Match |
|--------|---------------------------|-------------------|-------|
| Idioms live | 204 | 204 | ✓ |
| Fusion (Equity MS Sharpe) | 0.587 → 0.602 (+0.015) | 0.587 → 0.602 (+0.015) | ✓ exact |
| Non-neutral (FinVADER-Extended) | +7.90 pts (39.3% → 47.2%) | 39.27% → 47.17% (+7.90) | ✓ |
| Coverage pct_of_days | (idiom-independent) | 80 / 99 / 100 % | unchanged |

**Coverage flag (as asked):** `pct_of_days` (days-with-news) is idiom-count-INDEPENDENT
(unchanged). The `daily_change_sd_0_100` column is *mildly* idiom-dependent because it
is computed on the sentiment VALUES (0-100), which shift slightly with the lexicon:
12.82→12.81, 7.34→7.30, 2.86→2.86. Trivial drift; noted rather than assumed away.

All downstream regenerated from ONE run: fund_returns/weights/performance_metrics
(deterministic backtest, unchanged by lexicon), sector_/aggregate_sentiment_index,
sentiment_coverage, fusion_comparison, and figures.

## Step 4 — app refresh

- Lexicon counts in the "what we built" panel are read DYNAMICALLY from
  kept_lexicon.csv / kept_idioms.csv row counts -> now shows **123 words + 204 idioms**
  automatically.
- Fusion table (Fund pages / Sentiment page) reads fusion_comparison.csv ->
  auto-shows 0.587 → 0.602 (+0.015).
- Updated the one hardcoded fusion narrative caption: now states 204 is the live/chosen
  set (best tilt +0.015) and that extending to 473 diluted it to +0.005 so we reverted
  (473 archived). Honest about the try-then-revert.
- Market Fear & Greed gauge/standardised index recompute from the reverted
  aggregate_sentiment_index.csv (latest still "Extreme greed", z≈2.25).

## Step 5 — verify

- All 5 pages pass headless AppTest, zero exceptions.
- check_handin passes (only no-report.pdf WARN).
- Numbers on pages read straight from the regenerated CSVs -> consistent.

## Honest note for the report

473 idioms were built and tried FIRST; we reverted to 204 for a documented,
evidence-based reason — the sentiment tilt's Sharpe gain peaked at +0.015 with 204
idioms and diluted to +0.005 at 473. "More idioms is not strictly better" is a genuine
finding and belongs in the critical-reflection section; the 473 set is archived, not
erased, so the experiment is reproducible.
