# Part B Self-Assessment — evidence-based rubric marking
**Date:** 2026-08-14
**Project path:** `/Users/ryan.wu/Documents/GitHub/fins-agent/z5589978_projectB` (moved out of `fins2026/` since the last session)
**Graded report artifact:** `report/Project_B_report.pdf` (hand-edited final; `report.docx` was deleted, so the PDF is the source of truth)
**Marker:** `.claude/skills/mark-project-b` — strict, evidence-based, assessment-only. Does not author or fix content.

**Overall posture:** Strong project sitting broadly at **D/HD**. Two things cap the ceiling and one needs a browser to confirm: (1) crypto annualisation uses √252 not √365; (2) the live deployed app cannot be verified from the repo; (3) full own-words authorship can only be spot-checked.

---

## Evidence summary (raw checks)

| Check | Result |
|---|---|
| Required filenames (exact) | ✓ all 4: `results/data/fund_returns.csv`, `fund_weights.csv`, `sector_sentiment_index.csv`, `results/tables/performance_metrics.csv` |
| Fund coverage | 15 funds = equity/crypto/combined × ew/mv/ms/rp/hrp (`performance_metrics.csv`) |
| Required exhibits | ✓ metrics table, cumret_by_family, drawdown_combined, weights_over_time, sharpe_barplot, sector_sentiment, fusion_comparison (fig + `fusion_comparison.csv`) |
| No look-ahead | ✓ `src/backtest.py:210` window = `returns.iloc[i-estimation_window:i]` (excludes day i); `:199` `first_live = estimation_window` (≥252) |
| Annualisation | ⚠ `src/backtest.py:32` `ANNUALISE = 252` for **all** funds; crypto funds run 1,208 days on a 365-day calendar → annualised with √252, not √365 |
| Sentiment lag | ✓ `src/sentiment.py:171` `sector_daily.shift(1)`; `:220` aggregate shift(1) |
| App runtime safety | ✓ no `import nltk`, no `run_backtest`/`score_headlines`/`finvader` in `streamlit_app.py` (only a caption string names the data source) |
| Report artifact | `Project_B_report.pdf`, 5,399 words total (incl. refs+appendix); **0** `HUMAN EDIT REQUIRED`, **0** `STUDENT TO WRITE` markers |
| Report sections | Abstract, 1–6, References, Appendix (incl. Appendix D formal equations) all present |
| 3 recommendations | ✓ §6.3 "The first/second/third recommendation is …" (reworded in own words) |
| AI files | `AGENTS.md` (109 lines, 0 placeholder hits), `CLAUDE.md` (164 lines, 0 placeholder), `.claude/` present |
| Prompt logs | 25 logs `ai/prompt_log_01..26`; curated structure ("What was wrong", "Corrections made") present in the recent set |
| Repo visibility | **PUBLIC** — `gh repo view` → `{"visibility":"PUBLIC"}`, `github.com/z5589978/z5589978_projectB` |
| check_handin.py | All checks pass, 0 FAIL (1 cosmetic WARN: PDF named `Project_B_report.pdf`, not `report.pdf`) |
| Innovation evidence | 123 lexicon words + 204 idioms (`kept_lexicon.csv`/`kept_idioms.csv`); before/after `before_after.csv` finVADER 39.27% → Extended 47.17%; HRP in `portfolio.py`; custom Plotly design system |

---

## Mandatory Requirements (pass/fail gates)

| Gate | Verdict | Evidence |
|---|---|---|
| **AI submission** (own agent files + logs, stubs replaced) | **PASS** | `AGENTS.md`/`CLAUDE.md` present with 0 placeholder-stub hits; `.claude/` present; 25 curated prompt logs. |
| **Own writing & interpretation** | **PASS (spot-check) / partially UNVERIFIED** | 0 leftover AI markers in the PDF; §6.3 reworded away from the AI-draft phrasing ("The first recommendation is to…" vs draft "First,…"), which is positive evidence of hand-editing. Full authorship of every graded paragraph is **not verifiable from the repo** — flagged, not assumed. |
| **Academic integrity** (citations, own work) | **PASS (spot-check)** | References section present; data source cited; Part A reused legitimately. Minor: 3 references (Baker & Wurgler, Tetlock, Shapiro) appear only in the list, not cited in the body. |
| **Deployment gate** (public repo; app no nltk/no recompute) | **PASS on repo + app; live-load UNVERIFIED** | Repo PUBLIC (gh); app imports no nltk and recomputes nothing (grep). Whether the live `…streamlit.app` URL actually loads needs a browser — **UNVERIFIED**. |

No mandatory gate is currently failing on the evidence available.

---

## Criterion 1 — Funds: Optimal Portfolios & OOS Backtest (15%) → **D (75–84)**

**Evidence for the band.** Meets almost all HD wording: equity-only, crypto-only AND combined funds across several methods (15 funds = 3 families × 5 methods, `performance_metrics.csv`); correct walk-forward OOS with no look-ahead and weights from past data only (`backtest.py:210` window excludes day i; `:199` first live at index 252); all core exhibits present (metrics table, growth-of-$1, drawdown, weights-over-time, Sharpe barplot); fact sheets exist (app "Fund Fact Sheet" page); funds are compared (app "Compare Funds" + Table 1).

**Why not HD.** The HD band explicitly requires "**correct 252 vs 365 annualisation**." The code uses `ANNUALISE = 252` for every fund (`backtest.py:32`), but the crypto funds run 1,208 days on a 365-day calendar (`performance_metrics.csv`), so their return and Sharpe are annualised with √252 rather than √365. The report §1.1 justifies this as "every fund … measured on the equity trading calendar," which is inaccurate for the 1,208-day crypto funds and contradicts the project's own `CLAUDE.md` rule 2 ("crypto funds → √365").

**Biggest gap to HD:** crypto annualisation (√252 where √365 is correct).
**One next step:** in `src/backtest.py`, annualise crypto-family funds on 365 (and correct the §1.1 sentence), then regenerate `results/` — or, if 252 is a deliberate simplification, state that explicitly with the calendar reality rather than claiming all funds sit on the equity calendar.

---

## Criterion 2 — Sentiment Index (standalone) & Fusion Extension (10%) → **HD (85–100)** *(lower end)*

**Evidence.** A validated standalone sector sentiment index across equity sectors, shown over time (`sector_sentiment.png`, `sector_sentiment_index.csv`), with coverage validation (`sentiment_coverage.csv`: single-stock SD 12.81 → sector 7.30 → aggregate 2.86) and a look-ahead-safe expanding-window standardisation. Look-ahead-safe construction (`sentiment.py:171` `shift(1)`). Fusion of sentiment into the equity Max-Sharpe fund, with the effect measured (`fusion_comparison.csv`: base 0.534 → tilted 0.552, +0.018) and critically assessed (§4.4 discusses the small, sample-specific effect and the deeper drawdown). The honestly-reported modest/negative-leaning result is exactly what the HD band rewards.

**Biggest gap:** none material; to lock HD, ensure the §4.4 critical assessment is fully your own words.
**One next step:** re-read §4.4 and confirm the tradeoff discussion is your phrasing, not lightly-edited draft.

---

## Criterion 3 — Innovation & Data-Driven Results (30%, highest weight) → **HD (85–100)**

**Evidence.** Multiple built-and-demonstrated original extensions, each with evidence: (1) a **custom finance-sentiment lexicon** — 123 mined words + 204 idioms (`kept_lexicon.csv`, `kept_idioms.csv`), 10-agent-rated with a |mean|≥0.5 & std<2.0 keep rule, shown to advance the baseline (`before_after.csv`: finVADER 39.27% → FinVADER-Extended 47.17% non-neutral, +7.9pts) **and** an honestly-reported negative result (204 vs 473-idiom dilution); (2) **HRP** (a newer optimisation method, López de Prado 2016) implemented in `portfolio.py` with synthetic validation; (3) a **custom Plotly design system** in the app. The HD band names "a custom sentiment tool or lexicon" and "a careful extension with a negative result, explained" as sufficient — both are present and evidenced, not merely proposed.

**Biggest gap:** securing the band depends on the §4 write-ups reading as your own analysis.
**One next step:** spot-check that the §4.1/§4.2 lexicon narrative and the HRP writeup are in your words (the §4.2 dilution example was recently corrected — confirm you re-owned that paragraph).

---

## Criterion 4 — Streamlit App & Implementation (15%) → **D (75–84); HD contingent on UNVERIFIED live load**

**Evidence.** Full investor journey across 5 pages (Compare Funds, Fund Fact Sheet, My Allocation, Market Fear & Greed, Sentiment Analytics); reads only precomputed `results/` and imports no nltk / recomputes nothing (grep clean) — satisfies the deployment constraint; repo is **PUBLIC** at hand-in (gh); custom Plotly design system + custom fear/greed gauge (original design system, which the HD band rewards); `requirements.txt` slim.

**Why capped at D / not confirmed HD.** HD requires a **reliable, deployed** app that **loads** and supports the full journey. The repo and code support this, and a live URL (`https://z5589978projectb-…streamlit.app/`) is in the report — but **I cannot verify from the repo that the deployed app actually loads without errors and shows all pages with data.** That requires a browser.

**Biggest gap to confirmed HD:** unverified live deployment.
**One next step:** open the live URL, click through all 5 pages, confirm no load errors and that charts/tables render with data. If clean, this is HD-level.

---

## Criterion 5 — Economic Interpretation, Critical Reflection & Writing (10%) → **D (75–84); own-words spot-checked**

**Evidence.** §6.1 reflects on what worked / didn't / why; §6.3 gives **three concrete, specific recommendations** (method-by-client-type, sentiment-as-a-modest-tilt, add a transaction-cost model), reworded in your own voice; 0 leftover markers; figures appear interpreted; current RF-adjusted numbers throughout (0.534/0.552/0.983 etc.).

**Why D not HD.** HD hinges on "clear writing in the **student's own words**, with **every** exhibit interpreted." Own-words is spot-check-positive but not fully verifiable from the repo, and I did not confirm that literally every figure/table has an interpreting sentence.

**Biggest gap to HD:** full own-words assurance + every-exhibit-interpreted coverage.
**One next step:** do one pass confirming each figure/table has at least one interpreting sentence and that no paragraph still reads as verbatim AI.

---

## Criterion 6 — AI Workflow & Transparency (20%) → **HD (85–100)**

**Evidence.** Your own instruction files (`AGENTS.md` 109 lines, `CLAUDE.md` 164 lines, both with 0 placeholder-stub hits) plus `.claude/`; 25 curated prompt logs (`ai/prompt_log_01..26`) that record prompts verbatim, AI outputs, "What was wrong / risky", and "Corrections made" with reasons. This matches the HD wording (own agent files + curated logs showing prompts, outputs, and the student's own corrections).

**Biggest gap:** the candid "where AI was wrong and what I did instead" should read in your voice, not only as AI self-narration.
**One next step:** skim the logs and confirm at least a few carry your own reflective note on where you overrode or distrusted the AI.

---

## Bottom line

**Indicative position (label: indicative — rests on the per-criterion bands above):** the two 30%/20% pillars (Innovation HD, AI Workflow HD) are strong; Sentiment is HD; Funds, App, and Writing sit at D with clear, specific routes to HD. Weighted, that is an upper-D / low-HD overall picture — **contingent on the live app loading and on the own-words gate.**

**Top 3 highest-leverage fixes (weight × distance-to-next-band):**
1. **Crypto annualisation √252 → √365** (Criterion 1, 15%, D→HD). A concrete, code-level fix; the rubric names 252-vs-365 explicitly.
2. **Verify the live app loads in a browser** (Criterion 4, 15%, D→HD, and the deployment mandatory gate). Cannot be done from the repo.
3. **Own-words + every-exhibit-interpreted pass, and drop the 3 uncited references** (Criterion 5, 10%, plus mandatory gate 2).

## Unverified items (must check manually — not assumed pass)
- **Live Streamlit app actually loads and works** — needs a browser (URL in the report).
- **Full authorship of the graded prose** — repo can only spot-check; confirm every interpretation is your own.
- **Every exhibit has an interpreting sentence** — not exhaustively checked here.
- **Reference field accuracy** (each author/year/venue) — verify against sources; 3 uncited refs still listed.
- **PDF page count ≤ 10 (excl. appendix/refs)** — word count is 5,399 total; page count not measured here.

*This is a diagnostic assessment. It does not modify report content. Re-run `mark-project-b` after any change to see the updated position.*
