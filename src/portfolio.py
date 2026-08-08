"""Station 3 - portfolio optimisation methods (long-only, fully invested).

Four methods:
  equal_weight     - 1/N across all assets
  min_variance     - minimise portfolio variance (long-only, scipy)
  max_sharpe       - maximise Sharpe ratio (long-only, scipy, rf=0)
  risk_parity      - equalise risk contributions (long-only, scipy)

All return a 1-D numpy array of weights that sum to 1 with w_i >= 0.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def _clean_cov(cov: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """Add a small diagonal ridge for numerical stability."""
    return cov + np.eye(len(cov)) * ridge


def equal_weight(n: int) -> np.ndarray:
    return np.full(n, 1.0 / n)


def min_variance(cov: np.ndarray) -> np.ndarray:
    n = len(cov)
    Sigma = _clean_cov(cov)

    def objective(w):
        return float(w @ Sigma @ w)

    def grad(w):
        return 2.0 * Sigma @ w

    result = minimize(
        objective,
        x0=equal_weight(n),
        jac=grad,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * n,
        constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
        options={"ftol": 1e-12, "maxiter": 500},
    )
    w = np.clip(result.x, 0.0, 1.0)
    s = w.sum()
    return w / s if s > 1e-12 else equal_weight(n)


def max_sharpe(mu: np.ndarray, cov: np.ndarray, rf: float = 0.0) -> np.ndarray:
    n = len(mu)
    Sigma = _clean_cov(cov)
    excess = mu - rf

    def neg_sharpe(w):
        port_ret = float(w @ excess)
        port_vol = float(np.sqrt(w @ Sigma @ w))
        if port_vol < 1e-12:
            return 1e6
        return -port_ret / port_vol

    result = minimize(
        neg_sharpe,
        x0=equal_weight(n),
        method="SLSQP",
        bounds=[(0.0, 1.0)] * n,
        constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
        options={"ftol": 1e-12, "maxiter": 500},
    )
    w = np.clip(result.x, 0.0, 1.0)
    s = w.sum()
    return w / s if s > 1e-12 else equal_weight(n)


def risk_parity(cov: np.ndarray) -> np.ndarray:
    """Equal risk contribution portfolio."""
    n = len(cov)
    Sigma = _clean_cov(cov)
    target = np.full(n, 1.0 / n)

    def objective(w):
        port_var = float(w @ Sigma @ w)
        if port_var < 1e-24:
            return 1e6
        mrc = Sigma @ w          # marginal risk contributions
        rc = w * mrc / port_var  # fractional risk contributions
        return float(np.sum((rc - target) ** 2))

    result = minimize(
        objective,
        x0=equal_weight(n),
        method="SLSQP",
        bounds=[(1e-6, 1.0)] * n,
        constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
        options={"ftol": 1e-14, "maxiter": 1000},
    )
    w = np.clip(result.x, 0.0, 1.0)
    s = w.sum()
    return w / s if s > 1e-12 else equal_weight(n)
