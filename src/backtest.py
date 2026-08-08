"""Station 3 - walk-forward out-of-sample backtest.

Design:
  - Estimation window : 252 trading days (1 year)
  - Rebalance         : first trading day of each calendar month
  - No look-ahead     : weights formed only from past data
  - Long-only         : all weights >= 0, sum = 1
  - Risk-free rate    : 0 (stated assumption)
  - Transaction costs : 0 (stated assumption)

Fund families and methods:
  equity_ew      equity_mv      equity_ms      equity_rp
  crypto_ew      crypto_mv      crypto_ms      crypto_rp
  combined_ew    combined_mv    combined_ms    combined_rp
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from src.portfolio import equal_weight, min_variance, max_sharpe, risk_parity

ESTIMATION_WINDOW = 252   # trading days
RF = 0.0                  # risk-free rate (daily)
ANNUALISE = 252           # all panels are on equity trading calendar


@dataclass
class FundResult:
    name: str
    family: str           # equity / crypto / combined
    method: str           # ew / mv / ms / rp
    returns: pd.Series    # daily out-of-sample returns, DatetimeIndex
    weights: pd.DataFrame # (rebalance_date x ticker), NaN between rebalances

    # Computed on demand
    def ann_return(self) -> float:
        return float(self.returns.mean() * ANNUALISE)

    def ann_vol(self) -> float:
        return float(self.returns.std() * np.sqrt(ANNUALISE))

    def sharpe(self) -> float:
        v = self.ann_vol()
        return self.ann_return() / v if v > 1e-12 else 0.0

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
) -> np.ndarray:
    """Compute weights for the next period given a window of past returns."""
    ret_window = ret_window.dropna(axis=1, how="any")
    tickers = ret_window.columns.tolist()
    if len(tickers) == 0:
        return np.array([])

    mu = ret_window.mean().values
    cov = ret_window.cov().values

    try:
        if method == "ew":
            w = equal_weight(len(tickers))
        elif method == "mv":
            w = min_variance(cov)
        elif method == "ms":
            w = max_sharpe(mu, cov, rf=RF)
        elif method == "rp":
            w = risk_parity(cov)
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
) -> FundResult:
    """Run a walk-forward backtest for one (family, method) fund.

    Parameters
    ----------
    returns : wide DataFrame (date x ticker), daily returns, no NaN in date axis
    family  : 'equity', 'crypto', or 'combined'
    method  : 'ew', 'mv', 'ms', or 'rp'
    """
    all_dates = returns.index
    n = len(all_dates)

    if n <= estimation_window:
        raise ValueError(f"Not enough data ({n} days) for window {estimation_window}")

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
            current_weights = _compute_weights(window, method)

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
    }
    family_label = {"equity": "Equity", "crypto": "Crypto", "combined": "Combined"}
    name = f"{family_label.get(family, family)} {label_map.get(method, method)}"

    return FundResult(
        name=name,
        family=family,
        method=method,
        returns=ret_series,
        weights=weights_df,
    )


def run_all_funds(
    equity_ret: pd.DataFrame,
    crypto_ret: pd.DataFrame,
    combined_ret: pd.DataFrame,
    methods: list[str] | None = None,
    families: list[str] | None = None,
) -> list[FundResult]:
    """Run backtests for all (family, method) combinations."""
    if methods is None:
        methods = ["ew", "mv", "ms", "rp"]
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
                fund = run_backtest(panel, family, method)
                results.append(fund)
            except Exception as exc:
                print(f"    SKIP {family} {method}: {exc}")
    return results
