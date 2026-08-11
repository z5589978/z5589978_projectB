"""AlphaBlend — investor dashboard (Station 4).

Reads precomputed artifacts from results/ only.
Does NOT recompute backtests or run sentiment scoring at runtime.

Pages
-----
1. Compare Funds       — performance table + growth-of-$1 chart across all funds
2. Fund Fact Sheet     — detailed fact sheet for a selected fund
3. My Allocation       — set weights across funds, see blended portfolio stats
4. Market Fear & Greed — aggregate news fear/greed index: gauge, standardised
                         banded history, 0-100 levels, and what it can/cannot say
5. Sentiment Analytics — FinVADER-Extended overview, sector-level coverage
                         evidence, and the sector sentiment index over time
"""
from __future__ import annotations

import pathlib
import pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "results" / "data"
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"

# ── AlphaBlend design system ─────────────────────────────────────────────────
# One coherent palette + typography used across every page, applied through a
# single CSS block and a shared header helper, so the app reads as a designed
# product rather than default Streamlit with a few colours added.
NAVY    = "#1F3A5F"   # primary
NAVY2   = "#2A4E7E"   # header gradient end
CRIMSON = "#B23A48"   # loss / negative
FOREST  = "#2E7D32"   # gain / positive
GOLD    = "#C99700"   # accent
INK     = "#1A2233"   # body text
MUTED   = "#5B6472"   # secondary text
LINE    = "#E4E8EF"   # borders
PANEL   = "#F5F7FA"   # cards / sidebar

st.set_page_config(
    page_title="AlphaBlend",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     Helvetica, Arial, sans-serif;
    }}
    .stApp {{ background-color: #FFFFFF; color: {INK}; }}
    h1, h2, h3 {{ color: {NAVY}; letter-spacing: .2px; }}

    /* Branded hero header, one per page */
    .ab-hero {{
        background: linear-gradient(90deg, {NAVY} 0%, {NAVY2} 100%);
        color: #FFFFFF; padding: 1.05rem 1.35rem; border-radius: 12px;
        margin-bottom: 1.15rem;
    }}
    .ab-hero h1 {{ color: #FFFFFF; margin: 0; font-size: 1.55rem; font-weight: 700; }}
    .ab-hero p  {{ color: #D7E0EC; margin: .28rem 0 0; font-size: .9rem; }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background: {PANEL}; border: 1px solid {LINE};
        border-radius: 10px; padding: .7rem .9rem;
    }}
    [data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: .8rem; }}
    [data-testid="stMetricValue"] {{ color: {NAVY}; font-weight: 700; }}

    /* Sidebar + tables */
    section[data-testid="stSidebar"] {{
        background: {PANEL}; border-right: 1px solid {LINE};
    }}
    [data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 10px; }}
    .ab-side-foot {{ color: {MUTED}; font-size: .74rem; line-height: 1.4; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header(title: str, subtitle: str) -> None:
    """Branded hero header used at the top of every page."""
    st.markdown(
        f'<div class="ab-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


# ── Data loading (cached) ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_fund_returns() -> pd.DataFrame:
    path = DATA / "fund_returns.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, index_col="date", parse_dates=True)
    return df


@st.cache_data(ttl=3600)
def load_fund_weights() -> pd.DataFrame:
    path = DATA / "fund_weights.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["date"])
    return df


@st.cache_data(ttl=3600)
def load_performance_metrics() -> pd.DataFrame:
    path = TABLES / "performance_metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_sector_sentiment() -> pd.DataFrame:
    path = DATA / "sector_sentiment_index.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, index_col="date", parse_dates=True)
    return df


@st.cache_data(ttl=3600)
def load_aggregate_sentiment() -> pd.DataFrame:
    path = DATA / "aggregate_sentiment_index.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, index_col="date", parse_dates=True)


@st.cache_data(ttl=3600)
def load_csv(path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _row_count(path: pathlib.Path) -> int:
    df = load_csv(path)
    return 0 if df.empty else len(df)


# ── Fear/greed band colours (extreme fear -> extreme greed) ───────────────────
BAND_COLORS = {
    "Extreme fear": "#8C1D2B", "Fear": "#D97A3D", "Neutral": "#9AA5B1",
    "Greed": "#5FA06E", "Extreme greed": "#2E7D32",
}


def draw_gauge(z: float, band: str):
    """Semicircular fear/greed dial: coloured band arcs with a needle at the current
    standardised z (clipped to [-3, 3]). The app's custom design-system centrepiece."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge
    import numpy as np

    def z_to_angle(zz):  # z in [-3,3] -> 180deg (left/fear) .. 0deg (right/greed)
        return 180.0 - (np.clip(zz, -3, 3) + 3) * 30.0

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    bounds = [(-3, -1.5, "Extreme fear"), (-1.5, -0.5, "Fear"), (-0.5, 0.5, "Neutral"),
              (0.5, 1.5, "Greed"), (1.5, 3, "Extreme greed")]
    for lo, hi, name in bounds:
        ax.add_patch(Wedge((0, 0), 1.0, z_to_angle(hi), z_to_angle(lo),
                           width=0.32, facecolor=BAND_COLORS[name], edgecolor="white", lw=2))
    # needle
    ang = np.radians(z_to_angle(z))
    ax.plot([0, 0.82 * np.cos(ang)], [0, 0.82 * np.sin(ang)], color=INK, lw=3, solid_capstyle="round")
    ax.add_patch(plt.Circle((0, 0), 0.045, color=INK, zorder=5))
    ax.text(0, -0.14, band, ha="center", va="center", fontsize=15,
            fontweight="bold", color=BAND_COLORS.get(band, INK))
    ax.text(0, -0.30, f"z = {z:+.2f}", ha="center", va="center", fontsize=11, color=MUTED)
    ax.text(-1.02, -0.02, "Fear", ha="right", fontsize=8, color=MUTED)
    ax.text(1.02, -0.02, "Greed", ha="left", fontsize=8, color=MUTED)
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-0.42, 1.1); ax.set_aspect("equal"); ax.axis("off")
    return fig


# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("## 📈 **AlphaBlend**")
st.sidebar.markdown("*Systematic multi-asset investing*")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["Compare Funds", "Fund Fact Sheet", "My Allocation",
     "Market Fear & Greed", "Sentiment Analytics"],
)

st.sidebar.divider()
st.sidebar.markdown(
    '<div class="ab-side-foot">Out-of-sample backtest, 2021–2023.<br>'
    "252-day window · monthly rebalance · rf = 0.<br>"
    "All figures read precomputed results.</div>",
    unsafe_allow_html=True,
)

fund_returns = load_fund_returns()
fund_weights = load_fund_weights()
metrics      = load_performance_metrics()
sector_sent  = load_sector_sentiment()
agg_sent     = load_aggregate_sentiment()

DATA_MISSING = fund_returns.empty or metrics.empty


# ═══════════════════════════════════════════════════════════════════════════
# Page 1: Compare Funds
# ═══════════════════════════════════════════════════════════════════════════
if page == "Compare Funds":
    render_header("Compare Funds",
                  "Out-of-sample performance across every fund and method")
    st.caption(
        "Out-of-sample backtested performance (2021–2023). "
        "Estimation window: 252 trading days. Monthly rebalance. Risk-free rate: 0."
    )

    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results.")
        st.stop()

    # Filter controls
    families = ["All"] + sorted(metrics["family"].unique().tolist()) if "family" in metrics.columns else ["All"]
    fam = st.selectbox("Asset family", families)
    if fam != "All":
        m = metrics[metrics["family"] == fam]
    else:
        m = metrics

    # Performance table
    st.subheader("Performance metrics")
    display_cols = ["fund", "ann_return", "ann_vol", "sharpe", "max_drawdown"]
    display_cols = [c for c in display_cols if c in m.columns]
    fmt_map = {
        "ann_return":   "{:.1%}",
        "ann_vol":      "{:.1%}",
        "sharpe":       "{:.2f}",
        "max_drawdown": "{:.1%}",
    }
    st.dataframe(
        m[display_cols].style.format({k: v for k, v in fmt_map.items() if k in display_cols}),
        width="stretch",
        hide_index=True,
    )

    # Growth of $1
    st.subheader("Growth of $1 (out-of-sample)")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    if fam != "All":
        funds_to_plot = [c for c in fund_returns.columns if fam.lower() in c.lower()]
    else:
        funds_to_plot = fund_returns.columns.tolist()

    if funds_to_plot:
        fig, ax = plt.subplots(figsize=(11, 4))
        palette = [NAVY, CRIMSON, FOREST, GOLD, "#007C89", "#6B5B95", "#4A5568", "#8B4513"]
        for i, col in enumerate(funds_to_plot):
            wealth = (1 + fund_returns[col].dropna()).cumprod()
            ax.plot(wealth.index, wealth.values, label=col, lw=1.5,
                    color=palette[i % len(palette)])
        ax.axhline(1, color="gray", lw=0.7, ls="--")
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))
        ax.set_xlabel("Date")
        ax.set_ylabel("Growth of $1")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7, ncol=3)
        st.pyplot(fig)
        plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Page 2: Fund Fact Sheet
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Fund Fact Sheet":
    render_header("Fund Fact Sheet",
                  "Growth, drawdown, and current target weights for one fund")

    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results.")
        st.stop()

    fund_names = metrics["fund"].tolist() if "fund" in metrics.columns else []
    selected = st.selectbox("Select a fund", fund_names)

    if selected:
        row = metrics[metrics["fund"] == selected].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ann. Return",   f"{row.get('ann_return', 0):.1%}")
        col2.metric("Ann. Volatility", f"{row.get('ann_vol', 0):.1%}")
        col3.metric("Sharpe Ratio",  f"{row.get('sharpe', 0):.2f}")
        col4.metric("Max Drawdown",  f"{row.get('max_drawdown', 0):.1%}")

        st.caption(
            f"Out-of-sample period: {row.get('start_date', 'N/A')} to "
            f"{row.get('end_date', 'N/A')} ({row.get('n_days', '?')} trading days)."
        )

        # Growth of $1 + Drawdown
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        import numpy as np

        if selected in fund_returns.columns:
            r = fund_returns[selected].dropna()
            wealth = (1 + r).cumprod()
            dd = (wealth - wealth.cummax()) / wealth.cummax()

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
            ax1.plot(wealth.index, wealth.values, color=NAVY, lw=1.8)
            ax1.axhline(1, color="gray", lw=0.7, ls="--")
            ax1.set_ylabel("Growth of $1")
            ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))
            ax1.spines[["top", "right"]].set_visible(False)
            ax1.grid(alpha=0.25)

            ax2.fill_between(dd.index, dd.values, 0, alpha=0.25, color=CRIMSON)
            ax2.plot(dd.index, dd.values, color=CRIMSON, lw=1.4)
            ax2.axhline(0, color="gray", lw=0.8)
            ax2.set_ylabel("Drawdown")
            ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
            ax2.spines[["top", "right"]].set_visible(False)
            ax2.grid(alpha=0.25)
            ax2.set_xlabel("Date")

            fig.suptitle(f"{selected} — Fact Sheet", fontsize=12, fontweight="bold", color=NAVY)
            st.pyplot(fig)
            plt.close(fig)

        # Current holdings
        st.subheader("Current target weights (last rebalance)")
        if not fund_weights.empty and "fund" in fund_weights.columns:
            fw = fund_weights[fund_weights["fund"] == selected]
            if not fw.empty:
                last_date = fw["date"].max()
                latest = fw[fw["date"] == last_date][["ticker", "weight"]].sort_values(
                    "weight", ascending=False
                )
                st.caption(f"Weights as of {last_date.date()}. Long-only, sum = 1.")
                st.dataframe(
                    latest.style.format({"weight": "{:.1%}"}),
                    width="stretch",
                    hide_index=True,
                )


# ═══════════════════════════════════════════════════════════════════════════
# Page 3: My Allocation
# ═══════════════════════════════════════════════════════════════════════════
elif page == "My Allocation":
    render_header("My Allocation",
                  "Blend funds into a portfolio and see the combined statistics")
    st.markdown("Set the percentage you want to allocate across funds. The blended portfolio statistics update automatically.")

    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results.")
        st.stop()

    import numpy as np

    fund_names = fund_returns.columns.tolist()
    allocs = {}
    st.subheader("Allocation sliders (%)")

    cols = st.columns(2)
    for i, fn in enumerate(fund_names):
        with cols[i % 2]:
            allocs[fn] = st.slider(fn, 0, 100, 0, key=f"alloc_{fn}")

    total = sum(allocs.values())
    if total == 0:
        st.info("Set allocations above to see blended portfolio statistics.")
    elif total != 100:
        st.warning(f"Allocations sum to {total}% — adjust to 100% for a fully invested portfolio.")
    else:
        weights = pd.Series({k: v / 100.0 for k, v in allocs.items() if v > 0})
        common = fund_returns.columns.intersection(weights.index)
        # Only span dates where every selected fund is live. Funds have different
        # inception dates (crypto funds start earlier than equity/combined), so a
        # blend must start when the last-launched selected fund does — otherwise
        # early rows would report a partial-portfolio return.
        r = fund_returns[common].dropna(how="any")
        blended = (r * weights[common]).sum(axis=1)
        wealth = (1 + blended).cumprod()
        ann_r = blended.mean() * 252
        ann_v = blended.std() * (252 ** 0.5)
        sharpe = ann_r / ann_v if ann_v > 0 else 0
        dd = (wealth - wealth.cummax()) / wealth.cummax()
        mdd = dd.min()

        st.subheader("Blended portfolio")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ann. Return",    f"{ann_r:.1%}")
        c2.metric("Ann. Volatility", f"{ann_v:.1%}")
        c3.metric("Sharpe",         f"{sharpe:.2f}")
        c4.metric("Max Drawdown",   f"{mdd:.1%}")

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.plot(wealth.index, wealth.values, color=NAVY, lw=1.8, label="My allocation")
        ax.axhline(1, color="gray", lw=0.7, ls="--")
        ax.set_ylabel("Growth of $1")
        ax.set_xlabel("Date")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.25)
        st.pyplot(fig)
        plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Page 4: Market Fear & Greed (aggregate index — the sentiment centrepiece)
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Market Fear & Greed":
    render_header("Market Fear & Greed",
                  "A news-only fear/greed index across all 50 equities")

    if agg_sent.empty:
        st.warning("Run `python scripts/run_part_b.py` to generate the aggregate index.")
        st.stop()

    import matplotlib.pyplot as plt

    latest = agg_sent.dropna(subset=["z_expanding"]).iloc[-1]
    z_now, band_now = float(latest["z_expanding"]), str(latest["band"])
    below50 = float((agg_sent["score_100"] < 50).mean() * 100)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Where the market stands today")
        st.pyplot(draw_gauge(z_now, band_now))
        st.caption(
            f"As of {agg_sent.index[-1].date()}. The needle shows the standardised "
            f"index (expanding-window z); today reads **{band_now}**."
        )
    with right:
        st.subheader("Standardised index over time")
        zroll = agg_sent["z_expanding"].rolling(21).mean()
        fig, ax = plt.subplots(figsize=(6.6, 3.9))
        ax.axhspan(1.5, 4, color=BAND_COLORS["Extreme greed"], alpha=0.12)
        ax.axhspan(-4, -1.5, color=BAND_COLORS["Extreme fear"], alpha=0.12)
        ax.plot(agg_sent.index, agg_sent["z_expanding"], color="#9AA5B1", lw=0.5, alpha=0.6)
        ax.plot(zroll.index, zroll.values, color=NAVY, lw=1.8)
        ax.axhline(0, color="gray", lw=0.9, ls="--")
        ax.set_ylim(-3, 3); ax.set_ylabel("Standardised (z, expanding)"); ax.set_xlabel("Date")
        ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.25)
        st.pyplot(fig); plt.close(fig)
        st.caption("21-day average of the look-ahead-safe standardised index. "
                   "Shaded = unusually greedy (top) / fearful (bottom).")

    with st.expander("Why standardise? (the raw 0–100 level barely moves)"):
        st.markdown(
            f"On the raw 0–100 fear/greed scale the index sits **above 50 on "
            f"{100 - below50:.0f}% of days** — the news is mildly positive on average, so "
            "the level alone reads 'greed' almost every day and says nothing. Standardising "
            "against the index's own history (z-score) is what separates *relatively* "
            "fearful from greedy days. The z uses an **expanding window** (only data up to "
            "each date), so it never peeks ahead.")
        fig, ax = plt.subplots(figsize=(11, 3))
        roll100 = agg_sent["score_100"].rolling(21).mean()
        ax.plot(agg_sent.index, agg_sent["score_100"], color="#9AA5B1", lw=0.5, alpha=0.5)
        ax.plot(roll100.index, roll100.values, color=GOLD, lw=1.8)
        ax.axhline(50, color=CRIMSON, lw=0.9, ls="--")
        ax.set_ylabel("Index (0–100)"); ax.set_xlabel("Date")
        ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.25)
        st.pyplot(fig); plt.close(fig)

    st.subheader("What this index can — and cannot — tell you")
    c1, c2 = st.columns(2)
    c1.markdown(
        "**It can**\n\n"
        "- average many noisy headlines into one readable number\n"
        "- be standardised to flag relatively fearful / greedy days\n"
        "- line up with known events once standardised")
    c2.markdown(
        "**It cannot**\n\n"
        "- judge whether a headline is true or important\n"
        "- always get the sign right (headline sentiment is a noisy proxy)\n"
        "- serve as a standalone buy / sell rule")


# ═══════════════════════════════════════════════════════════════════════════
# Page 5: Sentiment Analytics (FinVADER-Extended + sector view + coverage)
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Sentiment Analytics":
    render_header("Sentiment Analytics",
                  "FinVADER-Extended, the coverage evidence, and the sector index")

    # ── What we built ────────────────────────────────────────────────────────
    ba = load_csv(TABLES.parent / "lexicon" / "before_after.csv")
    n_words = _row_count(TABLES.parent / "lexicon" / "kept_lexicon.csv")
    n_idioms = _row_count(TABLES.parent / "lexicon" / "kept_idioms.csv")
    st.subheader("The scoring model: FinVADER-Extended")
    st.markdown(
        f"Headlines are scored with **FinVADER-Extended** = finVADER (VADER + two finance "
        f"word lists) **plus our own layer**: **{n_words} finance words** and "
        f"**{n_idioms} finance idioms**, each mined from a fresh news corpus and rated by a "
        "10-independent-agent panel (kept only where |mean| ≥ 0.5 and cross-agent std < 2.0). "
        "Idioms are applied by phrase-collapsing so context fires regardless of position — "
        "e.g. *profit warning* scores negative, not the +0.13 finVADER gives it.")
    if not ba.empty:
        d = {r["model"]: r["pct_non_neutral"] for _, r in ba.iterrows()}
        k1, k2, k3 = st.columns(3)
        k1.metric("plain VADER", f"{d.get('plain VADER', 0):.1f}%", help="headlines scored non-neutral")
        k2.metric("finVADER", f"{d.get('finVADER', 0):.1f}%")
        k3.metric("FinVADER-Extended", f"{d.get('FinVADER-Extended', 0):.1f}%",
                  delta=f"+{d.get('FinVADER-Extended', 0) - d.get('finVADER', 0):.1f} pts vs finVADER")
        st.caption("Share of headlines scored non-neutral (|compound| > 0.05). Our layer "
                   "recovers finance sentiment finVADER misses, without re-introducing plain "
                   "VADER's false positives.")

    # ── Fusion result (sentiment -> funds) ───────────────────────────────────
    fus = load_csv(TABLES / "fusion_comparison.csv")
    if not fus.empty:
        st.subheader("Does folding sentiment into the funds help?")
        st.dataframe(fus, width="stretch", hide_index=True)
        st.caption(
            "Sentiment tilt on the Equity Max-Sharpe fund (above-median-sentiment sectors "
            "upweighted). Honest finding: the Sharpe gain peaked at **+0.015** with ~204 "
            "idioms and diluted to **+0.005** once all 473 were merged — more idioms is not "
            "strictly better. A small, sample-specific effect, reported as-is.")

    # ── Coverage evidence: why sector-level ──────────────────────────────────
    cov = load_csv(TABLES / "sentiment_coverage.csv")
    if not cov.empty:
        st.subheader("Why the fund signal is built at sector level")
        st.dataframe(
            cov.style.format({"pct_of_days": "{:.0f}%", "daily_change_sd_0_100": "{:.2f}"}),
            width="stretch", hide_index=True)
        st.caption(
            "A single stock has news on ~80% of days and its index swings ~12.8 pts/day "
            "(0–100 scale); pooling to sector level lifts coverage to ~99% and cuts day-to-day "
            "noise to ~7.3, and the market aggregate to ~2.9. That ~4.5× noise reduction is "
            "why the fund-facing signal is built at sector, not per-ticker, level.")

    # ── Sector sentiment series ──────────────────────────────────────────────
    st.subheader("Sector sentiment index over time")
    if sector_sent.empty:
        st.info("Sector sentiment index not found.")
    else:
        import matplotlib.pyplot as plt
        sectors = sector_sent.columns.tolist()
        selected_sectors = st.multiselect("Sectors to display", sectors, default=sectors[:5])
        smooth = st.slider("Rolling-mean window (trading days)", 1, 63, 21)
        if selected_sectors:
            palette = [NAVY, CRIMSON, FOREST, GOLD, "#007C89", "#6B5B95", "#4A5568",
                       "#8B4513", "#2C7873", "#FF6F61"]
            fig, ax = plt.subplots(figsize=(11, 4.5))
            for i, sector in enumerate(selected_sectors):
                s = sector_sent[sector].rolling(smooth).mean()
                ax.plot(s.index, s.values, label=sector, lw=1.4, color=palette[i % len(palette)])
            ax.axhline(0, color="gray", lw=0.9, ls="--")
            ax.set_xlabel("Date"); ax.set_ylabel(f"FinVADER-Extended compound ({smooth}-day MA)")
            ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.25)
            ax.legend(fontsize=8, ncol=2)
            st.pyplot(fig); plt.close(fig)
            st.caption(
                "Sector index = equal-ticker-weight FinVADER-Extended compound, lagged 1 "
                "trading day (no look-ahead). This lagged sector series is the input to the "
                "fund sentiment tilt. Source: FINS3645 news_headlines.parquet, 2020–2023.")
