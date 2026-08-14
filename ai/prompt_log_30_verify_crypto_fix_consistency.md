# Prompt Log 30 - Independently verify the crypto annualisation sweep
**Session date:** 2026-08-15
**Task:** Re-derive everything from source and independently verify the report is consistent after the crypto annualisation fix, including non-crypto claims that may have been disturbed.

## Prompt used (verbatim)
> # Prompt for Claude Code — Independently Verify the Crypto Annualisation Sweep
>
> The previous session (`ai/prompt_log_2X_crypto_annualisation_full_sweep.md`) reported the report fully synced after the crypto annualisation fix. Don't trust that self-report — re-derive everything from scratch and check for anything it missed or got wrong, including anything unrelated to crypto that might have been disturbed in the process.
>
> ## 1. Rebuild ground truth from the actual source, not from memory of the last session
> Read `results/tables/performance_metrics.csv` directly — this is the single source of truth for all 15 funds' current annualised return, annualised volatility, Sharpe ratio, and maximum drawdown. Don't rely on the numbers quoted in the last prompt log; pull them fresh from the CSV as it stands right now.
>
> ## 2. Cross-check every number in the report against that source, fund by fund
> Go through `report/report_draft.md` and `report/report.docx` and check every single numeric value quoted anywhere (tables, prose, captions, appendix) against the CSV. For each of the 15 funds, confirm return, volatility, Sharpe, and drawdown all match, including rounding (e.g. a figure rounded to 20.5% vs the CSV's precise value shouldn't be off by more than rounding error). Don't limit this to crypto funds only — confirm the 10 equity/combined funds are still correct too, in case anything was accidentally touched while editing around them.
>
> ## 3. Re-check every comparative or ranking claim in the whole report, not just crypto ones
> Independently identify every sentence in the report that compares, ranks, or makes an exception claim between any two funds or asset classes (for example "X beats Y", "the worst of the five", "higher than every equity fund", "except for..."), and verify each one against the current CSV numbers yourself. Do not assume the previous session's list of claims was complete — find your own, from a fresh read of the report top to bottom.
>
> ## 4. Check the report is internally self-consistent, not just consistent with the CSV
> Confirm `report/report_draft.md`, `report/report.docx`, and `report/OUTLINE.md` agree with each other everywhere a number or claim appears in more than one of them — these are meant to be kept in sync but tend to drift. Also check `PROJECT.md` for any leftover stale crypto figures from before the fix.
>
> ## 5. Check nothing else got disturbed
> Confirm the risk-free-rate figures and the sentiment/idiom figures (fusion Sharpe 0.534 → 0.552, the 204-idiom coverage numbers) are still correct and untouched — these were fixed in earlier sessions and shouldn't have moved, but confirm rather than assume, since report-wide edits can accidentally clobber unrelated sections.
>
> ## 6. Check the figures actually reflect the new numbers
> For every chart in `results/figures/` referenced in the report, confirm its file modification time is at or after the crypto-fix regeneration (not stale from before the fix). If you can inspect the underlying plotting data/script output rather than just the image timestamp, do that instead — a fresher timestamp doesn't guarantee the content actually changed if the regeneration script silently failed on a subset of charts.
>
> ## 7. Check the app
> Confirm `streamlit_app.py` reads only from `results/` (no hardcoded crypto numbers baked into the app code itself) and that the CSVs it reads (`results/data/fund_returns.csv`, `results/data/fund_weights.csv`) are consistent with `performance_metrics.csv`.
>
> ## 8. Report format
> Report as a table: location checked, what the source of truth says, what the report currently says, and a verdict of **Match** or **Mismatch** (with a fix applied and shown before/after) for each. Don't summarise with "everything checks out" without showing the individual checks that back that up.
>
> ## 9. Log it
> Log this to the next `ai/prompt_log_2X_verify_crypto_fix_consistency.md` — this prompt verbatim, and the full verification table from step 8.
>
> Start with step 1.

## Ground truth (performance_metrics.csv, pulled fresh)
Equity: EW 13.21%/16.17%/0.687/-20.32; MV 6.25/12.75/0.325/-15.43; MS 11.97/18.47/0.534/-26.10; RP 10.55/14.58/0.580/-18.53; HRP 9.24/13.71/0.520/-16.94.
Crypto: EW 73.47/80.52/0.878/-81.60; MV 81.47/64.68/1.217/-71.24; MS 20.52/77.56/0.229/-89.46; RP 75.53/78.32/0.929/-79.53; HRP 76.46/75.76/0.973/-78.05.
Combined: EW 16.22/21.25/0.664/-28.75; MV 6.31/12.78/0.329/-15.60; MS 26.57/24.89/0.983/-26.29; RP 14.36/16.02/0.765/-19.84; HRP 10.39/14.01/0.591/-18.41.
(Note report.docx does not exist — it was removed last session as a stale duplicate; the graded report is `report/Project_B_report_word.docx`.)

## Verification table (step 8)

| # | Location checked | Source of truth | Report says | Verdict |
|---|---|---|---|---|
| 1 | docx Table 1 - all 15 rows | CSV | every ret/vol/Sharpe/DD | **Match** (automated cell-by-cell, tol 0.06%/0.0015) |
| 2 | report_draft.md Table 1 - all 15 rows | CSV | every ret/vol/Sharpe/DD | **Match** |
| 3 | OUTLINE.md 2.1 table - all 15 rows | CSV | every ret/vol/Sharpe/DD | **Match** |
| 4 | docx Abstract: combined MS 0.983 / 26.6% | 0.983 / 26.57% | 0.983 / 26.6% | **Match** |
| 5 | docx 2 [27]: combined MS 0.983, 26.6% | 0.983 / 26.57% | 0.983 / 26.6% | **Match** |
| 6 | docx 2 [28]: Crypto MS Sharpe 0.229, DD -89.5% | 0.229 / -89.46% | 0.229 / -89.5% | **Match** |
| 7 | docx 2 [29]: Crypto MV Sharpe 1.217 | 1.217 | 1.217 | **Match** |
| 8 | docx 2 [30]: HRP DDs -16.9/-18.4/-78.1% | -16.94/-18.41/-78.05% | -16.9/-18.4/-78.1% | **Match (numbers)** - but see claim flag D1 |
| 9 | docx 2 [31]: equity ranking 0.580>0.534>0.520>0.325, EW 0.687 | RP.580 MS.534 HRP.520 MV.325 EW.687 | same | **Match** |
| 10 | docx 4 [63][66]: fusion 0.534->0.552 (+0.018), 11.97/12.32%, -26.10/-26.70% | fusion_comparison.csv | same | **Match** |
| 11 | docx 3 [45]: coverage 51.1/39.3/47.2, +7.9 | before_after 51.13/39.27/47.17 | same | **Match** |
| 12 | docx 3 [49]: SD 12.81/7.30/2.86, 4.5x | sentiment_coverage.csv | same | **Match** |
| 13 | docx App/Appendix: HRP 0.901/0.099; VADER α=15 | log 12 / nltk source | same | **Match** |
| 14 | OUTLINE 2.2 bullets: Crypto MS 0.229/20.52%, MV 1.217 | CSV | same | **Match** |
| 15 | OUTLINE change-note crypto line | CSV (current) + historical | 0.878/1.217/0.229/0.929/0.973 + pre-fix parenthetical | **Match** |
| 16 | PROJECT.md | - | no crypto figures | **Match (clean)** |
| 17 | streamlit_app.py hardcoded crypto numbers | - | none | **Match (clean)** |
| 18 | fund_returns.csv -> recompute all 15 metrics | performance_metrics.csv | recomputed ret/vol/Sharpe reproduce CSV exactly (per-family 365/252 + RF) | **Match** (deepest check - app data reproduces the report) |
| 19 | Figure 4 sharpe_barplot.png CONTENT | CSV | crypto bars 0.88/1.22/0.23/0.93/0.97; caption "√252 (equity, combined) or √365 (crypto)" | **Match** (visually inspected, not just mtime) |
| 20 | All figures mtime | CSV 08-14 22:40 | all figures 08-14 22:41 | **Match** (fresh) |
| 21 | Step 5: RF/idiom untouched (fusion 0.534->0.552; coverage 39.3->47.2) | CSVs | same | **Match** |

### Comparative-claim re-derivation (step 3) - found by independent check
| Claim | Re-derivation vs CSV | Verdict |
|---|---|---|
| 2 [28] "Crypto MS is the worst of all five crypto funds" | crypto Sharpes 0.878/1.217/0.229/0.929/0.973 -> 0.229 is min | **Holds** |
| 2 [29] "Crypto MV 1.217 higher than every equity fund" | equity max = EW 0.687 < 1.217 (gap now larger) | **Holds** |
| 2 [27] "combined MS beats all crypto except Min Variance" | 0.983 > EW .878, RP .929, MS .229, HRP **.973**; < MV 1.217 | **Holds, but FLAG D2** (margin over crypto HRP collapsed 0.175 -> **0.010**; "except MV" now hides a near-tie with HRP) |
| Abstract / 2 [30] / 6.3 [89] "HRP (or HRP/Risk Parity) delivered the LOWEST / shallowest maximum drawdown in every asset family" | **Min Variance has the shallowest DD in all 3 families** (eq -15.43 vs HRP -16.94; comb -15.60 vs -18.41; crypto -71.24 vs -78.05). HRP is 2nd, RP is 3rd, in every family. | **MISMATCH - FLAG D1** (numbers quoted match the CSV, but the "lowest/shallowest" ranking is wrong; MV is lowest, HRP is second) |

## Flags (not silently edited - graded, own-words interpretation)

**D1 (new, most important - a real ranking error the crypto-focused sweeps missed).** In the Abstract, Section 2 [30], and recommendation 1 (Section 6.3 [89]), the report states HRP (or "HRP or Risk Parity") delivered the *lowest/shallowest* maximum drawdown in every asset family. This is false: **Minimum Variance has the shallowest drawdown in all three families** (equity -15.4%, combined -15.6%, crypto -71.2%), with HRP second and Risk Parity third. The drawdown values the report quotes (-16.9/-18.4/-78.1) are correct for HRP; only the "lowest" superlative is wrong. This is unrelated to and unchanged by the crypto annualisation fix (drawdown is a path statistic) - it predates it and sits in the original AI draft too.
- Recommended fix (Section 2): "HRP delivered the lowest maximum drawdown..." -> "HRP delivered the **second-lowest** maximum drawdown in every asset family, behind Minimum Variance (-16.9% in equity, -18.4% in combined, -78.1% in crypto), the best or second-best of the five methods."
- Abstract and 6.3 need the same softening ("among the lowest" / "second only to Minimum Variance").
- Not auto-applied: this touches the HRP-as-stability-champion thesis and the drawdown-averse recommendation, so it is the student's call. Offered to apply on request.

**D2 (carried from last session, still unaddressed).** Section 2 [27] "combined Max Sharpe beats all standalone crypto funds except for the Minimum Variance fund" is still literally true (0.983 > crypto HRP 0.973), but the margin is now 0.010 (was 0.175 pre-fix). Consider adding "and only narrowly ahead of crypto HRP (0.973)".

Standing note (not a mismatch): the Abstract/2 call the combined MS fund the "best risk-adjusted" fund at 0.983, while crypto MV is numerically higher at 1.217; the report resolves this in 2 [29] by treating crypto MV as sample-window-confounded. Numbers match; framing is deliberate.

## What I checked / verified
- Pulled ground truth fresh from performance_metrics.csv; did not reuse last session's quoted numbers.
- Automated cell-by-cell comparison of all three tables (docx, draft, OUTLINE) to the CSV for all 15 funds within rounding tolerance - all match.
- Independent top-to-bottom read of the docx prose; re-derived every comparison/ranking claim against the CSV myself.
- Recomputed all 15 funds' return/vol/Sharpe directly from fund_returns.csv (per-family 365/252 + aligned RF) - reproduces performance_metrics.csv exactly (the strongest internal-consistency check).
- Visually inspected sharpe_barplot.png (crypto bars 0.88/1.22/0.23/0.93/0.97) rather than trusting the timestamp; caption correct.
- Confirmed streamlit_app.py has no hardcoded crypto figures; PROJECT.md clean; RF/idiom figures untouched.

## What was wrong or risky
- The previous crypto-focused sweeps were correct on every crypto number, but they did not catch the pre-existing **HRP "lowest drawdown" ranking error** (D1) because it is a drawdown claim, unchanged by the crypto fix, and the number quoted is HRP's own (correct) drawdown - only the superlative is wrong. This is exactly the kind of thing an independent re-derivation surfaces.
- The docx had been edited since the last session (the student removed the earlier "HRP does not outperform the max-sharpe funds" flag - good), so I re-read the current file rather than trusting the prior extract.

## Corrections made
- None applied. All crypto-annualisation numbers already match the CSV across docx, draft, OUTLINE, and the app data. The two flags (D1, D2) are interpretive claim issues left for the student's decision, with recommended before/after wording above.

## Not done (left for the student)
- Decide on D1 (HRP "lowest drawdown" -> "second-lowest, behind Minimum Variance") and D2 (crypto HRP near-tie). I can apply either on request.
- Re-export the PDF from the docx after any wording changes.
