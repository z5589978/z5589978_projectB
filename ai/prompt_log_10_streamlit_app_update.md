# Prompt Log 10 - Streamlit App Update (bring app up to date)

**Session date:** 2026-08-12
**Task:** Update streamlit_app.py to reflect everything the sentiment pipeline gained
since the first build (FinVADER-Extended words+idioms, Week 9 aggregate/standardised
index, coverage evidence, fusion finding).

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Bring the Streamlit App Up to Date With Everything Since the First Build
>
> [Section 1: reconstruct change list from logs 04-09 — FinVADER-Extended lexicon
> (words + 473-idiom phrase-collapsing, 39.3%->47.5% non-neutral); the fusion
> trade-off finding (peak +0.015 at 204 idioms, diluted to +0.005 at 473); the Week 9
> audit additions (to_score_100, build_aggregate_sentiment -> aggregate_sentiment_index.csv,
> standardise_expanding, sentiment_coverage -> sentiment_coverage.csv, Z_BANDS/z_band_label,
> aggregate_sentiment_standardised.png).
> Section 2: confirm all results/ from the same final (473-idiom) run; state which
> lexicon is live. Section 3: surface the new material in the app — aggregate 0-100
> fear/greed index, standardised/banded view as headline visual, can/cannot note,
> coverage evidence, "what we built" panel; build a gauge/dial as an original design
> system. Section 4: keep constraints (results-only, slim reqs, cross-check numbers).
> Section 5: test/verify/commit. Section 6: log it.]

(Full prompt retained in the session transcript; key requirements reproduced above.)

---

## Section 2 — consistency check result

Live lexicon: **123 words + 473 idioms (final version).** All pipeline outputs are
from ONE run (2026-08-12 00:45-00:49): fund_returns/weights/performance_metrics
(00:45, deterministic backtest) + sector_sentiment_index / aggregate_sentiment_index /
sentiment_coverage / fusion_comparison (00:49, sentiment stage of the same invocation).
fusion_comparison.csv shows Equity MS 0.587 -> 0.592 = **+0.005** = the 473-idiom
diluted-fusion final. **Confirmed out loud: the 473-idiom version with the diluted
fusion benefit is what is live — a legitimate already-made choice.** No regeneration
needed; nothing stale.

## Section 3 — what changed in the app

Was 4 pages (Compare Funds, Fund Fact Sheet, My Allocation, Sentiment Analytics).
Now 5:

- **NEW "Market Fear & Greed" page** (the sentiment centrepiece):
  - Custom **semicircular gauge/dial** (draw_gauge) — 5 coloured fear->greed band arcs
    with a needle at today's standardised z (Extreme greed today). The original
    design-system visual, not a reused line chart.
  - **Standardised banded time series** (expanding-window z, shaded greed/fear) as the
    headline visual.
  - Expander: raw 0-100 levels showing the index is above 50 on ~98% of days (why
    standardise).
  - **Can/cannot** two-column note (Week 9 slide 33).
- **Enhanced "Sentiment Analytics" page:**
  - "What we built" panel: FinVADER-Extended = finVADER + 123 words + 473 idioms;
    before/after non-neutral coverage metrics (plain VADER 51.1% / finVADER 39.3% /
    Extended 47.5%, +8.2 pts vs finVADER).
  - **Fusion result** table + honest caption (peak +0.015 at 204 idioms -> +0.005 at 473).
  - **Coverage evidence** table (single stock 80%/12.8 -> sector 99%/7.3 -> aggregate
    100%/2.9) justifying the sector-level fund signal.
  - Existing sector series retained (now labelled as the tilt input).
- Added loaders: load_aggregate_sentiment, load_csv, BAND_COLORS, draw_gauge.

## Section 4 — constraints held

- Grep: **0 forbidden runtime imports** (no nltk/finvader/SentimentIntensity/backtest/
  import src). App reads only precomputed results/ CSVs.
- No new dependency (gauge uses matplotlib.patches, already in requirements.txt).
- Numbers read straight from CSVs -> agree with performance_metrics / fusion_comparison
  by construction. Cross-checked: fusion 0.587->0.592 (+0.005); gauge z matches
  aggregate_sentiment_index.csv tail (Extreme greed).

## Section 5 — test/verify

- Headless AppTest on all 5 pages: **zero exceptions**.
- check_handin: passes (only the no-report.pdf WARN).
- Committed; git clean after.
