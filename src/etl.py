"""Station 1 - ETL: load, clean, and integrity-check all three datasets.

Cleaning philosophy:
- Genuine extreme returns are real events; keep them, document them.
- Deduplicate prices on ticker+date; deduplicate news on ticker+date+title.
- Compute crypto returns on its own 365-day calendar BEFORE merging.
- Normalise news dates from tz-aware UTC to tz-naive before any merge.
"""
from __future__ import annotations

import warnings
from typing import NamedTuple

import numpy as np
import pandas as pd

from src import data_access


class IntegrityReport(NamedTuple):
    missing_equity_dates: int
    missing_crypto_dates: int
    duplicate_equity_rows: int
    duplicate_news_rows: int
    equity_outliers: pd.DataFrame   # rows flagged as extreme
    crypto_outliers: pd.DataFrame


# ---------------------------------------------------------------------------
# Station 1a - equity prices
# ---------------------------------------------------------------------------

def load_clean_equities() -> tuple[pd.DataFrame, dict]:
    """Return clean equity price frame and a summary of integrity checks."""
    df = data_access.load_equity_prices().copy()

    # --- missing-date audit -------------------------------------------------
    # Count (ticker, business-day) pairs absent from the data.
    tickers = df["ticker"].unique()
    date_min, date_max = df["date"].min(), df["date"].max()
    bdays = pd.bdate_range(date_min, date_max)
    full_index = pd.MultiIndex.from_product([tickers, bdays],
                                            names=["ticker", "date"])
    observed = pd.MultiIndex.from_frame(df[["ticker", "date"]])
    n_missing_dates = len(full_index.difference(observed))

    # --- duplicate check ----------------------------------------------------
    dup_mask = df.duplicated(subset=["ticker", "date"], keep=False)
    n_dups = dup_mask.sum()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")

    # --- compute log returns for outlier screen -----------------------------
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["ret"] = (
        df.groupby("ticker")["adjClose"]
          .pct_change()
    )

    # --- outlier / extreme-value screen ------------------------------------
    # Flag daily returns outside ±25 % (real events: keep, but document).
    threshold = 0.25
    outlier_mask = df["ret"].abs() > threshold
    outliers = df.loc[outlier_mask, ["ticker", "date", "adjClose", "ret"]].copy()

    summary = {
        "n_tickers": len(tickers),
        "date_range": f"{date_min.date()} – {date_max.date()}",
        "total_rows_raw": len(df) + n_dups,
        "duplicate_rows_removed": n_dups,
        "missing_business_days": n_missing_dates,
        "outlier_rows_kept": len(outliers),
        "outlier_threshold_pct": threshold * 100,
    }
    return df, summary


# ---------------------------------------------------------------------------
# Station 1b - crypto prices
# ---------------------------------------------------------------------------

def load_clean_crypto() -> tuple[pd.DataFrame, dict]:
    """Return clean crypto price frame (capped at 2023-12-31) + summary."""
    df = data_access.load_crypto_prices().copy()

    # Cap at 2023-12-31 (10 stray 2024-01-01 rows in the raw data).
    df = df[df["date"] <= "2023-12-31"].copy()

    tickers = df["ticker"].unique()
    date_min, date_max = df["date"].min(), df["date"].max()
    all_days = pd.date_range(date_min, date_max, freq="D")
    full_index = pd.MultiIndex.from_product([tickers, all_days],
                                            names=["ticker", "date"])
    observed = pd.MultiIndex.from_frame(df[["ticker", "date"]])
    n_missing_dates = len(full_index.difference(observed))

    dup_mask = df.duplicated(subset=["ticker", "date"], keep=False)
    n_dups = dup_mask.sum()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")

    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["ret"] = (
        df.groupby("ticker")["adjClose"]
          .pct_change()
    )

    threshold = 0.50  # crypto can swing further
    outlier_mask = df["ret"].abs() > threshold
    outliers = df.loc[outlier_mask, ["ticker", "date", "adjClose", "ret"]].copy()

    summary = {
        "n_tickers": len(tickers),
        "date_range": f"{date_min.date()} – {date_max.date()}",
        "total_rows_raw": len(df) + n_dups,
        "duplicate_rows_removed": n_dups,
        "missing_calendar_days": n_missing_dates,
        "outlier_rows_kept": len(outliers),
        "outlier_threshold_pct": threshold * 100,
    }
    return df, summary


# ---------------------------------------------------------------------------
# Station 1c - news headlines
# ---------------------------------------------------------------------------

def load_clean_news() -> tuple[pd.DataFrame, dict]:
    """Return deduplicated news frame with tz-normalised dates."""
    df = data_access.load_news_headlines().copy()
    n_raw = len(df)

    # Normalise timezone: UTC → tz-naive date column for merge compatibility.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)

    # Deduplicate on ticker + date + title (not ticker+date alone).
    dup_mask = df.duplicated(subset=["ticker", "date", "title"], keep=False)
    n_dups = dup_mask.sum() // 2 if dup_mask.sum() % 2 == 0 else dup_mask.sum() - df.duplicated(subset=["ticker", "date", "title"], keep="first").sum()
    n_before_dedup = len(df)
    df = df.drop_duplicates(subset=["ticker", "date", "title"], keep="first")
    n_after_dedup = len(df)
    n_removed = n_before_dedup - n_after_dedup

    summary = {
        "total_rows_raw": n_raw,
        "duplicate_rows_removed": n_removed,
        "rows_after_dedup": n_after_dedup,
        "unique_tickers": df["ticker"].nunique(),
        "date_range": f"{df['date'].min().date()} – {df['date'].max().date()}",
    }
    return df, summary


# ---------------------------------------------------------------------------
# Calendar merge: equity + crypto combined returns panel
# ---------------------------------------------------------------------------

def build_combined_returns(
    equity_df: pd.DataFrame,
    crypto_df: pd.DataFrame,
) -> pd.DataFrame:
    """Left-merge crypto returns onto equity trading calendar.

    Key rule: compute returns within each panel FIRST, then merge.
    This drops weekend-only crypto moves (intentional: a fund trading on
    equity days could not act on them).
    """
    # Equity returns (already computed in load_clean_equities)
    eq_ret = (
        equity_df[["ticker", "date", "ret", "sector"]]
        .dropna(subset=["ret"])
        .pivot(index="date", columns="ticker", values="ret")
    )

    # Crypto returns on full 365-day calendar
    cr_ret = (
        crypto_df[["ticker", "date", "ret"]]
        .dropna(subset=["ret"])
        .pivot(index="date", columns="ticker", values="ret")
    )

    # Left-join crypto onto equity trading dates
    combined = eq_ret.join(cr_ret, how="left")
    combined.index.name = "date"
    combined.columns.name = "ticker"
    return combined
