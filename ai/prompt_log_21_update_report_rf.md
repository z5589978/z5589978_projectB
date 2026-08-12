# Prompt Log 21 - Update the report draft with the real risk-free-rate results
**Session date:** 2026-08-12
**Task:** Bring report.docx (and its source) up to date after the risk-free-rate change from prompt_log_20, replacing stale RF=0 numbers and assumption statements without rewriting the author's analysis.

## Prompt used (verbatim)
> # Prompt for Claude Code — Update the Report Draft With the Real Risk-Free Rate Results
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> ---
>
> `report.docx` was last built before the risk-free-rate change (it predates `ai/prompt_log_20_daily_risk_free_rate.md`), so it's now carrying stale RF=0 numbers. Bring it up to date. Log 20 itself flagged this as unfinished ("Left for me to do: rewrite the graded report prose... report_draft.md and scripts/build_report.py still carry the old RF=0 numbers"), so this is picking up exactly where that session left off.
>
> ## 1. Read what actually changed before editing anything
>
> - `ai/prompt_log_20_daily_risk_free_rate.md` in full — this has the complete before/after Sharpe table for all 15 funds, the fusion comparison change (0.587→0.602 under RF=0 is now 0.534→0.552, +0.018, under the real rate), the base annual return change (10.70%→11.97%), and which fund weights actually shifted.
> - `report/OUTLINE.md` Section 1.1 — already updated with the new RF methodology bullets and **two `[STUDENT TO WRITE:]` placeholders** that were added by the RF work but never carried into the actual draft.
> - `results/tables/performance_metrics.csv`, `results/tables/fusion_comparison.csv`, `results/data/fund_weights.csv` — the regenerated source of truth.
> - `report/report_draft.md` and `scripts/build_report.py` (if that's the docx-building script — check, per Part A's convention referenced in earlier logs) — read both in full and identify every stale number, not just the four line numbers log 20 already flagged (`build_report.py:303,314,315,382`, `report_draft.md:27,44,65,232`) — re-grep for `0.587`, `0.602`, `10.70`, `risk-free rate is set to zero`, `RF = 0`, and any of the old per-fund Sharpe values from the table in log 20, in case something was missed.
> - Check whether `report/report.docx` is currently open (there's a `~$report.docx` Word lock file present) — if so, tell me to close it in Word first, don't try to overwrite an open file.
>
> ## 2. Update the numbers and assumption statements, not the analysis that doesn't depend on them
>
> This is a **factual correction pass**, not a rewrite of my reasoning. For every place with a stale Sharpe, return, or "risk-free rate is zero" statement: replace it with the correct regenerated number from `performance_metrics.csv`/`fusion_comparison.csv`. Where my existing sentence's *interpretation* doesn't depend on the specific old number (e.g. a qualitative point that still holds), leave my wording alone. Where it does depend on the number or its magnitude changed enough to matter, flag it clearly rather than silently rewriting my reasoning for me — e.g. every equity/combined fund's Sharpe fell by roughly 0.05–0.16 (bigger than crypto's ~0.03 fall) because their sample sits mostly in the 2022–2023 rate-hike period; if I'd written anything implying a flat risk-free assumption barely mattered, that claim needs my own correction, not an AI-rewritten one — flag it, don't fix it silently.
>
> ## 3. Specific things that need updating
>
> - Every one of the 15 funds' Sharpe ratio wherever quoted in prose or tables.
> - The fusion comparison numbers (base and tilted Sharpe, the delta, and the base annual return).
> - Any description of Max-Sharpe fund holdings/weights — `ew`/`mv`/`rp`/`hrp` weights are byte-identical to before (log 20 confirmed this), but the three Max-Sharpe funds' weights shifted (max weight change 0.116, 12 ticker-rows entered/left the portfolio) — if the report describes specific current holdings for Equity/Crypto/Combined Max-Sharpe, pull the updated weights from `fund_weights.csv`, don't leave the old ones in.
> - Carry the two `[STUDENT TO WRITE:]` placeholders from `OUTLINE.md` Section 1.1 into the draft at the right spot in Section 1, verbatim as placeholders, not answered.
> - Any sentence stating "risk-free rate is set to zero" needs to become an accurate description of the real methodology (daily Ken French 1-month T-bill proxy, forward-filled for crypto's non-trading days) — pull the exact wording from `OUTLINE.md` Section 1.1 rather than re-explaining it differently.
>
> ## 4. Rebuild the docx
>
> Update `report/report_draft.md`, then rebuild `report/report.docx` (via `scripts/build_report.py` if that's the established pipeline, otherwise however the doc was originally produced) so the two stay in sync. Don't touch the actual PDF export, that's my step.
>
> ## 5. Verify
>
> - Grep the rebuilt draft/docx source for the old numbers (`0.587`, `0.602`, `10.70%`) to confirm zero stale references remain.
> - Confirm the word count is still within the ~5,000-word cap after the edits.
>
> ## 6. Log it
>
> Log this to the next `ai/prompt_log_2X_update_report_rf.md` — this prompt verbatim, exactly which stale numbers you found and replaced, and the list of anything you flagged for me to personally re-check rather than silently changed.
>
> Start with the read in section 1.

## AI output summary

**Pipeline finding.** `scripts/build_report.py` is the single source of truth: it generates BOTH `report/report.docx` AND `report/report_draft.md` (the md is a mirror built from the same in-memory content), and Table 1 / Table 2 load from `performance_metrics.csv` / `fusion_comparison.csv` at build time. So the two tables auto-update on rebuild; only the hardcoded prose numbers were stale. I edited `build_report.py` prose and re-ran it, keeping the docx and md in sync. I did NOT hand-edit `report_draft.md` (it is regenerated).

**Lock file.** No `~$report.docx` present at edit time (it had been closed since log 20), so overwriting the docx was safe.

**Rebuild result.** Body word count (Abstract through Section 6) = 4,255, within the ~5,000 cap. Em-dash count across outputs = 0. Verified both `report_draft.md` and the extracted `report.docx` body+tables contain zero stale values outside the HUMAN EDIT flags, and that the new numbers and RF methodology text are present.

## Stale numbers found and replaced

Regenerated source of truth: `performance_metrics.csv`, `fusion_comparison.csv`.

| Location (build_report.py section) | Old | New |
|---|---|---|
| Abstract | combined MS Sharpe 1.033; return 25.5%; fusion 0.587→0.602 | 0.983; 26.6%; 0.534→0.552 |
| 1.1 assumptions paragraph | "risk-free rate is set to zero ... distortion is small ... flatters every fund equally" | replaced with the real RF methodology (daily Fama/French RF, 2020-01-02..2023-12-29; window-mean in the Max-Sharpe objective; excess-return Sharpe; crypto forward-fill 376/1208; √252) pulled from OUTLINE 1.1 |
| 1.1 (new) | — | two `[STUDENT TO WRITE:]` placeholders carried in |
| 2 intro + Table 1 caption | "Sharpe ratio uses a zero risk-free rate" | "excess of the daily risk-free rate (Fama/French RF)" |
| 2 (combined MS para) | 1.033; 25.5%; best equity fund RP 0.724 | 0.983; 26.6%; RP 0.580 (see flag) |
| 2 (crypto MS para) | Sharpe 0.224; MaxDD -89.3% | 0.190; -89.5% |
| 2 (crypto MV para) | Sharpe 1.047 | 1.011 |
| 2 (equity ranking para) | RP 0.724 > HRP 0.674 > MS 0.587 | RP 0.580, MS 0.534, HRP 0.520, MV 0.325, EW 0.687 (see flag) |
| 4.2 (negative result) | fusion 0.587→0.602 (+0.015); 473 fell to 0.005 | 0.534→0.552 (+0.018); 473 figure flagged |
| 4.4 (fusion result) | base 10.70%/0.587/-26.07%; tilt 11.00%/0.602/+0.015/-26.66% | 11.97%/0.534/-26.10%; 12.32%/0.552/+0.018/-26.70% |
| 6.1 | combined MS Sharpe 1.033 | 0.983 |
| 6.3 rec 1 | 25.5% return; Sharpe 1.033 | 26.6%; 0.983 |
| 6.3 rec 2 | fusion +0.015 | +0.018 |
| 6.3 rec 3 | "replace ... a zero risk-free rate ... use a real short-rate proxy" | reframed to transaction costs only (see flag) |
| Needs Review item | crypto MV 1.047 | 1.011 |
| Table 1, Table 2 | old per-fund and fusion rows | auto-regenerated from the CSVs |

Unchanged and deliberately left alone (RF does not affect them): HRP drawdowns -16.9% / -18.4% / -78.1%; all sentiment/coverage numbers (51.1%, 39.3%, 47.2%, 7.9 pts, 12.81/7.30/2.86, z = 2.25); HRP synthetic 0.901/0.099; corpus counts; the "profit warning" +0.13 example.

## What I flagged for you to personally re-check (not silently changed)

1. **Section 2, equity method ranking flipped.** Under RF=0 the order was Risk Parity > HRP > Max Sharpe; under the real rate it is Risk Parity (0.580) > Max Sharpe (0.534) > HRP (0.520), with Minimum Variance last (0.325). Max Sharpe is no longer the worst, so your "the more elaborate method does not win" and "Maximum Sharpe is penalised most" reasoning no longer holds as written. Left an inline HUMAN EDIT REQUIRED flag; did not rewrite the argument.
2. **Section 4.2, the 473-idiom dilution figures.** The 204-vs-473 comparison (gains 0.015 vs 0.005) was measured under RF=0; only the live 204-idiom fusion was re-run under the real rate (now +0.018). The 473-idiom fusion was not re-run. Flagged inline to either re-run it or state the dilution finding predates the RF change.
3. **Section 6.3, recommendation 3.** It recommended replacing the zero risk-free rate with a real proxy — now already implemented. Reframed the recommendation to transaction costs and flagged the RF half inline for you to rewrite in your own words (and optionally reframe the RF change as work already done, with its measured effect: Sharpe fell ~0.05–0.16 for equity/combined vs ~0.03 for crypto).
4. **Section 1.1, two `[STUDENT TO WRITE:]` placeholders** carried in verbatim for you to answer (the Fed-hiking-cycle reasoning and the rest-of-design defensibility).
5. **Light factual tightening (Section 2, combined MS paragraph):** "best equity fund, Risk Parity" became "best optimised equity fund" (Equal Weight's 0.687 is higher but is the benchmark), and "beats every standalone crypto fund" now notes the exception of the confounded crypto Minimum Variance fund (1.011 > 0.983). This mismatch pre-dates the RF change (under RF=0 it was 1.047 > 1.033) and the next paragraph already treats crypto MV as confounded; I made the sentence consistent rather than leaving a false claim, but confirm you are happy with the wording.

## Max-Sharpe holdings check

The three Max-Sharpe funds' weights shifted (per log 20), but the report prose does not quote any specific ticker weights for Equity/Crypto/Combined Max Sharpe — Figure 3 (combined weights over time) is a regenerated PNG, and Appendix A is the HRP synthetic test, not real holdings. So no holdings prose needed updating. Noted per step 3.

## What I checked / verified

- Read `report_draft.md` and `build_report.py` in full; re-grepped for `0.587`, `0.602`, `10.70`, per-fund old Sharpes, "risk-free rate is set to zero", `RF = 0`.
- After edits, grepped both the regenerated `report_draft.md` and the extracted `report.docx` (paragraphs + tables): zero stale values outside HUMAN EDIT flags; new numbers and RF methodology text present; Tables 1 and 2 carry the regenerated CSV rows.
- Word count 4,255 (< 5,000). Em dashes 0.

## What was wrong or risky

- The two `[STUDENT TO WRITE:]` placeholders in OUTLINE 1.1 contain em dashes; `build_report.py` enforces a no-em-dash rule and the report's own style bans them. I transcribed the placeholders with hyphens in place of the em dashes (content otherwise verbatim) so the pipeline's em-dash check stays at 0. The student answers/deletes these anyway.
- Editing `report_draft.md` by hand would have desynced it from `build_report.py`; correct fix was to edit the generator and rebuild.

## Corrections made

- None to revert. All edits are in `scripts/build_report.py`; `report.docx` and `report_draft.md` regenerated from it.

## Not done (left for you)
- PDF export from Word (your step, per the prompt).
- Answering the placeholders and the HUMAN EDIT REQUIRED flags in your own words.
- These changes are not committed yet (this prompt did not ask to commit/push).
