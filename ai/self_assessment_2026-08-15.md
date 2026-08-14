# Part B Self-Assessment — evidence-based rubric marking (re-run)
**Date:** 2026-08-15
**Project path:** `/Users/ryan.wu/Documents/GitHub/fins-agent/z5589978_projectB`
**Graded report artifact:** `report/Project_B_report_word.docx` (Aug 15 03:06) — **no exported PDF exists** (`report/Project_B_report.pdf` is absent), so per the skill I grade the current .docx.
**Marker:** `.claude/skills/mark-project-b` — strict, evidence-based, assessment-only. Does not author or fix content.

**Overall posture:** Strong — five of six criteria sit at **HD** on the evidence, writing at high **D**. The crypto √365 annualisation fix has lifted Criterion 1 out of the D band it was capped in on 2026-08-14. The main risks now are **not content** but **submission mechanics**: no PDF has been exported, and a few writing-hygiene items remain.

---

## Evidence summary (fresh checks)

| Check | Result |
|---|---|
| Required filenames (exact) | ✓ all 4 present (`fund_returns.csv`, `fund_weights.csv`, `sector_sentiment_index.csv`, `performance_metrics.csv`) |
| Fund coverage | 15 funds = 3 families (equity/crypto/combined) × 5 methods (ew/mv/ms/rp/hrp) |
| Annualisation (**was the D-cap; now fixed**) | `src/backtest.py:33,81-85` `ann_factor` = 365 crypto / 252 else; used in ann_return/ann_vol/sharpe (`:89,92,108`) — **correct 252 vs 365** |
| No look-ahead | `backtest.py:219` window = `returns.iloc[i-estimation_window:i]` (excludes day i); `:208` first live at index 252 |
| Sentiment lag / fusion safety | `src/sentiment.py:171` `sector_daily.shift(1)` |
| App runtime safety | no `import nltk` / `run_backtest` / `score_headlines` in `streamlit_app.py` |
| App consistency | My Allocation now annualises crypto-only blends with √365 (`grep "ann = 365"` → 1) |
| Report artifact | `Project_B_report_word.docx`; **no PDF**; ~5,226 words incl. refs/appendix; body ≈ 4,375 (from build) — under the ~5,000 body cap |
| Unresolved markers in report | **0** HUMAN EDIT REQUIRED, **0** STUDENT TO WRITE |
| Crypto numbers | correct (1.217 & 0.229 present; old 1.011 & 0.190 absent); HRP "second-lowest" (D1 fixed) |
| Exhibits | ✓ 6 figures + fusion table (`cumret_by_family`, `drawdown_combined`, `weights_over_time`, `sharpe_barplot`, `sector_sentiment`, `fusion_comparison`, `fusion_comparison.csv`) |
| Equations | Appendix D (portfolio methods 1-7) + Appendix E (sentiment 8-9); 16 inline images |
| AI files | `AGENTS.md`/`CLAUDE.md` present, 0 stub hits; `.claude/skills/mark-project-b`; **30** prompt logs + 2 self-assessments |
| Repo visibility | **PUBLIC** (`gh repo view` → PUBLIC), pushed at `ac40086` |
| check_handin.py | **21 checks pass, 0 FAIL** (only cosmetic WARN: no `report.pdf` yet) |
| In-text exhibit refs | "Figure N" cross-refs: **1** of 7 figures; "Table N": 3 (see Criterion 5) |

---

## Mandatory Requirements (pass/fail gates)

| Gate | Verdict | Evidence |
|---|---|---|
| AI submission (own files + logs, stubs replaced) | **PASS** | AGENTS.md/CLAUDE.md 0 stub hits; `.claude/` with a custom marker skill; 30 curated prompt logs + self-assessments. |
| Own writing & interpretation | **PASS (spot-check) / partly UNVERIFIED** | 0 leftover AI markers; prose reworded in own voice ("The first recommendation is to…"); human-edit typos (whilest, tiltig, retuns) are positive evidence of hand-editing. Full authorship not repo-verifiable. |
| Academic integrity | **PASS (spot-check), one hygiene issue** | Data source cited; Part A reused legitimately. But 3 references (Baker & Wurgler, Tetlock, Shapiro) appear only in the list, not cited in the body. |
| Deployment gate (public repo; app no nltk/no recompute) | **PASS on repo+code; live-load user-confirmed** | Repo PUBLIC; app reads `results/` only. You confirmed the live URL loads in a browser; I cannot independently verify that from the repo. The corrected crypto data was just pushed — confirm the auto-redeploy has served it. |

No mandatory gate is failing on the available evidence.

---

## Criterion 1 — Funds: Optimal Portfolios & OOS Backtest (15%) → **HD (85-100)**
**Evidence.** Equity, crypto AND combined funds across five methods (15 funds, `performance_metrics.csv`); correct walk-forward OOS with no look-ahead (`backtest.py:219` excludes day i; `:208` first live at 252); **correct 252 vs 365 annualisation** (`:85` `ann_factor`) — the exact HD phrase that previously capped this at D is now satisfied; all core exhibits present (metrics table, growth-of-$1, drawdown, weights-over-time, Sharpe barplot); fact sheets in the app; funds compared (Compare Funds + Table 1).
**Biggest gap to hold HD:** none in content; the report must be exported to PDF so a marker actually sees it.
**One next step:** export the docx to `report/report.pdf`.

## Criterion 2 — Sentiment Index (standalone) & Fusion Extension (10%) → **HD (85-100)**
**Evidence.** Validated sector sentiment index over time (`sector_sentiment_index.csv`, `sector_sentiment.png`), with coverage validation (`sentiment_coverage.csv`) and look-ahead-safe construction (`sentiment.py:171` shift(1)). Look-ahead-safe fusion into the equity Max-Sharpe fund, measured (0.534 → 0.552, +0.018) and critically assessed with an honest small/negative result (§4, the 204-vs-473 dilution). Appendix E now gives the formal scoring equation (VADER compound, α = 15).
**Biggest gap:** ensure the §4 assessment reads as your own words.
**One next step:** re-read §4.2/§4.3 and confirm phrasing is yours.

## Criterion 3 — Innovation & Data-Driven Results (30%, highest weight) → **HD (85-100)**
**Evidence.** Multiple built-and-evidenced extensions: a custom finance-sentiment lexicon (123 words + 204 idioms, 10-agent |mean|≥0.5/std<2.0 rule, before/after `before_after.csv` 39.27% → 47.17%, plus an honestly-reported negative 473-idiom result); HRP (a newer optimisation method with synthetic validation); a custom Plotly design system; formal equations (Appendices D+E). The HD band explicitly credits "a custom sentiment tool or lexicon" and "a careful extension with a negative result, explained" — both present.
**Biggest gap:** authorship of the §4 narrative (own words).
**One next step:** spot-check §4.1/§4.2 are your analysis.

## Criterion 4 — Streamlit App & Implementation (15%) → **HD (85-100)** (live-load user-confirmed, not repo-verifiable)
**Evidence.** Deployed from a PUBLIC repo; app reads only precomputed `results/` and imports no nltk / recomputes nothing; full investor journey (Compare Funds, Fund Fact Sheet, My Allocation, Market Fear & Greed, Sentiment Analytics); custom design system + fear/greed gauge; My Allocation now per-family annualised for consistency. You confirmed the live app loads.
**Biggest gap / caveat:** I cannot verify the live deployment from the repo; and the corrected crypto data was only just pushed — the auto-redeploy must have completed for the live app to show the new numbers.
**One next step:** refresh the live URL and confirm Compare Funds shows Crypto Min Variance Sharpe ≈ 1.22.

## Criterion 5 — Economic Interpretation, Critical Reflection & Writing (10%) → **D (75-84)**
**Evidence for the band.** Evidence-based §6 reflection on what worked/didn't/why; three concrete, specific recommendations (§6.3); 0 leftover markers; numbers correct; D1/D2 comparison claims fixed.
**Why not HD (strict).** HD requires "clear writing in the student's own words, with **every** exhibit interpreted." Three concrete gaps: (1) only **1 of 7 figures** is cross-referenced in-text ("Figure N"), so several exhibits are not explicitly interpreted/referenced; (2) writing-quality slips — typos "whilest", "tiltig", "retuns"; (3) the reference list carries **3 uncited sources** (Baker & Wurgler, Tetlock, Shapiro). Own-words is spot-check-positive but not fully verifiable.
**Biggest gap to HD:** explicit interpretation/reference of every figure + a proofread + reference cleanup.
**One next step:** add an interpreting sentence that names each figure (Figure 1…7), fix the three typos, and drop or cite the three uncited references.

## Criterion 6 — AI Workflow & Transparency (20%) → **HD (85-100)**
**Evidence.** Your own AGENTS.md + CLAUDE.md (0 stub hits) plus `.claude/` including a custom `mark-project-b` marker skill; **30** curated prompt logs (`ai/prompt_log_01..30`) with prompts verbatim, AI outputs, and "What was wrong / Corrections made" sections, plus self-assessments. Matches the HD wording (own files + curated logs showing prompts, outputs, and the student's own corrections).
**Biggest gap:** ensure the candid "where AI was wrong, what I did instead" reads in your voice.
**One next step:** confirm a couple of logs carry your own reflective note.

---

## Bottom line
**Indicative position (label: indicative; rests on the per-criterion bands above):** five criteria at HD (Funds, Sentiment, Innovation, App, AI Workflow = 90% of the weight) and Writing at high-D. On indicative point estimates (HD≈88, D≈79) that weights to roughly **86-87 (HD)**. The crypto annualisation fix is the single biggest mover since 2026-08-14 (Criterion 1 D → HD).

**Top 3 highest-leverage actions (all submission-mechanics / writing, not content):**
1. **Export the report to `report/report.pdf`** — no PDF currently exists; the graded artifact is missing. (Blocks submission; touches every report criterion's visibility.)
2. **Criterion 5 (10%, D → HD):** reference each figure in-text (1/7 now), fix the typos, drop/cite the 3 uncited references.
3. **Confirm the live app redeployed** with the pushed crypto data (Criterion 4 + deployment gate).

## Unverified items (must check manually — not assumed pass)
- **Live Streamlit app loads and shows the new numbers** — you confirmed it loads; the just-pushed data needs the auto-redeploy to have completed. Not repo-verifiable.
- **Full authorship of the graded prose** — spot-check only.
- **Page count ≤ 10 (excl. appendix/refs)** — not measured (word count ≈ 5,226 total incl. refs/appendix).
- **Reference field accuracy** — verify each; 3 uncited refs still listed.

*Diagnostic only. No report content was modified. Re-run `mark-project-b` after exporting the PDF and the writing cleanup.*
