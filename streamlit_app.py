"""AlphaBlend — investor dashboard (Station 4).

Reads precomputed artifacts from results/ only.
Does NOT recompute backtests or run sentiment scoring at runtime.

All charts are Plotly (client-rendered SVG/JS): they resize correctly at any zoom /
fullscreen, manage date-axis tick density automatically, and add hover tooltips — a
single shared theme (apply_theme) keeps every chart visually consistent.

Pages
-----
1. Compare Funds       — performance table + growth-of-$1 chart across all 15 funds
2. Fund Fact Sheet     — two-step (family -> method) fund fact sheet
3. My Allocation       — blend funds, see combined statistics
4. Market Fear & Greed — aggregate news fear/greed gauge + standardised banded history
5. Sentiment Analytics — FinVADER-Extended overview, coverage evidence, sector index
"""
from __future__ import annotations

import pathlib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "results" / "data"
TABLES = ROOT / "results" / "tables"
LEXICON = ROOT / "results" / "lexicon"

# ── AlphaBlend design system ─────────────────────────────────────────────────
NAVY    = "#1F3A5F"   # primary
NAVY2   = "#2A4E7E"   # header gradient end
CRIMSON = "#B23A48"   # loss / negative
FOREST  = "#2E7D32"   # gain / positive
GOLD    = "#C99700"   # accent
TEAL    = "#007C89"
VIOLET  = "#6B5B95"
STEEL   = "#4A5568"
INK     = "#1A2233"   # body text
MUTED   = "#5B6472"   # secondary text
LINE    = "#E4E8EF"   # borders / gridlines
PANEL   = "#F5F7FA"   # cards / sidebar
FONT    = ('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, '
           'Arial, sans-serif')
COLORWAY = [NAVY, CRIMSON, FOREST, GOLD, TEAL, VIOLET, STEEL, "#8B4513", "#2C7873", "#FF6F61"]
# High-contrast palette for the multi-line sector chart. Ordered so the first five
# (the default selection) are maximally distinct — no two blue-leaning colours next to
# each other (NAVY and TEAL blur together at line weight, so TEAL is pushed later).
SECTOR_PALETTE = [NAVY, CRIMSON, FOREST, GOLD, VIOLET, TEAL, "#E8630A", "#8B4513",
                  STEEL, "#B5179E"]

st.set_page_config(page_title="AlphaBlend", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{ font-family: {FONT}; }}
    .stApp {{ background-color: #FFFFFF; color: {INK}; }}
    h1, h2, h3 {{ color: {NAVY}; letter-spacing: .2px; }}
    .block-container {{ padding-top: 2.2rem; }}

    /* Branded hero header */
    .ab-hero {{ background: linear-gradient(90deg, {NAVY} 0%, {NAVY2} 100%);
        color: #FFFFFF; padding: 1.05rem 1.35rem; border-radius: 12px; margin-bottom: 1.15rem; }}
    .ab-hero h1 {{ color: #FFFFFF; margin: 0; font-size: 1.55rem; font-weight: 700; }}
    .ab-hero p  {{ color: #D7E0EC; margin: .28rem 0 0; font-size: .9rem; }}

    /* Metric cards */
    [data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid {LINE};
        border-radius: 10px; padding: .7rem .9rem; }}
    [data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: .8rem; }}
    [data-testid="stMetricValue"] {{ color: {NAVY}; font-weight: 700; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background: {PANEL}; border-right: 1px solid {LINE}; }}
    .ab-brand {{ font-size: 1.25rem; font-weight: 800; color: {NAVY}; margin: .2rem 0 0; }}
    .ab-brand-sub {{ color: {MUTED}; font-size: .78rem; margin-bottom: .6rem; }}
    .ab-side-foot {{ color: {MUTED}; font-size: .74rem; line-height: 1.5;
        border-top: 1px solid {LINE}; padding-top: .7rem; margin-top: .4rem; }}

    /* Sidebar radio -> polished nav pills (text stays visible; only the small radio
       dot is de-emphasised — never hide the label content itself). */
    section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: .3rem; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
        display: flex; align-items: center; gap: .4rem; width: 100%;
        padding: .5rem .7rem; border-radius: 9px; cursor: pointer; font-size: .95rem;
        color: {INK}; transition: background .12s ease, color .12s ease; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{ background: #E9EEF6; }}
    /* shrink the native radio circle so the icon+label read as the nav */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
        transform: scale(.7); opacity: .55; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
        background: {NAVY}; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {{
        color: #FFFFFF !important; font-weight: 600; }}

    /* Sliders — thicker coloured track */
    .stSlider [data-baseweb="slider"] div[role="slider"] {{ background: {NAVY}; }}
    .stSlider [data-baseweb="slider"] > div > div > div {{ background: {NAVY}; }}

    /* Multiselect chips + segmented control */
    span[data-baseweb="tag"] {{ background-color: {NAVY} !important; border-radius: 7px; }}

    /* Tables / alerts / expander */
    [data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 10px; }}
    [data-testid="stExpander"] {{ border: 1px solid {LINE}; border-radius: 10px; }}
    [data-testid="stAlert"] {{ border-radius: 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="ab-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
                unsafe_allow_html=True)


def apply_theme(fig: go.Figure, height: int | None = None) -> go.Figure:
    """Shared Plotly theme so every chart matches the app's palette + type."""
    fig.update_layout(
        template="plotly_white", font=dict(family=FONT, size=13, color=INK),
        colorway=COLORWAY, paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=12, r=12, t=16, b=12), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False, showline=False)
    fig.update_yaxes(gridcolor=LINE, zeroline=False, showline=False)
    if height:
        fig.update_layout(height=height)
    return fig


PLOTLY_CFG = {"displayModeBar": False, "responsive": True}


def gauge_figure(z: float, band: str) -> go.Figure:
    """Native Plotly fear/greed dial (go.Indicator): resizes cleanly, hover-free."""
    steps = [
        {"range": [-3, -1.5], "color": BAND_COLORS["Extreme fear"]},
        {"range": [-1.5, -0.5], "color": BAND_COLORS["Fear"]},
        {"range": [-0.5, 0.5], "color": BAND_COLORS["Neutral"]},
        {"range": [0.5, 1.5], "color": BAND_COLORS["Greed"]},
        {"range": [1.5, 3], "color": BAND_COLORS["Extreme greed"]},
    ]
    col = BAND_COLORS.get(band, INK)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=round(z, 2),
        number={"prefix": "z = ", "font": {"size": 30, "color": col}},
        delta={"reference": 0, "increasing": {"color": FOREST}, "decreasing": {"color": CRIMSON}},
        title={"text": f"<b>{band}</b>", "font": {"size": 18, "color": col}},
        gauge={
            "axis": {"range": [-3, 3], "tickvals": [-3, -1.5, -0.5, 0.5, 1.5, 3],
                     "tickfont": {"size": 10, "color": MUTED}},
            "bar": {"color": "rgba(0,0,0,0)"},
            "steps": steps, "bgcolor": "white", "borderwidth": 0,
            "threshold": {"line": {"color": INK, "width": 4}, "thickness": 0.85, "value": round(z, 2)},
        },
    ))
    fig.update_layout(height=300, margin=dict(l=24, r=24, t=54, b=6),
                      paper_bgcolor="white", font=dict(family=FONT, color=INK))
    return fig


# ── Data loading (cached) ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_indexed(path: pathlib.Path) -> pd.DataFrame:
    return (pd.read_csv(path, index_col="date", parse_dates=True)
            if path.exists() else pd.DataFrame())


@st.cache_data(ttl=3600)
def load_csv(path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _row_count(path: pathlib.Path) -> int:
    df = load_csv(path)
    return 0 if df.empty else len(df)


BAND_COLORS = {
    "Extreme fear": "#8C1D2B", "Fear": "#D97A3D", "Neutral": "#9AA5B1",
    "Greed": "#5FA06E", "Extreme greed": "#2E7D32",
}
METHOD_NAMES = {"ew": "Equal Weight", "mv": "Min Variance", "ms": "Max Sharpe",
                "rp": "Risk Parity", "hrp": "Hierarchical Risk Parity"}
_NAME_TO_METHOD = {v: k for k, v in METHOD_NAMES.items()}
# Growth-of-$1 chart: encode method -> colour and family -> line style so all 15 funds
# get a unique, meaningful combination (a plain 10-colour cycle repeats after 10 funds).
METHOD_COLOR = {"ew": STEEL, "mv": NAVY, "ms": FOREST, "rp": CRIMSON, "hrp": VIOLET}
FAMILY_DASH = {"equity": "solid", "crypto": "dash", "combined": "dot"}


def fund_style(fund_name: str) -> tuple[str, str]:
    """(colour, dash) for a fund column name like 'Combined Max Sharpe'."""
    family, _, method_label = fund_name.partition(" ")
    return (METHOD_COLOR.get(_NAME_TO_METHOD.get(method_label, "ew"), STEEL),
            FAMILY_DASH.get(family.lower(), "solid"))

fund_returns = load_indexed(DATA / "fund_returns.csv")
fund_weights = load_csv(DATA / "fund_weights.csv")
if not fund_weights.empty:
    fund_weights["date"] = pd.to_datetime(fund_weights["date"])
metrics      = load_csv(TABLES / "performance_metrics.csv")
sector_sent  = load_indexed(DATA / "sector_sentiment_index.csv")
agg_sent     = load_indexed(DATA / "aggregate_sentiment_index.csv")
DATA_MISSING = fund_returns.empty or metrics.empty

# ── Sidebar: brand + polished nav ─────────────────────────────────────────────
st.sidebar.markdown('<div class="ab-brand">📈 AlphaBlend</div>'
                    '<div class="ab-brand-sub">Systematic multi-asset investing</div>',
                    unsafe_allow_html=True)
NAV = {
    "📊  Compare Funds": "Compare Funds",
    "📄  Fund Fact Sheet": "Fund Fact Sheet",
    "🎯  My Allocation": "My Allocation",
    "😨  Market Fear & Greed": "Market Fear & Greed",
    "📰  Sentiment Analytics": "Sentiment Analytics",
}
choice = st.sidebar.radio("Navigate", list(NAV), label_visibility="collapsed")
page = NAV[choice]
st.sidebar.markdown(
    '<div class="ab-side-foot">Out-of-sample backtest, 2021–2023.<br>'
    "252-day window · monthly rebalance · RF: daily 1M T-bill (Ken French).<br>"
    "All figures read precomputed results.</div>", unsafe_allow_html=True)


def growth_of_dollar(returns: pd.Series):
    return (1 + returns.dropna()).cumprod()


# ═══════════════════════════════════════════════════════════════════════════
# Page 1: Compare Funds
# ═══════════════════════════════════════════════════════════════════════════
if page == "Compare Funds":
    render_header("Compare Funds", "Out-of-sample performance across every fund and method")
    st.caption("Out-of-sample backtested performance (2021–2023). Estimation window: "
               "252 trading days. Monthly rebalance. Risk-free rate: daily 1-month "
               "T-bill proxy (Fama/French RF, Kenneth French Data Library; forward-"
               "filled on crypto non-trading days). Sharpe is excess of RF.")
    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results."); st.stop()

    families = ["All"] + sorted(metrics["family"].unique().tolist())
    fam = st.segmented_control("Asset family", families, default="All") or "All"
    m = metrics if fam == "All" else metrics[metrics["family"] == fam]

    st.subheader("Performance metrics")
    cols = [c for c in ["fund", "ann_return", "ann_vol", "sharpe", "max_drawdown"] if c in m.columns]
    fmt = {"ann_return": "{:.1%}", "ann_vol": "{:.1%}", "sharpe": "{:.2f}", "max_drawdown": "{:.1%}"}
    st.dataframe(m[cols].style.format({k: v for k, v in fmt.items() if k in cols})
                 .background_gradient(cmap="Blues", subset=[c for c in ["sharpe"] if c in cols]),
                 width="stretch", hide_index=True)

    st.subheader("Growth of $1 (out-of-sample)")
    to_plot = (fund_returns.columns.tolist() if fam == "All"
               else [c for c in fund_returns.columns if fam.lower() in c.lower()])
    if to_plot:
        c_log, c_hi = st.columns([1, 3])
        with c_log:
            log_scale = st.toggle("Log scale", value=False,
                                  help="Log y-axis — makes the compressed equity/combined "
                                       "cluster readable when crypto's growth dwarfs them.")
        with c_hi:
            highlight = st.selectbox("Highlight one fund", ["None"] + to_plot,
                                     help="Fades the other lines so one fund stands out.")

        fig = go.Figure()
        for col in to_plot:
            color, dash = fund_style(col)
            w = growth_of_dollar(fund_returns[col])
            faded = (highlight != "None" and col != highlight)
            fig.add_trace(go.Scatter(
                x=w.index, y=w.values, name=col, mode="lines",
                line=dict(color=color, dash=dash, width=1.3 if faded else 2.2),
                opacity=0.22 if faded else 1.0,
                hovertemplate="%{y:$.2f}<extra>%{fullData.name}</extra>"))
        fig.add_hline(y=1, line=dict(color="gray", dash="dash", width=1))
        apply_theme(fig, height=560)
        fig.update_layout(hovermode="closest")           # nearest line only (this chart only)
        if len(to_plot) > 6:                              # 15-fund "All" view: side legend
            fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1,
                                          xanchor="left", x=1.02, font=dict(size=10)))
        fig.update_yaxes(title="Growth of $1", tickprefix="$", tickformat=".2f",
                         type="log" if log_scale else "linear")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)
        st.caption("Colour = method (Equal Weight, Min Variance, Max Sharpe, Risk Parity, "
                   "HRP); line style = family (Equity solid, Crypto dashed, Combined dotted) "
                   "— so every one of the 15 funds is uniquely identifiable and the same "
                   "colour always means the same method. Hover shows the nearest line; click "
                   "the legend to toggle a fund, double-click to isolate one.")


# ═══════════════════════════════════════════════════════════════════════════
# Page 2: Fund Fact Sheet  (two-step: family -> method)
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Fund Fact Sheet":
    render_header("Fund Fact Sheet", "Pick an asset family, then a method")
    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results."); st.stop()

    fam_key = (st.segmented_control("Asset family", ["Equity", "Crypto", "Combined"],
                                    default="Equity") or "Equity").lower()
    fam_df = metrics[metrics["family"] == fam_key]
    order = ["ew", "mv", "ms", "rp", "hrp"]
    opts = [METHOD_NAMES[mth] for mth in order if mth in set(fam_df["method"])]
    disp = st.selectbox("Method", opts)
    inv = {v: k for k, v in METHOD_NAMES.items()}
    row = fam_df[fam_df["method"] == inv[disp]].iloc[0]
    selected = row["fund"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ann. Return", f"{row.get('ann_return', 0):.1%}")
    c2.metric("Ann. Volatility", f"{row.get('ann_vol', 0):.1%}")
    c3.metric("Sharpe Ratio", f"{row.get('sharpe', 0):.2f}")
    c4.metric("Max Drawdown", f"{row.get('max_drawdown', 0):.1%}")
    st.caption(f"{selected} — out-of-sample {row.get('start_date','N/A')} to "
               f"{row.get('end_date','N/A')} ({row.get('n_days','?')} trading days).")

    if selected in fund_returns.columns:
        r = fund_returns[selected].dropna()
        wealth = (1 + r).cumprod()
        dd = (wealth - wealth.cummax()) / wealth.cummax()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                            row_heights=[0.62, 0.38],
                            subplot_titles=("Growth of $1", "Drawdown"))
        fig.add_trace(go.Scatter(x=wealth.index, y=wealth.values, mode="lines",
                                 line=dict(color=NAVY, width=2), name="Growth",
                                 hovertemplate="%{y:$.2f}<extra></extra>"), row=1, col=1)
        fig.add_hline(y=1, line=dict(color="gray", dash="dash", width=1), row=1, col=1)
        fig.add_trace(go.Scatter(x=dd.index, y=dd.values, mode="lines", fill="tozeroy",
                                 line=dict(color=CRIMSON, width=1.4), name="Drawdown",
                                 hovertemplate="%{y:.1%}<extra></extra>"), row=2, col=1)
        apply_theme(fig, height=520)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title="Growth of $1", tickprefix="$", tickformat=".2f", row=1, col=1)
        fig.update_yaxes(title="Drawdown", tickformat=".0%", row=2, col=1)
        for a in fig.layout.annotations:
            a.font.update(size=12, color=NAVY)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

    st.subheader("Current target weights (last rebalance)")
    if not fund_weights.empty and "fund" in fund_weights.columns:
        fw = fund_weights[fund_weights["fund"] == selected]
        if not fw.empty:
            last = fw["date"].max()
            latest = fw[fw["date"] == last][["ticker", "weight"]].sort_values("weight", ascending=False)
            st.caption(f"Weights as of {last.date()}. Long-only, sum = 1.")
            st.dataframe(latest.style.format({"weight": "{:.1%}"}), width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# Page 3: My Allocation
# ═══════════════════════════════════════════════════════════════════════════
elif page == "My Allocation":
    render_header("My Allocation", "Blend funds into a portfolio and see the combined statistics")
    st.markdown("Set the percentage to allocate across funds; the blended statistics update automatically.")
    if DATA_MISSING:
        st.warning("Run `python scripts/run_part_b.py` to generate results."); st.stop()

    allocs, cols = {}, st.columns(2)
    for i, fn in enumerate(fund_returns.columns.tolist()):
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
        # Blend only over dates where every selected fund is live (funds have different
        # inception dates), else early rows would report a partial-portfolio return.
        r = fund_returns[common].dropna(how="any")
        blended = (r * weights[common]).sum(axis=1)
        wealth = (1 + blended).cumprod()
        ann_r, ann_v = blended.mean() * 252, blended.std() * (252 ** 0.5)
        sharpe = ann_r / ann_v if ann_v > 0 else 0
        mdd = ((wealth - wealth.cummax()) / wealth.cummax()).min()

        st.subheader("Blended portfolio")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ann. Return", f"{ann_r:.1%}"); k2.metric("Ann. Volatility", f"{ann_v:.1%}")
        k3.metric("Sharpe", f"{sharpe:.2f}"); k4.metric("Max Drawdown", f"{mdd:.1%}")
        fig = go.Figure(go.Scatter(x=wealth.index, y=wealth.values, mode="lines",
                                   line=dict(color=NAVY, width=2), name="My allocation",
                                   hovertemplate="%{y:$.2f}<extra></extra>"))
        fig.add_hline(y=1, line=dict(color="gray", dash="dash", width=1))
        apply_theme(fig, height=380)
        fig.update_yaxes(title="Growth of $1", tickprefix="$", tickformat=".2f")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)


# ═══════════════════════════════════════════════════════════════════════════
# Page 4: Market Fear & Greed
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Market Fear & Greed":
    render_header("Market Fear & Greed", "A news-only fear/greed index across all 50 equities")
    if agg_sent.empty:
        st.warning("Run `python scripts/run_part_b.py` to generate the aggregate index."); st.stop()

    latest = agg_sent.dropna(subset=["z_expanding"]).iloc[-1]
    z_now, band_now = float(latest["z_expanding"]), str(latest["band"])
    below50 = float((agg_sent["score_100"] < 50).mean() * 100)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Where the market stands today")
        st.plotly_chart(gauge_figure(z_now, band_now), use_container_width=True, config=PLOTLY_CFG)
        st.caption(f"As of {agg_sent.index[-1].date()}. Needle = standardised index "
                   f"(expanding-window z); today reads **{band_now}**. δ vs a neutral z = 0.")
    with right:
        st.subheader("Standardised index over time")
        zroll = agg_sent["z_expanding"].rolling(21).mean()
        fig = go.Figure()
        fig.add_hrect(y0=1.5, y1=4, fillcolor=BAND_COLORS["Extreme greed"], opacity=0.10, line_width=0)
        fig.add_hrect(y0=-4, y1=-1.5, fillcolor=BAND_COLORS["Extreme fear"], opacity=0.10, line_width=0)
        fig.add_trace(go.Scatter(x=agg_sent.index, y=agg_sent["z_expanding"], mode="lines",
                                 line=dict(color="#9AA5B1", width=0.6), name="daily", opacity=0.6,
                                 hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=zroll.index, y=zroll.values, mode="lines",
                                 line=dict(color=NAVY, width=2), name="21-day avg",
                                 hovertemplate="z = %{y:.2f}<extra></extra>"))
        fig.add_hline(y=0, line=dict(color="gray", dash="dash", width=1))
        apply_theme(fig, height=340)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title="Standardised (z)", range=[-3, 3])
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)
        st.caption("21-day average of the look-ahead-safe standardised index. "
                   "Shaded = unusually greedy (top) / fearful (bottom).")

    with st.expander("Why standardise? (the raw 0–100 level barely moves)"):
        st.markdown(
            f"On the raw 0–100 scale the index sits **above 50 on {100 - below50:.0f}% of "
            "days** — the news is mildly positive on average, so the level reads 'greed' almost "
            "every day and says nothing. Standardising against the index's own history (z-score) "
            "separates *relatively* fearful from greedy days, using an **expanding window** so it "
            "never peeks ahead.")
        roll100 = agg_sent["score_100"].rolling(21).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=agg_sent.index, y=agg_sent["score_100"], mode="lines",
                                 line=dict(color="#9AA5B1", width=0.6), opacity=0.5,
                                 name="daily", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=roll100.index, y=roll100.values, mode="lines",
                                 line=dict(color=GOLD, width=2), name="21-day avg",
                                 hovertemplate="%{y:.1f}<extra></extra>"))
        fig.add_hline(y=50, line=dict(color=CRIMSON, dash="dash", width=1))
        apply_theme(fig, height=280)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title="Index (0–100)")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

    st.subheader("What this index can — and cannot — tell you")
    a, b = st.columns(2)
    with a:
        st.success("**It can**")
        st.markdown("- average many noisy headlines into one readable number\n"
                    "- be standardised to flag relatively fearful / greedy days\n"
                    "- line up with known events once standardised")
    with b:
        st.error("**It cannot**")
        st.markdown("- judge whether a headline is true or important\n"
                    "- always get the sign right (headline sentiment is a noisy proxy)\n"
                    "- serve as a standalone buy / sell rule")


# ═══════════════════════════════════════════════════════════════════════════
# Page 5: Sentiment Analytics
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Sentiment Analytics":
    render_header("Sentiment Analytics",
                  "FinVADER-Extended, the coverage evidence, and the sector index")

    ba = load_csv(LEXICON / "before_after.csv")
    n_words = _row_count(LEXICON / "kept_lexicon.csv")
    n_idioms = _row_count(LEXICON / "kept_idioms.csv")
    st.subheader("The scoring model: FinVADER-Extended")
    st.markdown(
        f"Headlines are scored with **FinVADER-Extended** = finVADER (VADER + two finance word "
        f"lists) **plus our own layer**: **{n_words} finance words** and **{n_idioms} finance "
        "idioms**, each mined from a fresh news corpus and rated by a 10-independent-agent panel "
        "(kept where |mean| ≥ 0.5 and cross-agent std < 2.0). Idioms are applied by phrase-"
        "collapsing so context fires regardless of position — e.g. *profit warning* scores "
        "negative, not the +0.13 finVADER gives it.")
    if not ba.empty:
        d = {r["model"]: r["pct_non_neutral"] for _, r in ba.iterrows()}
        k1, k2, k3 = st.columns(3)
        k1.metric("plain VADER", f"{d.get('plain VADER', 0):.1f}%", help="headlines scored non-neutral")
        k2.metric("finVADER", f"{d.get('finVADER', 0):.1f}%")
        k3.metric("FinVADER-Extended", f"{d.get('FinVADER-Extended', 0):.1f}%",
                  delta=f"+{d.get('FinVADER-Extended', 0) - d.get('finVADER', 0):.1f} pts vs finVADER")
        st.caption("Share of headlines scored non-neutral (|compound| > 0.05).")

    fus = load_csv(TABLES / "fusion_comparison.csv")
    if not fus.empty:
        st.subheader("Does folding sentiment into the funds help?")
        st.dataframe(fus, width="stretch", hide_index=True)
        st.caption("Sentiment tilt on the Equity Max-Sharpe fund (above-median-sentiment sectors "
                   "upweighted). The live model uses the **204-idiom** set, the best tilt: excess-of-RF "
                   "Sharpe **0.534 → 0.552 (+0.018)**. Extending to 473 idioms diluted the effect, so we "
                   "reverted (473 archived). A small, sample-specific effect, reported as-is.")

    cov = load_csv(TABLES / "sentiment_coverage.csv")
    if not cov.empty:
        st.subheader("Why the fund signal is built at sector level")
        st.dataframe(cov.style.format({"pct_of_days": "{:.0f}%", "daily_change_sd_0_100": "{:.2f}"}),
                     width="stretch", hide_index=True)
        st.caption("A single stock has news on ~80% of days and swings ~12.8 pts/day (0–100 scale); "
                   "pooling to sector lifts coverage to ~99% and cuts noise to ~7.3, and the market "
                   "aggregate to ~2.9 — a ~4.5× noise reduction, so the fund signal is sector-level.")

    st.subheader("Sector sentiment index over time")
    if sector_sent.empty:
        st.info("Sector sentiment index not found.")
    else:
        sectors = sector_sent.columns.tolist()
        selected_sectors = st.multiselect("Sectors to display", sectors, default=sectors[:5])

        # Smoothing control — presets + fine slider grouped as one card
        if "smooth" not in st.session_state:
            st.session_state.smooth = 21

        def _set_preset():
            if st.session_state.get("smooth_preset") is not None:
                st.session_state.smooth = int(st.session_state.smooth_preset)

        ctrl, hi = st.columns([3, 2])
        with ctrl:
            with st.container(border=True):
                st.markdown("**Smoothing window** — rolling average over N trading days")
                st.segmented_control("presets", [7, 14, 21, 30, 63], format_func=lambda d: f"{d}d",
                                     key="smooth_preset", on_change=_set_preset,
                                     label_visibility="collapsed")
                smooth = st.slider("Fine control (days)", 1, 63, key="smooth")
        with hi:
            with st.container(border=True):
                st.markdown("**Highlight** — fade the other lines")
                highlight = st.selectbox("highlight", ["None"] + selected_sectors,
                                         label_visibility="collapsed",
                                         disabled=not selected_sectors)

        if selected_sectors:
            fig = go.Figure()
            for i, s in enumerate(selected_sectors):
                v = sector_sent[s].rolling(smooth).mean()
                faded = (highlight != "None" and s != highlight)
                fig.add_trace(go.Scatter(
                    x=v.index, y=v.values, name=s, mode="lines",
                    line=dict(width=1.5 if faded else 2.6,
                              color=SECTOR_PALETTE[i % len(SECTOR_PALETTE)]),
                    opacity=0.22 if faded else 1.0,
                    hovertemplate="%{y:.3f}<extra>%{fullData.name}</extra>"))
            fig.add_hline(y=0, line=dict(color="gray", dash="dash", width=1))
            apply_theme(fig, height=580)
            fig.update_layout(hovermode="closest")   # nearest line only (this chart only)
            fig.update_yaxes(title=f"FinVADER-Extended compound ({smooth}-day MA)")
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)
            st.caption("Sector index = equal-ticker-weight FinVADER-Extended compound, lagged 1 "
                       "trading day (no look-ahead) — the fund tilt's input. Hover shows the "
                       "nearest line; click a sector in the legend to toggle it, double-click to "
                       "isolate one. Source: FINS3645 news_headlines.parquet, 2020–2023.")
        else:
            st.info("Select at least one sector above to draw the chart.")
