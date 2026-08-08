"""Station 3 - VADER sentiment model and sector sentiment index.

Pipeline:
  1. Score each headline with VADER compound score [-1, +1].
  2. Average scores per (trading_date, ticker): ticker-day sentiment.
  3. Average ticker scores per (trading_date, sector): sector-day sentiment.
  4. Lag by 1 trading day so day-t signal uses only data available at t-1.
  5. Fill missing days by carrying the last known value forward (ffill),
     then fill any remaining leading NaN with 0 (neutral).
"""
from __future__ import annotations

import pandas as pd


def _get_analyzer():
    """Return a VADER SentimentIntensityAnalyzer, downloading lexicon if needed."""
    import nltk
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer()


def score_headlines(headlines: pd.DataFrame) -> pd.DataFrame:
    """Add a 'compound' VADER score column to the headlines frame.

    Expects columns: title, ticker, date (tz-naive), sector.
    Returns the same frame with an added 'compound' column.
    """
    sia = _get_analyzer()

    def _score(title: str) -> float:
        try:
            return sia.polarity_scores(str(title))["compound"]
        except Exception:
            return 0.0

    out = headlines.copy()
    out["compound"] = out["title"].apply(_score)
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
