"""Station 3 - FinVADER-Extended sentiment model and sector sentiment index.

Scorer (build-time only; the deployed app never runs this):
  base   = finVADER  (VADER + SentiBigNomics x0.1 + Henry; ~13,300 terms, Week 9)
  + our  = FinVADER-Extension, 20 finance-news words mined from a fresh CNBC/
           Reuters/MarketWatch corpus and rated by a 10-agent panel, kept only
           where |mean valence| >= 0.5 and cross-agent std < 2.0. Provenance:
           scripts/lexicon/, data/lexicon_extension/kept_lexicon.csv.

The combined scorer is FinVADER-Extended. Words are added on VADER's native
-4..+4 valence scale (e.g. "soars" = 3.1, like VADER's "great" = 3.1).

Pipeline:
  1. Score each headline with the FinVADER-Extended compound score [-1, +1].
  2. Average scores per (trading_date, ticker): ticker-day sentiment.
  3. Average ticker scores per (trading_date, sector): sector-day sentiment
     (equal-weight tickers within a sector).
  4. Lag by 1 trading day so day-t signal uses only data available at t-1.
  5. Fill missing days by carrying the last known value forward (ffill),
     then fill any remaining leading NaN with 0 (neutral).
"""
from __future__ import annotations

import pandas as pd

# FinVADER-Extension: mined + 10-agent-rated finance words (word -> mean valence,
# -4..+4). Single source of truth is results/lexicon/kept_lexicon.csv, built across
# mining rounds by scripts/lexicon/ (candidates filtered against finVADER's own
# lexicon, so these are genuine additions). Loaded at build time only; the deployed
# app never imports this module.
def _load_csv_map(filename: str, key_col: str) -> dict[str, float]:
    import csv
    import pathlib
    path = (pathlib.Path(__file__).resolve().parent.parent
            / "results" / "lexicon" / filename)
    out: dict[str, float] = {}
    if path.exists():
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                out[row[key_col]] = float(row["mean_valence"])
    return out


import re

# Single-word additions (kept_lexicon.csv) and phrase-level idioms (kept_idioms.csv),
# both mined + 10-agent-rated (|mean| >= 0.5, std < 2.0). Provenance: scripts/lexicon/.
#
# Idioms are applied by PHRASE COLLAPSING, not VADER's native SPECIAL_CASE_IDIOMS.
# The native mechanism only fires when the phrase's last word is a lexicon word, there
# are >= 3 preceding tokens, and the word 3-back is not a lexicon word -- so leading or
# mid-headline phrases ("Shares soar ...") usually do NOT fire. Instead we detect each
# idiom in the text and join it into one token carrying the idiom valence, which fires
# regardless of position. This gives phrases the context single words cannot: finVADER
# scores "profit warning" at +0.13 (backwards); the collapsed idiom scores it negative.
FINVADER_EXTENSION = _load_csv_map("kept_lexicon.csv", "word")
FINVADER_IDIOMS = _load_csv_map("kept_idioms.csv", "phrase")

_IDIOMS_BY_LEN = sorted(FINVADER_IDIOMS, key=lambda p: -len(p))  # longest-first


def _collapse(phrase: str) -> str:
    """Join a phrase into a single alphabetic token, e.g. 'profit warning' -> 'profitwarning'."""
    return re.sub(r"[^a-z]", "", phrase.lower())


def apply_idioms(text: str) -> str:
    """Replace each known idiom phrase in the text with its collapsed single token."""
    t = str(text)
    for phrase in _IDIOMS_BY_LEN:
        t = re.sub(r"(?i)\b" + re.escape(phrase) + r"\b", _collapse(phrase), t)
    return t


def _get_analyzer(extended: bool = True):
    """Return the FinVADER-Extended analyzer (or plain finVADER if extended=False).

    Base = NLTK VADER lexicon + finVADER's two finance word lists (SentiBigNomics
    scaled x0.1, Henry as-is), matching the Week 9 lecture. When extended, our mined
    single words AND collapsed idiom tokens are layered on the lexicon. Use
    finvader_extended_score() so idiom phrases are collapsed before scoring.
    """
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from finvader.SentiBignomics import lexicon1
    from finvader.Henry import lexicon2

    sia = SentimentIntensityAnalyzer()
    sia.lexicon.update({term: value * 0.1 for term, value in lexicon1().items()})
    sia.lexicon.update(lexicon2())
    if extended:
        sia.lexicon.update(FINVADER_EXTENSION)
        sia.lexicon.update({_collapse(p): v for p, v in FINVADER_IDIOMS.items()})
    return sia


def finvader_extended_score(sia, text: str, idioms: bool = True) -> float:
    """Compound score under FinVADER-Extended, collapsing idiom phrases first."""
    try:
        return sia.polarity_scores(apply_idioms(text) if idioms else str(text))["compound"]
    except Exception:
        return 0.0


def score_headlines(headlines: pd.DataFrame) -> pd.DataFrame:
    """Add a 'compound' FinVADER-Extended score column to the headlines frame.

    Expects columns: title, ticker, date (tz-naive), sector.
    Returns the same frame with an added 'compound' column.
    """
    sia = _get_analyzer()
    out = headlines.copy()
    out["compound"] = out["title"].apply(lambda t: finvader_extended_score(sia, str(t)))
    return out


def build_ticker_sentiment(
    scored: pd.DataFrame,
    trading_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Average VADER scores per (trading_date, ticker).

    Returns a wide frame: index = trading_date, columns = tickers.
    Missing ticker-days are NaN (no headlines that day).
    """
    # Align to trading dates (same mapping as Part A text assembly)
    df = scored.copy()
    df["date"] = pd.to_datetime(df["date"])
    trading_series = pd.Series(trading_dates, dtype="datetime64[ns]")

    def _next_td(d):
        idx = trading_series.searchsorted(d)
        return trading_series.iloc[idx] if idx < len(trading_series) else pd.NaT

    df["trading_date"] = df["date"].map(_next_td)
    df = df.dropna(subset=["trading_date"])
    df = df[df["trading_date"].isin(trading_dates)]

    ticker_daily = (
        df.groupby(["trading_date", "ticker"])["compound"]
          .mean()
          .unstack("ticker")
    )
    # Reindex to full trading calendar
    ticker_daily = ticker_daily.reindex(trading_dates)
    return ticker_daily


def build_sector_sentiment(
    ticker_sentiment: pd.DataFrame,
    sector_map: dict[str, str],
    trading_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Average ticker sentiment within each sector.

    sector_map: {ticker -> sector}

    Returns a wide frame: index = trading_date, columns = sectors.
    Missing days are filled by carry-forward then 0 (neutral).
    Lagged by 1 trading day.
    """
    # Map tickers to sectors
    ts = ticker_sentiment.copy()
    ts.columns = [sector_map.get(c, c) for c in ts.columns]

    # Average within each sector (equal-weight tickers)
    sector_daily = ts.T.groupby(ts.columns).mean().T

    # Lag by 1 trading day (shift forward so t uses t-1 data)
    sector_lagged = sector_daily.shift(1)

    # Fill missing: carry forward last known value, then fill leading NaN with 0
    sector_filled = sector_lagged.ffill().fillna(0.0)

    return sector_filled.reindex(trading_dates)


def build_sentiment_tilt(
    base_weights: pd.DataFrame,
    sector_sentiment: pd.DataFrame,
    sector_map: dict[str, str],
    alpha: float = 0.10,
) -> pd.DataFrame:
    """Apply a sentiment tilt to base portfolio weights.

    Upweights tickers in above-median-sentiment sectors and downweights
    those in below-median sectors by factor alpha. Weights are renormalized.

    Parameters
    ----------
    base_weights     : (rebalance_date x ticker) weight frame from backtest
    sector_sentiment : (date x sector) lagged sentiment frame
    sector_map       : {ticker -> sector}
    alpha            : tilt strength [0, 1]
    """
    tilted_records = []
    for date, row in base_weights.iterrows():
        weights = row.dropna()
        if len(weights) == 0:
            tilted_records.append(row)
            continue

        # Use lagged sentiment as of the rebalance date
        if date not in sector_sentiment.index:
            tilted_records.append(row)
            continue

        sent = sector_sentiment.loc[date]
        median_sent = sent.median()

        tilt_factors = {}
        for ticker in weights.index:
            sector = sector_map.get(ticker)
            if sector and sector in sent.index:
                s = sent[sector]
                if s > median_sent:
                    tilt_factors[ticker] = 1.0 + alpha
                elif s < median_sent:
                    tilt_factors[ticker] = 1.0 - alpha
                else:
                    tilt_factors[ticker] = 1.0
            else:
                tilt_factors[ticker] = 1.0

        new_w = weights * pd.Series(tilt_factors)
        new_w = new_w.clip(lower=0.0)
        total = new_w.sum()
        if total > 1e-12:
            new_w = new_w / total

        new_row = row.copy()
        new_row[new_w.index] = new_w.values
        tilted_records.append(new_row)

    return pd.DataFrame(tilted_records, index=base_weights.index)
