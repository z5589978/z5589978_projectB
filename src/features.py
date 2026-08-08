"""Station 2 - feature engineering and text assembly.

Produces:
- Daily returns per ticker (long format with 'ret' column)
- Descriptive statistics table by asset class
- Daily headline panel aligned to equity trading calendar
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Return features
# ---------------------------------------------------------------------------

def daily_returns(prices: pd.DataFrame, price_col: str = "adjClose") -> pd.DataFrame:
    """Compute simple daily returns within each ticker group.

    Returns a long-format frame with columns: ticker, date, ret
    (and sector if present in input).
    """
    prices = prices.sort_values(["ticker", "date"])
    prices = prices.copy()
    prices["ret"] = prices.groupby("ticker")[price_col].pct_change()
    keep = ["ticker", "date", "ret"]
    if "sector" in prices.columns:
        keep.append("sector")
    return prices[keep].dropna(subset=["ret"]).reset_index(drop=True)


def descriptive_stats(
    returns_long: pd.DataFrame,
    asset_class: str,
    annualise_factor: int = 252,
) -> pd.DataFrame:
    """Return a descriptive-statistics table from a long returns frame.

    Computes mean, volatility, min, max, skewness, and excess kurtosis.
    annualise_factor: 252 for equities, 365 for crypto.
    """
    r = returns_long.groupby("ticker")["ret"]
    stats = pd.DataFrame({
        "mean_daily": r.mean(),
        "vol_daily": r.std(),
        "min": r.min(),
        "max": r.max(),
        "skew": r.apply(lambda s: s.skew()),
        "kurtosis": r.apply(lambda s: s.kurtosis()),
    })
    af = annualise_factor
    stats["mean_ann"] = stats["mean_daily"] * af
    stats["vol_ann"] = stats["vol_daily"] * np.sqrt(af)
    stats["asset_class"] = asset_class
    stats.index.name = "ticker"
    return stats.reset_index()


# ---------------------------------------------------------------------------
# Text panel assembly
# ---------------------------------------------------------------------------

_STOP = frozenset([
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "will", "would", "could", "should", "may",
    "it", "its", "that", "this", "as", "up", "said", "says", "after",
    "new", "over", "into", "also", "than", "more", "about", "he", "she",
    "his", "her", "their", "they", "we", "you", "i", "not", "no", "s",
])

_SENTIMENT_VOCAB = frozenset([
    # Positive finance terms
    "beat", "beats", "surged", "gain", "gains", "profit", "profits",
    "growth", "record", "rally", "rallied", "upgrade", "upgraded",
    "strong", "higher", "rise", "rises", "rose", "boost", "positive",
    "outperform", "revenue", "earnings", "dividend", "buy", "bullish",
    # Negative finance terms
    "miss", "misses", "missed", "fell", "fall", "loss", "losses",
    "decline", "declined", "drop", "dropped", "weak", "lower", "cut",
    "downgrade", "downgraded", "concern", "risk", "warning", "sell",
    "bearish", "debt", "default", "lawsuit", "investigation", "recall",
    "layoffs", "bankruptcy", "plunged", "plunge", "crash", "volatile",
])


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z]+", text.lower())
    return [t for t in tokens if t not in _STOP and len(t) > 2]


def assemble_headline_panel(
    headlines: pd.DataFrame,
    equity_trading_dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Align headlines to equity trading dates and aggregate per (date, ticker).

    A headline dated on a trading day maps to that day; otherwise it maps
    to the NEXT trading day (the soonest day a fund could act on it).

    Returns a frame with columns:
        trading_date, ticker, sector, headline_count,
        sentiment_word_count, headlines_text (concatenated)
    """
    df = headlines.copy()
    df["date"] = pd.to_datetime(df["date"])

    trading_series = pd.Series(equity_trading_dates, dtype="datetime64[ns]")

    def _next_trading_day(d: pd.Timestamp) -> pd.Timestamp:
        idx = trading_series.searchsorted(d)
        if idx >= len(trading_series):
            return pd.NaT
        return trading_series.iloc[idx]

    df["trading_date"] = df["date"].map(_next_trading_day)
    df = df.dropna(subset=["trading_date"])
    df["trading_date"] = pd.to_datetime(df["trading_date"])

    # Keep only dates within the equity trading calendar span
    df = df[df["trading_date"].isin(equity_trading_dates)]

    # Sentiment-bearing word count (descriptive only - NOT scoring yet)
    def _sentiment_count(title: str) -> int:
        tokens = re.findall(r"[a-z]+", str(title).lower())
        return sum(1 for t in tokens if t in _SENTIMENT_VOCAB)

    df["sentiment_words"] = df["title"].apply(_sentiment_count)

    # Aggregate per (trading_date, ticker)
    agg = df.groupby(["trading_date", "ticker", "sector"]).agg(
        headline_count=("title", "count"),
        sentiment_word_count=("sentiment_words", "sum"),
        headlines_text=("title", lambda x: " | ".join(x)),
    ).reset_index()

    return agg


def top_terms(
    headlines: pd.DataFrame,
    n: int = 30,
    title_col: str = "title",
) -> pd.Series:
    """Return the n most frequent non-stop tokens across all headlines."""
    all_tokens: list[str] = []
    for text in headlines[title_col].dropna():
        all_tokens.extend(_tokenize(str(text)))
    counts = Counter(all_tokens)
    return pd.Series(dict(counts.most_common(n)), name="count")
