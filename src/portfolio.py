"""Station 3 - portfolio optimisation methods (long-only, fully invested).

Five methods:
  equal_weight              - 1/N across all assets
  min_variance              - minimise portfolio variance (long-only, scipy)
  max_sharpe                - maximise Sharpe ratio (long-only, scipy, rf=0)
  risk_parity               - equalise risk contributions (long-only, scipy)
  hierarchical_risk_parity  - HRP: cluster on correlation, allocate recursively,
                              no covariance inversion (Lopez de Prado, 2016)

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


def hierarchical_risk_parity(cov: np.ndarray, corr: np.ndarray) -> np.ndarray:
    """Hierarchical Risk Parity (Lopez de Prado, 2016).

    Clusters assets on correlation structure and allocates risk recursively without
    ever inverting the covariance matrix, which makes it robust to the estimation
    error that destabilises min-variance / max-Sharpe on noisy sample covariances.

    Parameters
    ----------
    cov  : (n x n) sample covariance matrix (used for variances / cluster variance)
    corr : (n x n) sample correlation matrix (used for clustering)

    Long-only weights summing to 1 by construction (inverse-variance weights are
    always positive), so no clipping/renormalisation is needed.
    """
    from scipy.cluster.hierarchy import linkage, dendrogram
    from scipy.spatial.distance import pdist

    n = len(cov)
    if n == 1:
        return np.array([1.0])
    Sigma = _clean_cov(cov)

    # --- Step 1: tree clustering ------------------------------------------------
    # Correlation -> distance metric in [0, 1]: d = sqrt(0.5 * (1 - corr)).
    c = np.clip(corr, -1.0, 1.0)
    d = np.sqrt(0.5 * (1.0 - c))
    # Second-order distance: Euclidean distance between COLUMNS of d (how similarly
    # i and j relate to everything else). pdist(d.T) is exactly that, in condensed form.
    d_bar = pdist(d.T)
    link = linkage(d_bar, method="single")   # single linkage, as in the paper

    # --- Step 2: quasi-diagonalisation (leaf order) -----------------------------
    order = dendrogram(link, no_plot=True)["leaves"]

    # --- Step 3: recursive bisection --------------------------------------------
    def _cluster_var(items):
        sub = Sigma[np.ix_(items, items)]
        ivp = 1.0 / np.diag(sub)          # inverse-variance weights within the side
        ivp /= ivp.sum()
        return float(ivp @ sub @ ivp)

    w = np.ones(n)
    clusters = [order]
    while clusters:
        nxt = []
        for cl in clusters:
            if len(cl) <= 1:
                continue
            mid = len(cl) // 2
            left, right = cl[:mid], cl[mid:]
            cv_l, cv_r = _cluster_var(left), _cluster_var(right)
            # lower-variance side gets the larger share of the parent's weight
            alpha = 1.0 - cv_l / (cv_l + cv_r)
            for i in left:
                w[i] *= alpha
            for i in right:
                w[i] *= (1.0 - alpha)
            nxt += [left, right]
        clusters = nxt

    assert np.all(w >= -1e-12) and abs(w.sum() - 1.0) < 1e-8, "HRP weights invalid"
    return w
