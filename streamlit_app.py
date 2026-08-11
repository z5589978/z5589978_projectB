"""AlphaBlend — investor dashboard (Station 4).

Reads precomputed artifacts from results/ only.
Does NOT recompute backtests or run sentiment scoring at runtime.

Pages
-----
1. Compare Funds      — performance table + growth-of-$1 chart across all funds
2. Fund Fact Sheet    — detailed fact sheet for a selected fund
3. My Allocation      — set weights across funds, see blended portfolio stats
4. Sentiment Analytics — sector sentiment index over time
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


# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("## 📈 **AlphaBlend**")
st.sidebar.markdown("*Systematic multi-asset investing*")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["Compare Funds", "Fund Fact Sheet", "My Allocation", "Sentiment Analytics"],
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
# Page 4: Sentiment Analytics
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Sentiment Analytics":
    render_header("Sector Sentiment Analytics",
                  "News-sentiment index across the equity sectors")
    st.caption(
        "FinVADER-Extended compound score of news headlines (finVADER plus 123 mined "
        "finance words and 473 mined finance idioms, each rated by a 10-agent panel), "
        "averaged equal-weight across the tickers in each sector, then lagged 1 "
        "trading day to avoid look-ahead. Score in [−1, +1]; 0 is neutral. "
        "Source: FINS3645 news_headlines.parquet, 2020–2023."
    )

    if sector_sent.empty:
        st.warning("Run `python scripts/run_part_b.py` to generate the sentiment index.")
        st.stop()

    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    sectors = sector_sent.columns.tolist()
    selected_sectors = st.multiselect("Sectors to display", sectors, default=sectors[:5])
    smooth = st.slider("Rolling-mean window (trading days)", 1, 63, 21)

    if selected_sectors:
        palette = [NAVY, CRIMSON, FOREST, GOLD, "#007C89", "#6B5B95", "#4A5568",
                   "#8B4513", "#2C7873", "#FF6F61"]

        fig, ax = plt.subplots(figsize=(11, 4.5))
        for i, sector in enumerate(selected_sectors):
            s = sector_sent[sector].rolling(smooth).mean()
            ax.plot(s.index, s.values, label=sector, lw=1.4,
                    color=palette[i % len(palette)])
        ax.axhline(0, color="gray", lw=0.9, ls="--")
        ax.set_xlabel("Date")
        ax.set_ylabel(f"FinVADER-Extended compound ({smooth}-day MA)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, ncol=2)
        ax.set_title("Sector Sentiment Index", fontsize=11, fontweight="bold", color=NAVY)
        st.pyplot(fig)
        plt.close(fig)

        st.subheader("Most recent sentiment (latest available date)")
        latest = sector_sent[selected_sectors].dropna(how="all").iloc[-1]
        latest_df = latest.reset_index()
        latest_df.columns = ["Sector", "Sentiment score"]
        latest_df = latest_df.sort_values("Sentiment score", ascending=False)
        st.dataframe(
            latest_df.style.format({"Sentiment score": "{:.4f}"}),
            width="stretch",
            hide_index=True,
        )
