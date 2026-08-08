# Prompt Log 03 - Week 9 Lecture Walkthrough (Fear & Greed Index)

**Session date:** 2026-08-05
**Task:** Walk through Week 9 lecture slides and starter scripts section by section before building the sentiment index. Identify where the lecture maps onto our deliverables and flag any code changes it implies.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Week 9 Lecture Walkthrough (Fear & Greed Index)
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> Before we go further on the sentiment model, walk me through **Week 9's lecture in detail** — this is the lecture that directly specifies how to build Station 3's sentiment index, and I want to actually understand it, not skim it.
>
> ## 1. Read first, in this order
>
> 1. `fins2026/week9/week09_fear_greed_fins3645 (1).pdf` — the lecture slides in full.
> 2. `fins2026/week9/fear_greed_index/` — the starter scripts (`01_recap_vader_meet_finvader.py` through `05_make_fear_greed_figures.py`, plus `fear_greed_tools.py`). These implement exactly what the slides teach, on the same `news_headlines.parquet` file we already use, so treat them as the reference implementation, not just example code.
>
> ## 2. Go through it with me section by section, in the lecture's own order
>
> [... sections 1-8 as stated in the user's prompt ...]
>
> ## 3. After the walkthrough, map it onto our actual deliverables
>
> Give me a short table or list connecting each lecture concept above to the specific place it lands in Project B.
>
> ## 4. Log this
>
> Add this session to `ai/prompt_log_0X_week9_lecture.md` (next number after what's already in `ai/`), including this prompt verbatim, and a short note on any code changes it leads to.

---

## Files read

- `fins2026/week9/week09_fear_greed_fins3645 (1).pdf` — all 34 slides
- `fins2026/week9/fear_greed_index/fear_greed_tools.py`
- `fins2026/week9/fear_greed_index/01_recap_vader_meet_finvader.py`
- `fins2026/week9/fear_greed_index/02_score_headlines.py`
- `fins2026/week9/fear_greed_index/03_transform_to_01.py`
- `fins2026/week9/fear_greed_index/04_build_fear_greed_index.py`
- `fins2026/week9/fear_greed_index/05_make_fear_greed_figures.py`

---

## AI walkthrough output — see conversation for full section-by-section text

Key findings logged here:

### Critical code finding: our src/sentiment.py uses plain VADER, not finVADER
The lecture explicitly states finVADER is the model to use for the index (slide 13, 14).
Our current `_get_analyzer()` in `src/sentiment.py` returns a plain VADER SentimentIntensityAnalyzer.
This needs to be changed. The finvader package may need installing. See section 2 of the walkthrough.

### Look-ahead finding: current code is safe, but with a nuance
Our current `build_sector_sentiment()` uses raw compound scores (not z-scored) for the fusion tilt.
The look-ahead risk from slide 28 (full-sample mean/sd for standardisation) does NOT apply to our
current tilt implementation, because we don't standardise the tilt signal.
IF we ever use a z-scored sentiment as a trading signal, we must use an expanding-window mean/sd.
The `sector_sentiment_index.csv` we produce (raw lagged compound scores) is look-ahead free as-is.

### Sector-level aggregation: our implementation is correct per the brief
The lecture's `groupby(["date","sector"]).mean()` is news-volume-weighted (more headlines = more weight).
The brief says "equal-weight the tickers within each sector."
Our current `src/sentiment.py` does the two-step correctly:
  Step 1: build_ticker_sentiment() — average per (date, ticker)
  Step 2: build_sector_sentiment() — average ticker scores per sector (equal-weight tickers)
This is the right approach. The lecture's simpler version is acceptable but doesn't match the brief.

### Innovation implications
The planned innovation (extended VADER lexicon ~80 terms) is LARGELY what finVADER already does
(SentiBigNomics: 7,295 terms + Henry's 189 terms = 7,484 total). Simply switching to finVADER is
following the lecture instruction, not an innovation. Stage 7 will need to revisit the innovation.

---

## Code changes this session implies

1. **Switch `src/sentiment.py` `_get_analyzer()` to use finVADER** — required per the lecture.
   Check if `finvader` package is installed in `.venv` first.
2. **No change to the tilt/fusion code** — raw compound scores are look-ahead safe.
3. **If adding z-scored standardisation as a trading signal** — must use expanding-window,
   not full-sample mean/sd. Not currently in our code.

---

## Corrections and follow-up

- Innovation choice to be revisited in Stage 7.
- User should rewrite the economic interpretation sections flagged in the walkthrough.
