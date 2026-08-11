# Prompt Log 09 - Week 9 Fear & Greed Methodology Audit

**Session date:** 2026-08-12
**Task:** Audit Week 9's index-construction methodology against src/sentiment.py
concept-by-concept, implement gaps, and distinguish it from the (brief-derived) tilt.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Audit Week 9's Fear & Greed Methodology Against Our Code, Implement Any Gaps
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> I want a full audit of Week 9's fear-and-greed methodology against what's actually in `src/sentiment.py` right now — concept by concept, not a skim — and then implement whatever's missing.
>
> ## 1. Re-read the source material
> - `fins2026/week9/week09_fear_greed_fins3645 (1).pdf` — the whole deck.
> - `fins2026/week9/fear_greed_index/` scripts (`01`–`05`, `fear_greed_tools.py`) — the reference implementation.
> - Our current `src/sentiment.py` in full, plus anything already changed by the lexicon-augmentation work (check the latest `ai/prompt_log_*` entries first, since that thread may already have modified this file — don't duplicate or clash with it).
>
> ## 2. One important thing to check honestly, not assume
> I asked you to also cover "tilting methodology from the Week 9 slides" — **check whether the slides actually define a portfolio-tilting methodology at all.** From my own read, Week 9 is entirely about *building the index* (Stage 3: text → score → index) and doesn't mention folding sentiment into portfolio weights anywhere. If that's what you find too, say so explicitly rather than inventing a "Week 9 tilting method" that isn't there — our tilt logic (`build_sentiment_tilt` in `src/sentiment.py`) comes from the main `PROJECT_BRIEF.md`'s fusion requirement instead, which is more open-ended ("fold sentiment into the equity funds — a tilt or factor — and report before-vs-after"). Audit that function against the *brief's* requirement, not against Week 9, and make the distinction clear in the report so I don't misattribute it.
>
> ## 3. Go through every piece of Week 9's index-construction methodology and check implementation status
> [items 1-9: finVADER; 0-100 rescale; three aggregation levels incl market-wide aggregate; coverage analysis; 21-day rolling; standardisation z-score; look-ahead expanding window; fear/greed bands; "what the index can and cannot tell you" slide 33]
>
> ## 4. After the audit, give me a clean summary
> A short table: concept -> already implemented (where) / newly implemented (what changed) / deliberate judgement call (what you chose and why).
>
> ## 5. Log it
> Log this session to the next ai/prompt_log_0X_week9_methodology_audit.md.
>
> Start with the audit now.

---

## Point 2 — the honest check: does Week 9 define a tilt? NO.

Confirmed: the Week 9 deck (34 slides) and scripts 01-05 are ENTIRELY index
construction (text -> finVADER score -> 0-100 rescale -> aggregate/sector/stock
average -> standardise). Nothing about portfolio weights or tilting. Our
`build_sentiment_tilt` is NOT a Week 9 method; it implements PROJECT_BRIEF.md's
fusion requirement ("fold sentiment into the equity funds — a tilt or factor — and
report before-vs-after"). Attribution must be: index = Week 9; tilt = brief. The
report should state this so it isn't misattributed.

Tilt audited against the BRIEF: build_sentiment_tilt does a same-day CROSS-SECTIONAL
median split (upweight tickers in above-median-sentiment sectors, downweight
below-median, by alpha=0.10, renormalise), using the LAGGED sector index -> satisfies
"tilt/factor" and "before-vs-after" (fusion_comparison), look-ahead-safe. Valid.

## Findings + what changed (concept by concept)

1. **finVADER (not plain VADER)** — DONE earlier (lexicon thread). Confirmed:
   _get_analyzer builds VADER + SentiBigNomics x0.1 + Henry (+ our words/idioms).
2. **0-100 rescale** — was MISSING (all compound space). ADDED `to_score_100()`;
   aggregate_sentiment_index.csv carries score_100; Figure 5b Panel A plots it.
   Judgement call: kept the REQUIRED sector_sentiment_index.csv in compound space
   (the tilt and the app read it); added 0-100 as an additional standalone exhibit.
3. **Aggregate (market-wide) index** — was MISSING (only ticker + sector). ADDED
   `build_aggregate_sentiment()` (equal-ticker-weight mean across 50 stocks, lagged),
   saved to results/data/aggregate_sentiment_index.csv. Judgement call: equal-ticker-
   weight (matches sector index) rather than the deck's headline-weight pooling, so
   aggregate and sector are directly comparable.
4. **Coverage analysis** — was ASSERTED, not evidenced in code. ADDED
   `sentiment_coverage()` -> results/tables/sentiment_coverage.csv. On our data:
   single stock 80% of days / SD 12.82 (0-100); sector 99% / SD 7.34; aggregate
   100% / SD 2.86 — pooling cuts day-to-day noise ~4.5x, the evidence for building
   at sector level. (Report must CITE this; no report.docx exists yet — flagged.)
5. **21-day rolling average** — already used (Figure 5 `.rolling(21)`), and in
   Figure 5b. Confirmed.
6. **Standardisation (z vs history)** — was MISSING for the standalone index. ADDED
   expanding-window z on the aggregate (Figure 5b Panel B, banded). The TILT keeps
   its same-day cross-sectional median split — a different, valid way to avoid the
   "always greedy" problem (compares sectors to each other, not to their own
   history). Deliberate: index exhibit = standardised-vs-history (Week 9 framing);
   tilt = cross-sectional (brief's fusion). Evidence it's needed: aggregate index is
   above 50 on 98.3% of days.
7. **Look-ahead in standardisation** — `standardise_expanding()` uses an expanding
   window (data up to each date only), never the full sample. Expanding vs
   full-sample z correlate 0.998 on our data (deck reports 0.996). Safe.
8. **Fear/greed bands** — ADDED Z_BANDS + `z_band_label()`; a 'band' column in
   aggregate_sentiment_index.csv and shaded greed/fear regions in Figure 5b. Used
   z-bands (meaningful post-standardisation) rather than the raw 0-100 level bands
   (which never fire below 50, exactly the Week 9 point).
9. **"What the index can and cannot tell you" (slide 33)** — belongs in the report's
   critical-reflection section. No report.docx exists yet -> cannot wire it in.
   Flagged: when writing Section 6, include the can/cannot framing (averages many
   noisy headlines into a readable, standardisable signal; canNOT judge whether a
   headline is true/important, always get the sign right, or serve as a standalone
   buy/sell rule).

## Artifacts added
- results/tables/sentiment_coverage.csv
- results/data/aggregate_sentiment_index.csv (compound, score_100, z_expanding, z_full, band)
- results/figures/aggregate_sentiment_standardised.png (Figure 5b)
- src/sentiment.py: to_score_100, build_aggregate_sentiment, standardise_expanding,
  sentiment_coverage, Z_BANDS, z_band_label.

## Not done (needs the report, which doesn't exist yet)
- Point 4 (cite coverage as the reason for sector-level) and point 9 (can/cannot
  framing) are report-writing tasks; material is prepared above. check_handin still
  warns there is no report/report.pdf.
