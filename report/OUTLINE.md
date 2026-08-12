# AlphaBlend Investment Platform — Part B Report: Funds, Sentiment & App
### OUTLINE / planning scaffold (NOT the report)

> **Rule for this file:** dot-points + structure only. Every judgement / interpretation
> is a `[STUDENT TO WRITE: …]` placeholder — do NOT submit these as prose. Numbers are
> cited to the source file so you verify them yourself before writing. Author the real
> report in `report/report.docx` → export `report/report.pdf`. Target **~5,000 words /
> 10 pages excl. appendix + references.** Per-section word budgets below.
>
> Reference data (verify against source):
> - Funds table → `results/tables/performance_metrics.csv` (15 rows)
> - Fusion → `results/tables/fusion_comparison.csv`
> - Sentiment before/after → `results/lexicon/before_after.csv`
> - Coverage → `results/tables/sentiment_coverage.csv`
> - Aggregate index → `results/data/aggregate_sentiment_index.csv`
> - Lexicon: 123 words (`kept_lexicon.csv`) + 204 idioms (`kept_idioms.csv`); 473-idiom
>   experiment archived in `kept_idioms_473_round2.csv`
> - Build history / judgement calls → `ai/prompt_log_01`…`16`

---

## Abstract  *(budget ~150 words)*
- `[STUDENT TO WRITE: one paragraph — scope (15 systematic funds across equity/crypto/
  combined × 5 methods; a news fear/greed index; a deployed app), plus the 2–3 headline
  numbers you choose to lead with.]`
- Candidate headline facts to draw from (cite sources): best fund Combined Max Sharpe
  Sharpe 1.033 (`performance_metrics.csv`); FinVADER-Extended lifts non-neutral headline
  coverage over finVADER 39.27%→47.17% (`before_after.csv`); sentiment tilt Sharpe
  0.587→0.602 (`fusion_comparison.csv`).

---

## Section 1 — The funds and the backtest design  *(budget ~700 words)*

### 1.1 Walk-forward design (source: `src/backtest.py`)
- Estimation window: **252 trading days** (`ESTIMATION_WINDOW = 252`).
- Weights formed from **past data only**: window is `returns.iloc[i-252 : i]` (excludes day i) → no look-ahead.
- Rebalance: **first trading day of each calendar month** (`_rebalance_dates`).
- First live OOS return at index 252 → **2021-01-04** for equity/combined (753 OOS days); **2020-09-10** for crypto (1208 days, 365-day calendar exhausts the window sooner). (source: `performance_metrics.csv` start_date/n_days.)
- **Risk-free rate = a real daily series** (replaces the old `RF = 0.0`). Source: **Fama/French 5 Factors (daily), `RF` column, Kenneth French Data Library**, filtered to **2020-01-02 to 2023-12-29** (`data/external/ff_rf_daily_2020_2023.csv`; `rf` is the decimal daily rate). Annualised, the sample RF runs from **0% (Apr 2020–Jul 2022) to ≈5.0%/yr (Dec 2022 onward)**.
- RF enters in **two places** (source: `src/backtest.py`): (i) the **Max-Sharpe objective**, using the *mean daily RF over the same 252-day estimation window* at each rebalance (past data only → no look-ahead); (ii) the reported **Sharpe ratio**, now an **excess-return Sharpe** = mean(daily return − daily RF) × 252 / annualised vol, computed per fund over its own date range. The other four methods (EW, MV, RP, HRP) do not use RF, so their weights are unchanged.
- **Forward-fill choice for crypto (deliberate assumption):** the RF file is on the equity trading calendar (~252 days/yr). Equity and combined funds share that calendar exactly (**0 missing dates**). Crypto funds trade all **365 calendar days**, so **376 of 1,208 crypto dates (31%, all weekends/holidays, incl. the trailing 2023-12-30/31) have no own-day RF**; these are **forward-filled** (carry the last trading-day rate forward), the same carry-forward convention used for missing sentiment days (`CLAUDE.md` rule 8). A short rate barely moves over a weekend, so this is a stated, deliberate choice, not a silent default-to-zero.
- **Zero transaction costs** (stated assumption; docstring in `backtest.py`).
- Annualisation: **√252 throughout** (`ANNUALISE = 252`) — all fund return series sit on the trading calendar.
- `[STUDENT TO WRITE: the 2021-2023 backtest window crosses the Fed's 2022 hiking cycle, so a zero-rate assumption is a much weaker approximation late in the sample than early in it — connect this to the actual RF values you see in the data]`
- `[STUDENT TO WRITE: why the rest of this design is defensible — window length (estimation noise vs adaptivity), monthly rebalance (turnover/cost realism), no-look-ahead as the integrity backbone.]`

> **⚠ Numbers changed — do not write results from stale figures.** Switching from `RF = 0` to the daily Ken French RF lowered **every** fund's reported Sharpe (positive RF is now subtracted) and shifted the **Max-Sharpe weights** (the optimiser objective changed; EW/MV/RP/HRP weights are byte-identical to before). New headline numbers (source: regenerated `performance_metrics.csv`, `fusion_comparison.csv`):
> - **Fusion (Equity MS):** base Sharpe **0.587 → 0.534**; tilted **0.602 → 0.552**; effect **+0.015 → +0.018** (still positive; base ann. return 10.70% → 11.97% because MS re-optimised).
> - **Equity:** EW 0.817→0.687, MV 0.490→0.325, MS 0.587→0.534, RP 0.724→0.580, HRP 0.674→0.520.
> - **Crypto:** EW 0.758→0.730, MV 1.047→1.011, MS 0.224→0.190, RP 0.801→0.772, HRP 0.839→0.808 (smaller drop — much of crypto's sample is in the zero-rate era and its vol is high).
> - **Combined:** EW 0.763→0.664, MV 0.494→0.329, MS 1.033→0.983, RP 0.896→0.765, HRP 0.741→0.591.
> - The Section-3/4 outline tables below and the prose in `report_draft.md` / `build_report.py` still carry the old `RF=0` numbers — rewrite them (in your own words) before submission, and rebuild `report.docx`.

### 1.2 The five optimisation methods (source: `src/portfolio.py`)
- **Equal Weight (EW):** 1/N; benchmark, no estimation.
- **Min Variance (MV):** minimise w′Σw, long-only, SLSQP with analytical gradient 2Σw.
- **Max Sharpe (MS) / mean-variance tangency:** maximise (w′μ − rf)/√(w′Σw); uses the sample mean μ (noisy estimator).
- **Risk Parity (RP):** equalise fractional risk contributions (rc = w·(Σw)/w′Σw → 1/N).
- **Hierarchical Risk Parity (HRP)** — López de Prado, M. (2016), "Building Diversified Portfolios that Outperform Out-of-Sample," *The Journal of Portfolio Management*, 42(4), 59–69. No covariance inversion → robust to noisy Σ. Three steps (source: `hierarchical_risk_parity()`):
  1. **Tree clustering** — d(i,j)=√(0.5(1−corr)); second-order distance = Euclidean between columns of d; single-linkage.
  2. **Quasi-diagonalisation** — reorder to dendrogram leaf order (correlated assets adjacent).
  3. **Recursive bisection** — split ordered list in half; inverse-variance weights within each side; allocate α = 1 − cv_left/(cv_left+cv_right) to the lower-variance side; recurse; final weight = product of α's on the path.
  - Synthetic validation (source: `ai/prompt_log_12_add_hrp.md`): 2 clusters, low-var {0,1} / high-var {2,3}, ~0 cross-corr → weights sum to 1, all ≥ 0; low-var cluster **0.901** vs high-var **0.099**; same ranking as risk_parity (rank corr 1.00) but not identical (HRP 90/10 vs RP 75/25). → `[STUDENT TO WRITE: one line confirming the test shows HRP behaves as the paper predicts.]`

### 1.3 Fund universe & innovation flag
- **3 families (Equity, Crypto, Combined) × 5 methods = 15 funds.**
- Brief's required minimum = a combined fund with ≥ 2 methods → **we far exceed it.**
- Flag explicitly as an **innovation item**: "a wider or newer set of funds or optimisation methods than the required minimum" (HRP is the *newer* method; 15 funds is the *wider* set).

---

## Section 2 — Out-of-sample results and fund fact sheets  *(budget ~900 words)*

### 2.1 Full performance table (verbatim from `results/tables/performance_metrics.csv`)

| Fund | Family | Method | Ann.ret | Ann.vol | Sharpe | Max DD |
|------|--------|--------|--------:|--------:|-------:|-------:|
| Equity Equal Weight | equity | ew | 13.21% | 16.17% | 0.817 | −20.32% |
| Equity Min Variance | equity | mv | 6.25% | 12.75% | 0.490 | −15.43% |
| Equity Max Sharpe | equity | ms | 10.70% | 18.23% | 0.587 | −26.07% |
| Equity Risk Parity | equity | rp | 10.55% | 14.58% | 0.724 | −18.53% |
| Equity HRP | equity | hrp | 9.24% | 13.71% | 0.674 | −16.94% |
| Crypto Equal Weight | crypto | ew | 50.73% | 66.91% | 0.758 | −81.60% |
| Crypto Min Variance | crypto | mv | 56.25% | 53.74% | 1.047 | −71.24% |
| Crypto Max Sharpe | crypto | ms | 14.37% | 64.16% | 0.224 | −89.28% |
| Crypto Risk Parity | crypto | rp | 52.15% | 65.07% | 0.801 | −79.53% |
| Crypto HRP | crypto | hrp | 52.79% | 62.95% | 0.839 | −78.05% |
| Combined Equal Weight | combined | ew | 16.22% | 21.25% | 0.763 | −28.75% |
| Combined Min Variance | combined | mv | 6.31% | 12.78% | 0.494 | −15.60% |
| Combined Max Sharpe | combined | ms | 25.48% | 24.65% | **1.033** | −26.26% |
| Combined Risk Parity | combined | rp | 14.36% | 16.02% | 0.896 | −19.84% |
| Combined HRP | combined | hrp | 10.39% | 14.01% | 0.741 | −18.41% |

### 2.2 Results worth discussing (numbers = fact; interpretation = yours)
- **Combined Max Sharpe = best risk-adjusted** (Sharpe 1.033, ret 25.48%). `[STUDENT TO WRITE: why might equity+crypto under Max-Sharpe beat either alone? — diversification of the tangency portfolio across two weakly-related return sources.]`
- **Crypto Max Sharpe = worst crypto fund** (Sharpe 0.224, ret 14.37%, MaxDD −89.28%) despite crypto being the highest-return class. `[STUDENT TO WRITE: connect to mean-variance's sensitivity to noisy μ, amplified in high-vol/high-kurtosis crypto.]`
- **Crypto Min Variance Sharpe 1.047 > every equity fund.** `[STUDENT TO WRITE: genuine risk-adjusted edge, or an artefact of the vol/annualisation/sample-window difference between asset classes? Note crypto n_days=1208 vs equity 753.]`
- **HRP lowest/near-lowest MaxDD in every family** (Equity −16.94%, Combined −18.41%, Crypto −78.05%) though not the top Sharpe. `[STUDENT TO WRITE: tie to the HRP paper's claim — stability/robustness over raw in-sample optimality.]`
- **Equity RP (0.724) > Equity HRP (0.674) > Equity MS (0.587).** `[STUDENT TO WRITE: the more sophisticated method does not always win OOS — discuss why (estimation error, small equity cross-section, single-period sample).]`

### 2.3 Required exhibits checklist (exact filenames)
- Performance-metrics table → `results/tables/performance_metrics.csv`
- Growth-of-$1 figure → `results/figures/cumret_by_family.png`
- Drawdown figure (≥1 fund) → `results/figures/drawdown_combined.png`
- Weights-over-time (≥1 fund, across methods) → `results/figures/weights_over_time.png`
- Sharpe / return-vs-risk barplot → `results/figures/sharpe_barplot.png`
- `[STUDENT TO WRITE: one interpreting sentence under EACH exhibit — never drop raw.]`

---

## Section 3 — The sentiment index  *(budget ~900 words)*

### 3.1 The scoring model: FinVADER-Extended (source: `src/sentiment.py`)
- Base = **finVADER** = VADER lexicon + **SentiBigNomics (~7,295 terms)** + **Henry's list (189 terms)** (Koráb 2023 package; Week 9).
- Our layer = **123 mined finance words** + **204 mined finance idioms**, each rated by a **10-independent-agent panel** on −4..+4, kept only where **|mean| ≥ 0.5 AND cross-agent std < 2.0**.
- Word additions on VADER's native −4..+4 scale; idioms applied by **phrase-collapsing** (see §4).

### 3.2 Before/after coverage (verbatim from `results/lexicon/before_after.csv`)
- plain VADER **51.13%** non-neutral | finVADER **39.27%** | FinVADER-Extended **47.17%**.
- `[STUDENT TO WRITE: plain VADER's non-neutral rate is HIGHER than finVADER's — argue this reflects finVADER CORRECTING false-positive sentiment on generic finance words (market/shares/stock, cf. Loughran & McDonald 2011) rather than finVADER being "worse"; our layer then recovers genuine finance sentiment (+7.9 pts over finVADER) without re-introducing the false positives.]`

### 3.3 Sector-level construction (source: `src/sentiment.py` build_sector_sentiment)
- **Equal-ticker-weight** average within each sector.
- **Lagged ≥ 1 trading day** (shift +1) → no look-ahead.
- Missing days: **carry-forward (ffill) then leading NaN → 0 (neutral)**.
- `[STUDENT TO WRITE: justify the missing-day rule — ffill assumes sentiment persists absent news; 0-fill for the leading gap is the neutral prior; note the alternative (drop) would break the fixed trading calendar the tilt needs.]`

### 3.4 Coverage evidence (verbatim from `results/tables/sentiment_coverage.csv`)
- single stock (median): 80% of days, day-to-day SD **12.81** (0–100 scale)
- sector (median): 99% of days, SD **7.30**
- aggregate (all 50): 100% of days, SD **2.86**  → **~4.5× noise reduction** pooling stock→aggregate.
- `[STUDENT TO WRITE: present this as the EVIDENCE (not assertion) that the fund-facing signal is built at sector level — enough coverage, far less day-to-day noise than single stocks.]`

### 3.5 Week 9 index-construction material (source: `ai/prompt_log_09`, `src/sentiment.py`, `results/data/aggregate_sentiment_index.csv`)
- **0–100 rescale:** score = (compound+1)/2×100 (`to_score_100`).
- **Aggregate market-wide index:** equal-ticker-weight mean across all 50 (`build_aggregate_sentiment`).
- **Standardisation (z):** raw level sits above 50 on **98.3% of days** (index below 50 only 1.7%) → level alone is uninformative; z-score against the index's own history separates fearful/greedy days.
- **Expanding window, not full-sample:** `standardise_expanding` uses data up to each date only → look-ahead-safe; expanding vs full-sample z correlate ~0.998 (so it costs almost nothing, but is required for anything used as a signal). `[STUDENT TO WRITE: one line on why expanding is mandatory for a live signal.]`
- **Fear/greed bands:** Z_BANDS (extreme fear/fear/neutral/greed/extreme greed); latest reading **Extreme greed, z ≈ 2.25** (`aggregate_sentiment_index.csv`).
- Index span 2020-01-02→2023-12-29; 0–100 range 45.3–62.8.

### 3.6 Attribution note (DO NOT conflate — see `ai/prompt_log_09`)
- **Index construction** methodology → Week 9 lecture (text→score→0–100→aggregate/sector→standardise).
- **Fusion / tilt** methodology → `PROJECT_BRIEF.md`'s fusion requirement (Week 9 defines NO tilt). `[STUDENT TO WRITE: state this attribution explicitly so the two sources aren't conflated.]`

---

## Section 4 — Extensions and innovations  *(budget ~1,000 words — highest-weighted, 30%)*

### 4.1 Primary innovation: the lexicon-mining pipeline (source: `scripts/lexicon/`, logs 05,07,08)
- **External corpus:** ~**2,154 articles** for idioms (452 for words) from Reuters/CNBC/MarketWatch/Bloomberg via RSS + Google News feeds. **Disclose:** used ONLY to discover candidate vocabulary; **never** as project data — all reported sentiment runs on the provided `news_headlines.parquet`. `[STUDENT TO WRITE: one sentence making this boundary explicit for the marker.]`
- **10-independent-agent valence rating** (−4..+4), each pass isolated → mean + cross-agent std per candidate.
- **Two-stage filter:** |mean| ≥ 0.5 (directional consensus) AND std < 2.0 (agreement). Note: std rarely binds (max std ~0.52 for words) — the binding constraint is the |mean| floor (documented in log 07).
- **Idiom phrase-collapsing fix** (the VADER positional bug, source: `ai/prompt_log_08`): VADER's `SPECIAL_CASE_IDIOMS` only fires when the phrase's **last word is a lexicon word, there are ≥3 preceding tokens, and the word 3-back is not a lexicon word** → most headline-LEADING idioms (e.g. "Shares soar …") never fired. Fix: detect each idiom and **collapse it into one token** carrying the idiom valence → fires regardless of position. Example: finVADER scores "profit warning" **+0.13** (backwards); collapsed idiom scores it negative.

### 4.2 Honestly-reported negative result: 204 vs 473 idioms (source: logs 08, 11; `fusion_comparison.csv`, `kept_idioms_473_round2.csv`)
- Round 1 → 204 idioms; fusion Sharpe **0.587 → 0.602 (+0.015)**.
- Round 2 added 269 (→ 473); fusion diluted to **+0.005**.
- **Reverted to 204** (best); **473 archived, not deleted** (`kept_idioms_473_round2.csv`).
- Rubric hook: "a careful extension that does not beat the baseline, clearly explained, still earns this band."
- `[STUDENT TO WRITE: explain WHY more idioms diluted rather than helped — candidate quality degrades at lower frequency thresholds; marginal/boilerplate phrases (e.g. "biggest analyst calls", "central bank", "rate hike", "cost cutting" — see appendix) dilute a previously sharp signal.]`

### 4.3 Second innovation: HRP (wider optimisation-method set)
- Cross-reference §1.2; frame as the "newer optimisation method" innovation, distinct from the lexicon work. `[STUDENT TO WRITE: one line on why HRP is a genuine methodological addition, not just a fifth colour on a chart.]`

### 4.4 Fusion result nuance (verbatim from `results/tables/fusion_comparison.csv`)
- Base Equity Max Sharpe: ret 10.70%, Sharpe **0.587**, MaxDD **−26.07%**.
- + Sentiment tilt: ret 11.00%, Sharpe **0.602 (+0.015)**, MaxDD **−26.66%** (slightly WORSE).
- `[STUDENT TO WRITE: interpret the tradeoff — the tilt improved risk-adjusted RETURN but slightly worsened DOWNSIDE protection; a small, sample-specific effect; sentiment as a modest tilt, not a primary signal.]`

---

## Section 5 — The app and the investor journey  *(budget ~600 words)*

### 5.1 Structure (source: `streamlit_app.py`)
- 5 pages: **Compare Funds · Fund Fact Sheet · My Allocation · Market Fear & Greed · Sentiment Analytics.**
- Investor journey: compare funds → read a fact sheet → set an allocation → check sentiment.

### 5.2 Design system (supports the "original figure & design system" band)
- Documented palette + shared header/metric-card CSS; **Plotly migration** (responsive, interactive, hover, fullscreen-safe) via one shared `apply_theme`.
- **Custom fear/greed gauge** (`go.Indicator`) as the sentiment centrepiece.
- Method→colour / family→line-style encoding on the growth chart (all 15 funds uniquely identifiable — see log 16).
- `[STUDENT TO WRITE: 2–3 lines on how these choices exceed default Streamlit.]`

### 5.3 Target user
- `[STUDENT TO WRITE: describe the target user — a moderate-to-high-risk-tolerance investor, ≥ $10k, preferring quantitative/rules-based management. Match Part A's stated value proposition (z5589978_projectA/report/report.pdf), do NOT reinvent it.]`

### 5.4 Deployment constraint (state plainly)
- The deployed app **only reads precomputed `results/` CSVs** — never recomputes the backtest or runs sentiment scoring live (no nltk/finvader at runtime). Grep-verified across sessions (logs 04,13).

### 5.5 Links (fill at hand-in)
- Live Streamlit URL: `[STUDENT TO ADD at hand-in]`
- Public GitHub repo: `[STUDENT TO ADD at hand-in — currently private z5589978/z5589978_projectB, make public at submission]`

---

## Section 6 — Critical reflection: 3 concrete recommendations  *(budget ~750 words)*

### 6.1 What worked / what didn't / why (from the honest findings above)
- Worked: HRP's drawdown stability; Combined Max-Sharpe's risk-adjusted return; the sentiment layer's coverage lift.
- Didn't (as expected/explained): idiom dilution 204→473; Crypto Max-Sharpe instability; the tilt's return-vs-drawdown tradeoff.
- `[STUDENT TO WRITE: synthesise — no new material, tie to the numbers already cited.]`

### 6.2 "What the index can and cannot tell you" (Week 9 slide 33 — put this here explicitly)
- Can: average many noisy headlines into one standardisable signal; flag relatively fearful/greedy days once standardised.
- Cannot: judge whether a headline is true or important; always get the sign right (headline sentiment is a noisy proxy); serve as a standalone buy/sell rule.
- `[STUDENT TO WRITE: phrase in your own words.]`

### 6.3 Three recommendations (write these yourself)
1. `[STUDENT TO WRITE: optimisation-method choice by client type — HRP/Risk Parity for a drawdown-averse client (evidence: HRP lowest MaxDD every family) vs Max-Sharpe for a return-chaser (evidence: Combined MS 25.5% ret / 1.033 Sharpe). Ground in the §2 table.]`
2. `[STUDENT TO WRITE: sentiment as a MODEST tilt, not a primary signal — evidence: +0.015 Sharpe but worse MaxDD, and the 204→473 dilution.]`
3. `[STUDENT TO WRITE: the rf=0 / zero-transaction-cost assumptions are unrealistic for a live product — recommend what to add (a real rf proxy, a turnover/cost model — note the brief calls a transaction-cost model an innovation) and how it would change monthly-rebalance conclusions.]`

---

## Front matter / References / Appendix

### References (compile in Part A's style; verify each — see `.claude/rules/`)
- López de Prado, M. (2016). Building Diversified Portfolios that Outperform Out-of-Sample. *The Journal of Portfolio Management*, 42(4), 59–69.
- Hutto, C.J. & Gilbert, E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. *ICWSM*.
- Koráb, P. (2023). finVADER (Python package; adds SentiBigNomics + Henry finance lexicons to VADER). `[STUDENT: confirm exact citation form used in Week 9.]`
- Loughran, T. & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65.
- Baker, M. & Wurgler, J. (2007). Investor Sentiment in the Stock Market. *Journal of Economic Perspectives* — *[from Part A refs; verify]*.
- Tetlock, P. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. *Journal of Finance* — *[Part A]*.
- Shapiro, Sudhof & Wilson (2022). Measuring news sentiment. *Journal of Econometrics* — *[Part A; verify]*.
- CNN Business Fear & Greed Index (market-data version, contrast with our news-only index).
- FINS3645 project data bundle (equity/crypto/news, 2020–2023).
- `[STUDENT TO WRITE: reconcile against z5589978_projectA reference list; drop any not actually cited.]`

### Appendix candidates
- **Full 15-fund metrics table** (already in §2.1; move to appendix if §2 runs long).
- **HRP synthetic-validation test** result (low-var 0.901 vs high-var 0.099; source log 12).
- **Borderline idioms to spot-check** (source `ai/prompt_log_08`): "biggest analyst calls", "central bank", "rate hike", "cost cutting". `[STUDENT: actually open results/lexicon/kept_idioms.csv and review these before finalising.]`
- Full combined-lexicon dump (`results/lexicon/finvader_extended_full.csv`) if space.

---
*Scaffold generated from ai/ logs 01–16, PROJECT.md, src/ and results/. Every `[STUDENT TO WRITE]` is yours to write; every number cites its source file — verify before use.*
