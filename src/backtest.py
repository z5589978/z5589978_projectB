"""Station 3 - walk-forward out-of-sample backtest.

Design:
  - Estimation window : 252 trading days (1 year)
  - Rebalance         : first trading day of each calendar month
  - No look-ahead     : weights formed only from past data
  - Long-only         : all weights >= 0, sum = 1
  - Risk-free rate    : daily 1-month T-bill proxy (Fama/French 5 Factors daily RF,
                        Kenneth French Data Library, 2020-01-02 to 2023-12-29).
                        Forward-filled onto crypto funds' non-trading days.
  - Transaction costs : 0 (stated assumption)

Fund families and methods (5 methods x 3 families = 15 funds):
  equity_ew    equity_mv    equity_ms    equity_rp    equity_hrp
  crypto_ew    crypto_mv    crypto_ms    crypto_rp    crypto_hrp
  combined_ew  combined_mv  combined_ms  combined_rp  combined_hrp
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from src.portfolio import (equal_weight, min_variance, max_sharpe, risk_parity,
                           hierarchical_risk_parity)

ESTIMATION_WINDOW = 252   # trading days
RF = 0.0                  # fallback daily risk-free rate if the RF file is missing
ANNUALISE = 252           # equity/combined funds sit on the equity trading calendar
ANNUALISE_CRYPTO = 365    # crypto-only funds trade all 365 calendar days

# Fama/French 5 Factors (daily) RF column, Kenneth French Data Library, filtered to
# 2020-01-02..2023-12-29. `rf` is already the decimal daily rate.
RF_CSV = (pathlib.Path(__file__).resolve().parent.parent
          / "data" / "external" / "ff_rf_daily_2020_2023.csv")


def load_rf_daily(path: str | pathlib.Path | None = None) -> pd.Series:
    """Daily risk-free rate (decimal), indexed by date, on the equity trading calendar.

    Source: Fama/French 5 Factors (daily) RF column, Kenneth French Data Library.
    Returns an empty Series if the file is absent, so callers fall back to RF = 0.
    """
    p = pathlib.Path(path) if path is not None else RF_CSV
    if not p.exists():
        return pd.Series(dtype=float)
    df = pd.read_csv(p, parse_dates=["date"])
    return df.set_index("date")["rf"].astype(float).sort_index()


def align_rf(rf: pd.Series, dates: pd.DatetimeIndex) -> pd.Series:
    """Align the trading-day RF series onto an arbitrary date index.

    Carries the last known trading-day rate forward across non-trading days
    (weekends/holidays). Crypto funds trade all 365 calendar days, so ~31% of their
    dates have no own-day RF in the equity-sourced file; forward-fill applies the
    prevailing short rate to them (a short rate barely moves over a weekend). Equity
    and combined funds share the file's calendar, so this is a no-op for them. Any
    leading gap before the RF sample starts falls back to 0 (neutral).
    """
    dates = pd.DatetimeIndex(dates)
    if rf is None or rf.empty:
        return pd.Series(0.0, index=dates)
    union = rf.index.union(dates)
    return rf.reindex(union).ffill().reindex(dates).fillna(0.0)


@dataclass
class FundResult:
    name: str
    family: str           # equity / crypto / combined
    method: str           # ew / mv / ms / rp
    returns: pd.Series    # daily out-of-sample returns, DatetimeIndex
    weights: pd.DataFrame # (rebalance_date x ticker), NaN between rebalances
    rf: pd.Series | None = None  # daily risk-free rate aligned to `returns` dates

    @property
    def ann_factor(self) -> int:
        """Annualisation factor for this fund's calendar: 365 for crypto-only funds
        (they trade every calendar day), 252 for equity and combined funds (both sit
        on the equity trading calendar). See CLAUDE.md coding rule 2."""
        return ANNUALISE_CRYPTO if self.family == "crypto" else ANNUALISE

    # Computed on demand
    def ann_return(self) -> float:
        return float(self.returns.mean() * self.ann_factor)

    def ann_vol(self) -> float:
        return float(self.returns.std() * np.sqrt(self.ann_factor))

    def sharpe(self) -> float:
        """Annualised excess-return Sharpe: mean(daily return - daily RF) x the fund's
        annualisation factor (252 for equity/combined, 365 for crypto), divided by the
        fund's annualised volatility. RF is aligned per fund (this fund's own date
        range), forward-filled onto crypto non-trading days. Falls back to a zero RF
        only if no RF series was attached."""
        v = self.ann_vol()
        if v <= 1e-12:
            return 0.0
        if self.rf is None:
            excess = self.returns
        else:
            rf_aligned = self.rf.reindex(self.returns.index).fillna(0.0)
            excess = self.returns - rf_aligned
        return float(excess.mean() * self.ann_factor) / v

    def max_drawdown(self) -> float:
        wealth = (1 + self.returns).cumprod()
        roll_max = wealth.cummax()
        dd = (wealth - roll_max) / roll_max
        return float(dd.min())

    def metrics(self) -> dict:
        return {
            "fund": self.name,
            "family": self.family,
            "method": self.method,
            "ann_return": self.ann_return(),
            "ann_vol": self.ann_vol(),
            "sharpe": self.sharpe(),
            "max_drawdown": self.max_drawdown(),
            "start_date": str(self.returns.index[0].date()),
            "end_date": str(self.returns.index[-1].date()),
            "n_days": len(self.returns),
        }


def _rebalance_dates(all_dates: pd.DatetimeIndex, start_idx: int) -> list[int]:
    """Return indices in all_dates where we rebalance (first day of each month)."""
    dates = pd.Series(all_dates, name="date")
    is_month_start = dates.dt.to_period("M") != dates.dt.to_period("M").shift(1)
    indices = [i for i in range(start_idx, len(all_dates)) if is_month_start.iloc[i]]
    # Always include the very first live day
    if not indices or indices[0] != start_idx:
        indices.insert(0, start_idx)
    return indices


def _compute_weights(
    ret_window: pd.DataFrame,
    method: str,
    rf: float = 0.0,
) -> np.ndarray:
    """Compute weights for the next period given a window of past returns.

    `rf` is the mean daily risk-free rate over this estimation window; it enters the
    Max-Sharpe objective only. The other four methods ignore it, so their weights are
    unchanged by the risk-free rate.
    """
    ret_window = ret_window.dropna(axis=1, how="any")
    tickers = ret_window.columns.tolist()
    if len(tickers) == 0:
        return np.array([])

    mu = ret_window.mean().values
    cov = ret_window.cov().values
    corr = ret_window.corr().values   # HRP clusters on correlation structure

    try:
        if method == "ew":
            w = equal_weight(len(tickers))
        elif method == "mv":
            w = min_variance(cov)
        elif method == "ms":
            w = max_sharpe(mu, cov, rf=rf)
        elif method == "rp":
            w = risk_parity(cov)
        elif method == "hrp":
            w = hierarchical_risk_parity(cov, corr)
        else:
            raise ValueError(f"Unknown method: {method}")
    except Exception:
        w = equal_weight(len(tickers))

    return pd.Series(w, index=tickers)


def run_backtest(
    returns: pd.DataFrame,
    family: str,
    method: str,
    estimation_window: int = ESTIMATION_WINDOW,
    rf: pd.Series | None = None,
) -> FundResult:
    """Run a walk-forward backtest for one (family, method) fund.

    Parameters
    ----------
    returns : wide DataFrame (date x ticker), daily returns, no NaN in date axis
    family  : 'equity', 'crypto', or 'combined'
    method  : 'ew', 'mv', 'ms', or 'rp'
    rf      : daily risk-free rate (decimal), trading-day indexed. Aligned to this
              panel's calendar (forward-filled for crypto). If None, RF = 0 is used.
    """
    all_dates = returns.index
    n = len(all_dates)

    if n <= estimation_window:
        raise ValueError(f"Not enough data ({n} days) for window {estimation_window}")

    # Align RF onto this panel's calendar once (no-op for equity/combined; forward-fill
    # across weekends/holidays for crypto's 365-day calendar).
    rf_aligned = align_rf(rf, all_dates) if rf is not None else None

    first_live = estimation_window  # first index we produce a live return
    rebal_idx  = _rebalance_dates(all_dates, first_live)

    # Storage
    port_returns = []
    weights_records = []
    current_weights = pd.Series(dtype=float)

    for i in range(first_live, n):
        # Rebalance?
        if i in rebal_idx:
            window = returns.iloc[i - estimation_window : i]
            # Mean daily RF over the same 252-day estimation window (past data only,
            # no look-ahead). Used by Max-Sharpe; ignored by the other methods.
            if rf_aligned is not None:
                rf_win = float(rf_aligned.iloc[i - estimation_window : i].mean())
            else:
                rf_win = RF
            current_weights = _compute_weights(window, method, rf=rf_win)

        # Daily return: dot current weights with available asset returns
        day_ret_raw = returns.iloc[i]
        common = current_weights.index.intersection(day_ret_raw.index)
        if len(common) == 0 or current_weights[common].sum() < 1e-12:
            port_ret = 0.0
        else:
            w_sub = current_weights[common]
            w_sub = w_sub / w_sub.sum()
            port_ret = float((w_sub * day_ret_raw[common].fillna(0.0)).sum())

        port_returns.append((all_dates[i], port_ret))

        # Record weights on rebalance days
        if i in rebal_idx:
            row = current_weights.to_dict()
            row["date"] = all_dates[i]
            weights_records.append(row)

    ret_series = pd.Series(
        [r for _, r in port_returns],
        index=pd.DatetimeIndex([d for d, _ in port_returns]),
        name=f"{family}_{method}",
    )
    weights_df = (
        pd.DataFrame(weights_records).set_index("date")
        if weights_records else pd.DataFrame()
    )

    label_map = {
        "ew": "Equal Weight",
        "mv": "Min Variance",
        "ms": "Max Sharpe",
        "rp": "Risk Parity",
        "hrp": "Hierarchical Risk Parity",
    }
    family_label = {"equity": "Equity", "crypto": "Crypto", "combined": "Combined"}
    name = f"{family_label.get(family, family)} {label_map.get(method, method)}"

    fund_rf = (rf_aligned.reindex(ret_series.index)
               if rf_aligned is not None else None)

    return FundResult(
        name=name,
        family=family,
        method=method,
        returns=ret_series,
        weights=weights_df,
        rf=fund_rf,
    )


def run_all_funds(
    equity_ret: pd.DataFrame,
    crypto_ret: pd.DataFrame,
    combined_ret: pd.DataFrame,
    methods: list[str] | None = None,
    families: list[str] | None = None,
    rf: pd.Series | None = None,
) -> list[FundResult]:
    """Run backtests for all (family, method) combinations.

    `rf` is the trading-day daily risk-free rate; each fund aligns it to its own
    calendar (forward-filled for crypto). If None, RF = 0 is used throughout.
    """
    if methods is None:
        methods = ["ew", "mv", "ms", "rp", "hrp"]
    if families is None:
        families = ["equity", "crypto", "combined"]

    panel_map = {
        "equity": equity_ret,
        "crypto": crypto_ret,
        "combined": combined_ret,
    }
    results = []
    for family in families:
        panel = panel_map[family]
        for method in methods:
            print(f"  Backtesting {family} {method} …")
            try:
                fund = run_backtest(panel, family, method, rf=rf)
                results.append(fund)
            except Exception as exc:
                print(f"    SKIP {family} {method}: {exc}")
    return results
