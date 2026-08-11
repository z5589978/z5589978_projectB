# Prompt Log 12 - Add Hierarchical Risk Parity (HRP) as a 5th method

**Session date:** 2026-08-12
**Task:** Add Hierarchical Risk Parity (López de Prado 2016) as a fifth portfolio
optimisation method alongside EW / MV / MS / RP, matching the existing code style.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Add Hierarchical Risk Parity as a Fifth Portfolio Method
>
> I want to add Hierarchical Risk Parity (HRP) as a fifth optimisation method alongside our existing four (equal-weight, min-variance, max-Sharpe, risk parity). This is López de Prado, M. (2016), "Building Diversified Portfolios that Outperform Out-of-Sample," The Journal of Portfolio Management, 42(4), 59-69 (DOI: 10.3905/jpm.2016.42.4.059) — it addresses the instability of mean-variance-style optimisers on noisy covariance estimates ... by clustering assets on correlation structure and allocating recursively, without ever inverting the covariance matrix.
>
> [Step 1: read src/portfolio.py (4 fns, cov in, 1-D long-only weights out) and backtest.py's _compute_weights dispatch + run_all_funds; follow the exact style/integration.
> Step 2: implement hierarchical_risk_parity(cov, corr) with all 3 steps — tree clustering (d=sqrt(0.5*(1-corr)); second-order d_bar = Euclidean between columns of d; single-linkage), quasi-diagonalisation (dendrogram leaves), recursive bisection (inverse-variance within side; alpha=1-cv_l/(cv_l+cv_r); product of alphas down the path). Assert long-only & sums to 1, no needless clip/renorm. Update _compute_weights to pass ret_window.corr().values.
> Step 3: synthetic two-cluster validation — sums to 1, all>=0; less weight to higher-variance cluster; similar-in-spirit-but-not-identical to risk_parity. Show it passing.
> Step 4: wire "hrp" into dispatch, label_map ("Hierarchical Risk Parity"), run_all_funds default methods; update docstrings; re-run run_part_b.py so all *_hrp funds + figures regenerate. Note whether tilting against HRP is interesting (don't do unprompted).
> Step 5: add HRP funds to the app views; update PROJECT.md to five methods.
> Step 6: prepare a plain-language methodology description + citation for the report; do NOT write the economic interpretation of HRP's relative performance.
> Step 7: streamlit run + check_handin + commit/push; log verbatim prompt, validation results, HRP vs existing performance.]

---

## Step 2/3 — implementation + synthetic validation (PASSED)

`hierarchical_risk_parity(cov, corr)` added to src/portfolio.py (all 3 steps; uses
scipy pdist(d.T) for the second-order distance, single-linkage, dendrogram leaves,
iterative recursive bisection; assertion instead of clip/renorm). Synthetic test:
2 clusters {0,1} low-variance, {2,3} high-variance, ~0 cross-correlation:
- (a) weights sum to 1, all >= 0 -> True
- (b) low-var cluster weight 0.901 > high-var cluster 0.099 -> True (less to higher-variance)
- (c) same ranking as risk_parity (rank corr 1.00) but NOT identical (HRP 90/10 vs RP
  75/25) -> HRP concentrates more in the low-variance cluster because it splits weight
  BETWEEN clusters by cluster variance, which plain risk parity does not do.

## Step 4 — performance: HRP vs the existing four (OOS 2021-2023, √252, rf=0)

| family | ew | mv | ms | rp | **hrp** |
|--------|----|----|----|----|---------|
| equity Sharpe   | 0.817 | 0.490 | 0.587 | 0.724 | **0.674** |
| equity ann.vol  | 0.162 | 0.128 | 0.182 | 0.146 | **0.137** |
| crypto Sharpe   | 0.758 | 1.047 | 0.224 | 0.801 | **0.839** |
| crypto ann.vol  | 0.669 | 0.537 | 0.642 | 0.651 | **0.629** |
| combined Sharpe | 0.763 | 0.494 | 1.033 | 0.896 | **0.741** |
| combined ann.vol| 0.212 | 0.128 | 0.246 | 0.160 | **0.140** |

(The economic interpretation of *how HRP performed relative to the others* is for the
student to write. Mechanics only here: HRP produces low-vol, diversified portfolios
sitting broadly between risk-parity and min-variance, without inverting the covariance
matrix. The existing 4 methods' numbers are unchanged — deterministic — confirming HRP
was added without perturbing them.)

Fusion base is still Equity Max-Sharpe (0.587 -> 0.602, +0.015; unchanged).
**Optional idea flagged, NOT done:** testing the sentiment tilt against an HRP base
(lower-turnover, more diversified than Max-Sharpe) could show whether the tilt helps a
stable base differently — worth a follow-up only if the student wants it.

---

## Report methodology description (mechanics for the funds/methodology section)

**Hierarchical Risk Parity (HRP)** — López de Prado, M. (2016), "Building Diversified
Portfolios that Outperform Out-of-Sample," *Journal of Portfolio Management* 42(4),
59-69, DOI 10.3905/jpm.2016.42.4.059.

HRP allocates risk using the correlation structure of the assets and never inverts the
covariance matrix, which is what makes mean-variance-style optimisers unstable on the
noisy sample covariances estimated from a 252-day window. Three steps:

1. **Tree clustering.** Turn the correlation matrix into a distance,
   d(i,j) = sqrt(0.5·(1 − corr(i,j))) (a proper metric in [0,1]); then take a
   second-order distance — the Euclidean distance between the *columns* of d — so
   assets are judged similar when they relate to *everything else* the same way, not
   just to each other. Single-linkage hierarchical clustering on that gives a tree.
2. **Quasi-diagonalisation.** Reorder the assets to the tree's leaf order, which places
   correlated assets next to each other (so the reordered covariance is roughly
   block-diagonal).
3. **Recursive bisection.** Start with the whole ordered list holding weight 1.
   Repeatedly split each cluster in half (in the quasi-diagonal order); for each side
   compute an inverse-variance weight vector and its cluster variance
   w_i ∝ 1/var_i, cluster_var = wᵀ·cov·w; give the parent's weight to the two sides in
   proportion α = 1 − cluster_var_left / (cluster_var_left + cluster_var_right) (the
   lower-variance side gets more), and recurse until each cluster is a single asset.
   Each asset's final weight is the product of the α's along its path down the tree —
   positive by construction, summing to 1, so long-only with no extra normalisation.

## Step 5/7 — app, checks

- App is data-driven: the 3 HRP funds auto-appear in Compare Funds, Fund Fact Sheet
  (selector), and My Allocation from performance_metrics.csv / fund_returns.csv. Figure
  palettes (METHOD_COLOR/LABEL) got an "hrp" entry (VIOLET / "HRP") so figures don't
  KeyError. All 5 app pages pass headless AppTest.
- check_handin: passes. Committed.
