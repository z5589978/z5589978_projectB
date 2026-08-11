"""Reproduce all Part B results. Run from the project root:

    python scripts/run_part_b.py

Generates:
    results/data/fund_returns.csv          (required)
    results/data/fund_weights.csv          (required)
    results/data/sector_sentiment_index.csv (required)
    results/tables/performance_metrics.csv  (required)
    results/figures/cumret_by_family.png
    results/figures/drawdown_combined.png
    results/figures/weights_over_time.png
    results/figures/sharpe_barplot.png
    results/figures/sector_sentiment.png
    results/figures/fusion_comparison.png
"""
from __future__ import annotations

import pathlib
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore", message=".*No runtime found.*")

from src.etl import load_clean_equities, load_clean_crypto, load_clean_news, build_combined_returns
from src.features import daily_returns, assemble_headline_panel
from src.backtest import run_all_funds, run_backtest, ANNUALISE
from src.sentiment import score_headlines, build_ticker_sentiment, build_sector_sentiment, build_sentiment_tilt

RESULTS = ROOT / "results"
TABLES  = RESULTS / "tables"
FIGURES = RESULTS / "figures"
DATA    = RESULTS / "data"
for d in [TABLES, FIGURES, DATA]:
    d.mkdir(parents=True, exist_ok=True)

# ── FINS palette ─────────────────────────────────────────────────────────────
NAVY    = "#1F3A5F"
CRIMSON = "#B23A48"
FOREST  = "#2E7D32"
GOLD    = "#C99700"
TEAL    = "#007C89"
VIOLET  = "#6B5B95"
STEEL   = "#4A5568"
COLORS  = [NAVY, CRIMSON, FOREST, GOLD, TEAL, VIOLET, STEEL, "#8B4513"]

METHOD_COLOR = {"ew": STEEL, "mv": NAVY, "ms": FOREST, "rp": CRIMSON, "hrp": VIOLET}
METHOD_LABEL = {
    "ew": "Equal Weight",
    "mv": "Min Variance",
    "ms": "Max Sharpe",
    "rp": "Risk Parity",
    "hrp": "HRP",
}

def _style():
    return {
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.dpi": 150,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 1. Load and clean data (Part A pipeline)
# ═══════════════════════════════════════════════════════════════════════════
print("=== Station 3 Part B ===")
print("Loading data …")
eq, _  = load_clean_equities()
cr, _  = load_clean_crypto()
news, _ = load_clean_news()

sector_map = eq[["ticker", "sector"]].drop_duplicates().set_index("ticker")["sector"].to_dict()
trading_dates = pd.DatetimeIndex(sorted(eq["date"].unique()))

# Returns panels (wide: date x ticker)
eq_ret_long = daily_returns(eq)
cr_ret_long = daily_returns(cr)

eq_ret = eq_ret_long.pivot(index="date", columns="ticker", values="ret").sort_index()
cr_ret = cr_ret_long.pivot(index="date", columns="ticker", values="ret").sort_index()
combined_ret = build_combined_returns(eq, cr)

print(f"Equity panel  : {eq_ret.shape}")
print(f"Crypto panel  : {cr_ret.shape}")
print(f"Combined panel: {combined_ret.shape}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Run walk-forward backtests for all funds
# ═══════════════════════════════════════════════════════════════════════════
print("\nRunning backtests (252-day window, monthly rebalance) …")
funds = run_all_funds(eq_ret, cr_ret, combined_ret)
print(f"  {len(funds)} funds completed.")


# ═══════════════════════════════════════════════════════════════════════════
# 3. Save required outputs: fund_returns.csv, fund_weights.csv
# ═══════════════════════════════════════════════════════════════════════════
# fund_returns.csv: one column per fund, date index
ret_wide = pd.DataFrame({f.name: f.returns for f in funds})
ret_wide.index.name = "date"
ret_wide.to_csv(DATA / "fund_returns.csv")
print("Saved results/data/fund_returns.csv")

# fund_weights.csv: long format (date, fund, ticker, weight)
weight_rows = []
for f in funds:
    if f.weights.empty:
        continue
    for date, row in f.weights.iterrows():
        for ticker, w in row.dropna().items():
            if w > 1e-6:
                weight_rows.append({"date": date, "fund": f.name, "ticker": ticker, "weight": round(w, 6)})
weights_long = pd.DataFrame(weight_rows)
weights_long.to_csv(DATA / "fund_weights.csv", index=False)
print("Saved results/data/fund_weights.csv")

# performance_metrics.csv
metrics_rows = [f.metrics() for f in funds]
metrics_df = pd.DataFrame(metrics_rows)
for col in ["ann_return", "ann_vol", "sharpe", "max_drawdown"]:
    metrics_df[col] = metrics_df[col].round(4)
metrics_df.to_csv(TABLES / "performance_metrics.csv", index=False)
print("Saved results/tables/performance_metrics.csv")

print("\nFund performance summary:")
print(metrics_df[["fund", "ann_return", "ann_vol", "sharpe", "max_drawdown"]].to_string(index=False))


# ═══════════════════════════════════════════════════════════════════════════
# 4. VADER sentiment model
# ═══════════════════════════════════════════════════════════════════════════
print("\nScoring headlines with VADER …")
scored = score_headlines(news)
print(f"  Scored {len(scored):,} headlines. Mean compound = {scored['compound'].mean():.4f}")

ticker_sent  = build_ticker_sentiment(scored, trading_dates)
sector_sent  = build_sector_sentiment(ticker_sent, sector_map, trading_dates)

# Save required output
sector_sent.index.name = "date"
sector_sent.to_csv(DATA / "sector_sentiment_index.csv")
print("Saved results/data/sector_sentiment_index.csv")

# ── Week 9 index-construction deliverables (standalone fear/greed exhibits) ───
# Market-wide aggregate index, 0-100 rescale, coverage analysis, and look-ahead-safe
# (expanding-window) standardisation. These describe the index; the tilt keeps its
# own same-day cross-sectional median split.
from src.sentiment import (to_score_100, build_aggregate_sentiment,
                           standardise_expanding, sentiment_coverage, z_band_label)

coverage = sentiment_coverage(ticker_sent, sector_map, trading_dates)
coverage.to_csv(TABLES / "sentiment_coverage.csv", index=False)
print("Saved results/tables/sentiment_coverage.csv")
print(coverage.to_string(index=False))

agg_sent = build_aggregate_sentiment(ticker_sent, trading_dates)
agg = pd.DataFrame({"compound": agg_sent})
agg["score_100"] = to_score_100(agg["compound"])
agg["z_expanding"] = standardise_expanding(agg["score_100"])
agg["z_full"] = (agg["score_100"] - agg["score_100"].mean()) / agg["score_100"].std()
agg["band"] = agg["z_expanding"].apply(z_band_label)
agg.index.name = "date"
agg.to_csv(DATA / "aggregate_sentiment_index.csv")
print("Saved results/data/aggregate_sentiment_index.csv")

_below50 = float((agg["score_100"] < 50).mean() * 100)
_ov = agg.dropna(subset=["z_expanding"])
_corr = float(_ov["z_expanding"].corr(_ov["z_full"]))
print(f"  aggregate index below 50 on {_below50:.1f}% of days (levels say 'greed' "
      f"almost always -> standardise); expanding vs full-sample z corr = {_corr:.3f}")


# ═══════════════════════════════════════════════════════════════════════════
# 5. Sentiment-fusion: equity Max Sharpe base vs tilted
# ═══════════════════════════════════════════════════════════════════════════
print("\nBuilding sentiment fusion fund …")

# Base fund: equity max sharpe
base_fund = next(f for f in funds if f.family == "equity" and f.method == "ms")

# Build tilted weights
tilted_weights = build_sentiment_tilt(
    base_fund.weights, sector_sent, sector_map, alpha=0.10
)

# Run return stream with tilted weights
fusion_ret_list = []
all_dates_eq = eq_ret.index
for i, date in enumerate(base_fund.returns.index):
    day_ret_raw = eq_ret.loc[date] if date in eq_ret.index else pd.Series(dtype=float)
    # Find the most recent rebalance weight <= date
    past = tilted_weights.index[tilted_weights.index <= date]
    if len(past) == 0 or day_ret_raw.empty:
        fusion_ret_list.append(0.0)
        continue
    w_row = tilted_weights.loc[past[-1]].dropna()
    common = w_row.index.intersection(day_ret_raw.index)
    if len(common) == 0:
        fusion_ret_list.append(0.0)
        continue
    w_sub = w_row[common]; w_sub = w_sub / w_sub.sum()
    fusion_ret_list.append(float((w_sub * day_ret_raw[common].fillna(0.0)).sum()))

fusion_ret = pd.Series(fusion_ret_list, index=base_fund.returns.index, name="Equity MS + Sentiment")


# ═══════════════════════════════════════════════════════════════════════════
# 6. Figures
# ═══════════════════════════════════════════════════════════════════════════

def _cumret(returns: pd.Series, base: float = 1.0) -> pd.Series:
    return (1 + returns).cumprod() * base

def _drawdown(returns: pd.Series) -> pd.Series:
    wealth = (1 + returns).cumprod()
    return (wealth - wealth.cummax()) / wealth.cummax()


# ── Figure 1: Cumulative returns by family (one panel per family) ──────────
print("\nGenerating figures …")
families = ["equity", "crypto", "combined"]
family_labels = {"equity": "Equity funds", "crypto": "Crypto funds", "combined": "Combined funds"}

with plt.rc_context(_style()):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, fam in zip(axes, families):
        fam_funds = [f for f in funds if f.family == fam]
        for f in fam_funds:
            c = METHOD_COLOR[f.method]
            wealth = _cumret(f.returns)
            ax.plot(wealth.index, wealth.values, label=METHOD_LABEL[f.method], color=c, lw=1.6)
        ax.axhline(1, color="gray", lw=0.7, ls="--")
        ax.set_title(family_labels[fam], fontsize=10, fontweight="bold")
        ax.set_xlabel("Date")
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))
        if fam == "equity":
            ax.set_ylabel("Growth of $1")
        ax.legend(fontsize=7)
    fig.suptitle("Figure 1. Cumulative return (growth of $1) by fund family, 2021–2023\n"
                 "(252-day estimation window, monthly rebalance, long-only, rf = 0)", fontsize=10, y=1.02)
    fig.text(0.5, -0.02, "Source: FINS3645 project data bundle. Returns are out-of-sample.",
             ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "cumret_by_family.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/cumret_by_family.png")


# ── Figure 2: Drawdown — combined funds ────────────────────────────────────
with plt.rc_context(_style()):
    fig, ax = plt.subplots(figsize=(10, 4))
    comb_funds = [f for f in funds if f.family == "combined"]
    for f in comb_funds:
        dd = _drawdown(f.returns)
        ax.fill_between(dd.index, dd.values, 0, alpha=0.25, color=METHOD_COLOR[f.method])
        ax.plot(dd.index, dd.values, label=METHOD_LABEL[f.method], color=METHOD_COLOR[f.method], lw=1.4)
    ax.axhline(0, color="gray", lw=0.8)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.set_title("Figure 2. Drawdown — Combined funds, 2021–2023", fontsize=10, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Drawdown")
    ax.legend(fontsize=8)
    fig.text(0.5, -0.03, "Source: FINS3645 project data bundle. Drawdown = (cumret − rolling peak) / rolling peak.",
             ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "drawdown_combined.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/drawdown_combined.png")


# ── Figure 3: Portfolio weights over time (combined Max Sharpe) ────────────
ms_combined = next(f for f in funds if f.family == "combined" and f.method == "ms")
w_ts = ms_combined.weights.copy().fillna(0)

# Top 10 tickers by average weight
top_tickers = w_ts.mean().nlargest(10).index.tolist()
w_plot = w_ts[top_tickers]

with plt.rc_context(_style()):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bottom = np.zeros(len(w_plot))
    for i, ticker in enumerate(top_tickers):
        vals = w_plot[ticker].fillna(0).values
        ax.bar(range(len(w_plot)), vals, bottom=bottom,
               color=COLORS[i % len(COLORS)], label=ticker, width=0.9)
        bottom += vals
    ax.set_xticks(range(len(w_plot)))
    ax.set_xticklabels([d.strftime("%Y-%m") for d in w_plot.index], rotation=45, fontsize=7)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.set_ylabel("Weight")
    ax.set_title("Figure 3. Portfolio weights over time — Combined Max Sharpe fund, 2021–2023\n"
                 "(top 10 holdings shown; remaining weight in unlabelled slice)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=7, ncol=5, loc="upper right")
    fig.text(0.5, -0.06, "Source: FINS3645 project data bundle. Weights are long-only (≥ 0), "
             "sum to 1 at each monthly rebalance.", ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "weights_over_time.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/weights_over_time.png")


# ── Figure 4: Sharpe ratio barplot ─────────────────────────────────────────
with plt.rc_context(_style()):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=False)
    for ax, fam in zip(axes, families):
        fam_funds = [f for f in funds if f.family == fam]
        sharpes   = [f.sharpe() for f in fam_funds]
        labels    = [METHOD_LABEL[f.method] for f in fam_funds]
        colors    = [METHOD_COLOR[f.method] for f in fam_funds]
        bars = ax.bar(labels, sharpes, color=colors, alpha=0.85, width=0.55)
        ax.axhline(0, color="gray", lw=0.7)
        for bar, val in zip(bars, sharpes):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + 0.01 * (1 if val >= 0 else -1),
                    f"{val:.2f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
        ax.set_title(family_labels[fam], fontsize=10, fontweight="bold")
        ax.set_ylabel("Sharpe ratio (rf = 0)" if fam == "equity" else "")
        ax.tick_params(axis="x", rotation=15, labelsize=8)
    fig.suptitle("Figure 4. Out-of-sample Sharpe ratio by fund family and method, 2021–2023",
                 fontsize=10, y=1.02)
    fig.text(0.5, -0.02, "Source: FINS3645 project data bundle. Annualised with √252. Risk-free rate = 0.",
             ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "sharpe_barplot.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/sharpe_barplot.png")


# ── Figure 5: Sector sentiment index over time ─────────────────────────────
sectors = sector_sent.columns.tolist()
with plt.rc_context(_style()):
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, sector in enumerate(sectors):
        s = sector_sent[sector].rolling(21).mean()  # 1-month smoothing
        ax.plot(s.index, s.values, label=sector, color=COLORS[i % len(COLORS)], lw=1.3)
    ax.axhline(0, color="gray", lw=0.9, ls="--")
    ax.set_xlabel("Date"); ax.set_ylabel("FinVADER-Extended compound (1-month MA)")
    ax.set_title("Figure 5. Sector sentiment index (FinVADER-Extended), 2020–2023 (1-month rolling mean)",
                 fontsize=10, fontweight="bold")
    ax.legend(fontsize=7, ncol=2)
    fig.text(0.5, -0.03,
             "Note: FinVADER-Extended compound score in [−1, +1]. Score lagged by 1 trading day to avoid look-ahead. "
             "Missing days carry-forward filled then set to 0 (neutral). "
             "Source: FINS3645 project data bundle, news_headlines.parquet.",
             ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "sector_sentiment.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/sector_sentiment.png")


# ── Figure 5b: Aggregate fear/greed index on 0-100, and standardised ───────────
# Week 9's central point: in levels the index sits above 50 on almost every day, so
# it must be standardised (expanding window, look-ahead-safe) to separate relatively
# fearful/greedy days.
with plt.rc_context(_style()):
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 4.5))
    roll100 = agg["score_100"].rolling(21).mean()
    axL.plot(agg.index, agg["score_100"].values, color=STEEL, lw=0.5, alpha=0.5)
    axL.plot(roll100.index, roll100.values, color=NAVY, lw=1.8)
    axL.axhline(50, color=CRIMSON, lw=0.9, ls="--")
    axL.text(agg.index[5], 50.6, "Neutral (50)", fontsize=7, color=CRIMSON)
    axL.set_ylabel("Fear/greed index (0–100)"); axL.set_xlabel("Date")
    axL.set_title(f"Panel A. Levels — above 50 on {100-_below50:.0f}% of days",
                  fontsize=9, fontweight="bold")

    zroll = agg["z_expanding"].rolling(21).mean()
    axR.axhspan(1.5, 4, color=FOREST, alpha=0.12); axR.axhspan(-4, -1.5, color=CRIMSON, alpha=0.12)
    axR.plot(agg.index, agg["z_expanding"].values, color=STEEL, lw=0.5, alpha=0.5)
    axR.plot(zroll.index, zroll.values, color=NAVY, lw=1.8)
    axR.axhline(0, color="gray", lw=0.9, ls="--")
    axR.text(agg.index[5], 1.62, "unusually greedy", fontsize=7, color=FOREST)
    axR.text(agg.index[5], -1.95, "unusually fearful", fontsize=7, color=CRIMSON)
    axR.set_ylim(-3, 3); axR.set_ylabel("Standardised index (z, expanding)"); axR.set_xlabel("Date")
    axR.set_title("Panel B. Standardised — separates fearful/greedy days", fontsize=9, fontweight="bold")

    fig.suptitle("Figure 5b. Aggregate news fear/greed index (all 50 equities), 2020–2023",
                 fontsize=10, y=1.02)
    fig.text(0.5, -0.03,
             f"Note: index = (compound+1)/2×100, equal-ticker-weight across 50 stocks, lagged 1 trading day. "
             f"z uses an expanding window (look-ahead-safe); expanding vs full-sample z correlate {_corr:.3f}. "
             "Source: FINS3645 news_headlines.parquet.", ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "aggregate_sentiment_standardised.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/aggregate_sentiment_standardised.png")


# ── Figure 6: Fusion before vs after ───────────────────────────────────────
with plt.rc_context(_style()):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Cumulative return
    ax = axes[0]
    base_wealth   = _cumret(base_fund.returns)
    fusion_wealth = _cumret(fusion_ret)
    ax.plot(base_wealth.index,  base_wealth.values,  color=NAVY,   lw=1.8, label="Base (Equity MS)")
    ax.plot(fusion_wealth.index, fusion_wealth.values, color=CRIMSON, lw=1.8, ls="--", label="Sentiment-tilted MS")
    ax.axhline(1, color="gray", lw=0.7, ls=":")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))
    ax.set_title("Panel A. Growth of $1", fontsize=10, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Growth of $1")
    ax.legend(fontsize=8)

    # Drawdown
    ax2 = axes[1]
    dd_base   = _drawdown(base_fund.returns)
    dd_fusion = _drawdown(fusion_ret)
    ax2.fill_between(dd_base.index,   dd_base.values,   0, alpha=0.20, color=NAVY)
    ax2.fill_between(dd_fusion.index, dd_fusion.values, 0, alpha=0.20, color=CRIMSON)
    ax2.plot(dd_base.index,   dd_base.values,   color=NAVY,   lw=1.5, label="Base")
    ax2.plot(dd_fusion.index, dd_fusion.values, color=CRIMSON, lw=1.5, ls="--", label="Sentiment-tilted")
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax2.set_title("Panel B. Drawdown", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Date"); ax2.set_ylabel("Drawdown")
    ax2.legend(fontsize=8)

    fig.suptitle("Figure 6. Sentiment-fusion comparison — Equity Max Sharpe fund, 2021–2023\n"
                 "(sentiment tilt α = 0.10; sector weights adjusted by VADER sector score)", fontsize=10, y=1.02)
    fig.text(0.5, -0.03,
             "Note: Sentiment-tilted fund upweights (downweights) tickers in sectors with above- (below-) median "
             "lagged VADER score by 10%. Source: FINS3645 project data bundle.",
             ha="center", fontsize=7, color="gray")
    plt.tight_layout()
    fig.savefig(FIGURES / "fusion_comparison.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
print("Saved results/figures/fusion_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════
# 7. Fusion metrics comparison table
# ═══════════════════════════════════════════════════════════════════════════
fusion_metrics = pd.DataFrame([
    {
        "Fund":           "Equity Max Sharpe (base)",
        "Ann. return":    f"{base_fund.ann_return():.2%}",
        "Ann. vol.":      f"{base_fund.ann_vol():.2%}",
        "Sharpe":         f"{base_fund.sharpe():.3f}",
        "Max drawdown":   f"{base_fund.max_drawdown():.2%}",
    },
    {
        "Fund":           "Equity Max Sharpe + Sentiment tilt",
        "Ann. return":    f"{float(fusion_ret.mean() * ANNUALISE):.2%}",
        "Ann. vol.":      f"{float(fusion_ret.std() * np.sqrt(ANNUALISE)):.2%}",
        "Sharpe":         f"{float(fusion_ret.mean() * ANNUALISE / (fusion_ret.std() * np.sqrt(ANNUALISE))):.3f}",
        "Max drawdown":   f"{float(_drawdown(fusion_ret).min()):.2%}",
    },
])
fusion_metrics.to_csv(TABLES / "fusion_comparison.csv", index=False)
print("Saved results/tables/fusion_comparison.csv")

print("\n=== Part B complete ===")
print(f"Funds produced : {len(funds)}")
print(f"Headlines scored: {len(scored):,} (mean VADER = {scored['compound'].mean():.4f})")
print(f"\nSentiment-fusion effect on Equity MS:")
print(f"  Base Sharpe    : {base_fund.sharpe():.3f}")
fus_sharpe = float(fusion_ret.mean() * ANNUALISE / (fusion_ret.std() * np.sqrt(ANNUALISE)))
print(f"  Tilted Sharpe  : {fus_sharpe:.3f}")
print(f"  Change         : {fus_sharpe - base_fund.sharpe():+.3f}")
