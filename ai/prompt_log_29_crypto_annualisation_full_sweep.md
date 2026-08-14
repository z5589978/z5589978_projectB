# Prompt Log 29 - Full report sweep after the crypto annualisation fix
**Session date:** 2026-08-14
**Task:** Exhaustively re-check every crypto-touching number AND comparison/ranking claim across the whole report and repo after the √365 annualisation fix (log 28), not just a literal-number grep.

## Prompt used (verbatim)
> # Prompt for Claude Code — Full Report Sweep After the Crypto Annualisation Fix
>
> `ai/prompt_log_28_crypto_annualisation.md` fixed the crypto annualisation bug (crypto funds trade 365 days/year and were wrongly annualised with √252/×252 instead of √365/×365). You already updated Table 1's five crypto rows and two Sharpe values in Section 2 prose, and confirmed equity/combined are byte-identical. I don't trust "fully synced" as reported — that pass only caught the spots you happened to grep for. Do a genuinely exhaustive sweep this time, not a repeat of the same grep.
>
> ## 1. The full before/after, for reference
> | Crypto fund | Ann. return | Sharpe |
> | Equal Weight | 50.7% → 73.5% | 0.730 → 0.878 |
> | Min Variance | 56.2% → 81.5% | 1.011 → 1.217 |
> | Max Sharpe | 14.2% → 20.5% | 0.190 → 0.229 |
> | Risk Parity | 52.1% → 75.5% | 0.772 → 0.929 |
> | HRP | 52.8% → 76.5% | 0.808 → 0.973 |
> Volatility also scales ×1.20 for all five; maximum drawdown is unchanged (it's a path statistic, not an annualisation). Equity and combined funds (10 funds) are untouched.
>
> ## 2. Grep is not enough — check the claims, not just the numbers
> A literal-number grep will miss any sentence that makes a *comparison, ranking, or exception* involving a crypto fund without repeating the raw figure. Go through the whole report and, for every sentence anywhere that compares or ranks a crypto fund against another fund (equity, combined, or another crypto method), re-derive whether the claim still holds under the new numbers. Known example to check first: Section 2 says the combined Max Sharpe fund "beats all optimized equity only funds, and all standalone crypto funds except for the Minimum Variance fund" — Combined Max Sharpe is 0.983; check this against ALL five new crypto Sharpes, not just Min Variance, since HRP moved from 0.808 to 0.973, which is now much closer to 0.983 than it was and may deserve its own mention. Do this same re-derivation for every crypto-touching comparison in the report, not just this one example.
>
> ## 3. Watch for my abbreviation
> I sometimes shorten "Max Sharpe" to "MS" (for example "the combined MS fund" in Section 2). Make sure your search for Max-Sharpe-related sentences covers "MS" as well as "Max Sharpe" / "Maximum Sharpe" / "MaxSharpe" — a plain grep for the full phrase will miss these.
>
> ## 4. Places to check specifically, beyond Table 1 and the two prose values already fixed
> - The Abstract.
> - All of Section 2 (out-of-sample results) — go sentence by sentence, not just the two you already caught.
> - Section 2's crypto Min Variance discussion — the "1.011... should be read with care" paragraph now needs the updated 1.217, and re-check whether the "confounded by sample period" argument's framing (e.g. "higher than every equity fund") still reads correctly at the new, larger gap.
> - Section 4 (extensions/innovations) — the fusion work is equity-only, but check for any incidental crypto figure mentioned in passing (e.g. in the HRP discussion, since HRP's crypto drawdown/Sharpe might be cited as an example).
> - Section 6 (critical reflection and the three recommendations) — check for any crypto number used to support a recommendation.
> - The **Needs Review** section at the end — item 1 literally quotes "the different sample window (1,208 vs 753 days)" discussion referencing "crypto Minimum Variance Sharpe 1.011" — this is now stale and must be updated to 1.217, and the item's substance (is the sample-window confound point still valid at the new number?) re-confirmed.
> - Any figure captions or in-text figure references describing crypto values directly (not just the figures themselves, which you already regenerated).
> - `report/OUTLINE.md` and `PROJECT.md` — same stale-number risk as previous sync passes; check these too, not just the draft/docx.
> - `streamlit_app.py` — any hardcoded caption, tooltip, or markdown text (not chart data, which reads from `results/` and is already fixed) that quotes a specific crypto number.
>
> ## 5. Report back per item, don't just say "done"
> For every place you find or check, report: the location, whether it was stale, what you changed (before → after), and for comparison/ranking claims specifically, confirm whether the underlying claim still holds true under the new numbers (not just whether you updated a number). If a comparative claim's *meaning* changed even though no number needed editing (e.g. a gap got a lot smaller or larger), flag that too.
>
> ## 6. Verify
> - Full-text grep the whole repo (draft, docx, OUTLINE.md, PROJECT.md, ai/ logs excluded) for the old figures (50.7, 56.2, 14.2, 52.1, 52.8, 0.730, 0.772, 0.808 — the two already-fixed ones, 1.011 and 0.190, too, in case they reappear elsewhere) to confirm zero stale instances remain anywhere, not just where you already looked.
> - Confirm the five new figures (73.5/0.878, 81.5/1.217, 20.5/0.229, 75.5/0.929, 76.5/0.973) each appear the correct number of times given how many places in the report cite them.
> - `python scripts/check_handin.py`.
> - Rebuild `report/report.docx` if anything changed.
>
> ## 7. Log it
> Log this to the next `ai/prompt_log_2X_crypto_annualisation_full_sweep.md` — this prompt verbatim, and the full per-location report from step 5.
>
> Start with step 2.

## Per-location report (step 5)

### Graded report — `report/Project_B_report_word.docx` (checked every crypto/MS sentence, "MS" abbreviation included)
| Location | Stale? | Finding / action |
|---|---|---|
| Abstract | No | Cites only combined MS (0.983, 26.6%), HRP drawdown (qualitative), equity fusion (0.534→0.552). No crypto figure. |
| §1.1 dates/calendar | No | 753 days / 4 Jan 2021 / crypto 10 Sep 2020 all unchanged. |
| §1.1 annualisation sentence | Fixed in log 28 | Correctly states √252 equity/combined, √365 crypto. |
| §2 "combined MS beats all crypto except MV" | **CLAIM HOLDS, meaning shifted — FLAGGED** | Combined MS 0.983 vs new crypto EW 0.878, MV 1.217, MS 0.229, RP 0.929, **HRP 0.973**. Still beats all except MV, but the margin over crypto HRP collapsed from 0.175 (0.983 vs 0.808) to **0.010** (0.983 vs 0.973). "except for the Minimum Variance fund" now papers over a near-tie with HRP. Not silently rewritten (student's interpretation). Recommend adding a clause, e.g. "and only narrowly ahead of crypto HRP (0.973)". |
| §2 Crypto Max Sharpe "0.229" | Fixed in log 28 | Still the worst crypto fund (0.229 is lowest of the five). Claim holds. |
| §2 Crypto Min Variance "1.217, higher than every equity fund" | Fixed in log 28 | Still higher than every equity fund; the gap to the best equity fund (EW 0.687) is now larger, so the claim reads more strongly, not less. "Confounded by sample period" argument (1,208 vs 753 days) unchanged and still valid. |
| §2 "HRP does not outperform the max-sharpe funds" | **CLAIM PARTLY FALSE — FLAGGED** | True for equity (0.520<0.534) and combined (0.591<0.983), but crypto HRP (0.973) hugely outperforms crypto MS (0.229). Pre-existing (was 0.808 vs 0.190) but the fix widens it. Recommend scoping to equity/combined or rewording to "HRP rarely posts the top Sharpe". |
| §2 equity ranking (RP 0.580 > MS 0.534 > HRP 0.520...) | No | Equity only; untouched by annualisation. |
| §4 lexicon / fusion | No | Equity/sentiment only; no incidental crypto figure. |
| §5.3 "crypto drawdowns as deep as -89%" | No | Drawdown unchanged. |
| §6.1 "crypto MS -89% drawdown", "combined MS 0.983" | No | Drawdown + combined unchanged. |
| §6.3 recommendations | No | Only cites combined MS (26.6%, 0.983) and MS turnover; no crypto figure. |
| Table 1 (5 crypto rows) | Fixed in log 28 | ret/vol/Sharpe updated; drawdown unchanged. |
| Needs Review section | N/A | The student removed it from their hand-edited docx (it exists only in the stale `report_draft.md`). |

### `report/OUTLINE.md` (planning scaffold) — UPDATED
- §2.1 table, 5 crypto rows: ret/vol/Sharpe → current (e.g. MV 56.25%/53.74%/1.011 → 81.47%/64.68%/1.217).
- §2.2 bullets: "Crypto Max Sharpe (Sharpe 0.190, ret 14.17%)" → (0.229, 20.52%); "Crypto Min Variance Sharpe 1.011" → 1.217.
- The "Numbers changed" note (RF section): crypto line rewritten to show current Sharpes (EW 0.878, MV 1.217, MS 0.229, RP 0.929, HRP 0.973) with the pre-fix RF=0/√252 values kept as a parenthetical historical record.

### `PROJECT.md` — CLEAN (no per-fund crypto figures; grep empty).
### `streamlit_app.py` — CLEAN (no hardcoded crypto numbers; all chart data reads from `results/`, already regenerated).
### `report/report_draft.md` (stale AI draft, in-repo) — REGENERATED
- Re-ran `build_report.py` so the Table auto-loads current crypto rows from the CSV; prose "0.190"/"1.011" → "0.229"/"1.217"; Needs Review item 1 → 1.217.
- Deleted the stale `report/report.docx` that `build_report.py` regenerates (the graded report is `Project_B_report_word.docx`; I did not recreate a duplicate stale docx).
### `scripts/build_report.py` — UPDATED (source): 3 hardcoded crypto numbers (Section 2 prose x2 + Needs Review item) → 0.229 / 1.217.
### `scripts/run_part_b.py` — Figure 4 caption already updated in log 28 (√252 equity/combined, √365 crypto).
### Figures — regenerated in log 28 (Sharpe barplot etc. read from the corrected CSVs).

## Verify (step 6)
- Repo-wide grep (excl. `ai/` logs) for 50.7, 56.2, 14.2/14.17, 52.1, 52.8, 66.9, 53.7, 64.5, 65.1, 62.9, 0.730, 0.772, 0.808, 1.011, 0.190, 0.224: **zero stale instances** (only the deliberately-kept historical parenthetical in OUTLINE's change note).
- New figures present in the graded docx: 0.878 x1 (Table only), 1.217 x2 (Table + §2), 0.229 x2 (Table + §2), 0.929 x1, 0.973 x1; all five returns/vols x1 in Table 1. Correct counts.
- `check_handin.py`: passes (only cosmetic WARNs: PDF named `Project_B_report.pdf`, `__pycache__` to delete before zip).
- "Rebuild report.docx": the graded docx was NOT changed this pass (its crypto numbers were already correct from log 28; the only new findings are the two interpretive flags, which I did not silently edit). So no rebuild was needed. Removed the stale `report.docx` duplicate.

## What was wrong or risky
- The two comparison claims (§2 combined-MS-beats-all-crypto-except-MV, and HRP-does-not-outperform-max-sharpe) are the exact class of issue a literal grep misses: no number is wrong, but the meaning shifted. Flagged for the student rather than rewritten, since both sit in graded, own-words interpretation.
- Did NOT blindly "rebuild report.docx" from `build_report.py` — that pipeline is stale relative to the student's hand-edited `Project_B_report_word.docx` and would have destroyed their edits. Synced the real docx directly (log 28) and the draft artifacts separately.

## Corrections made
- OUTLINE.md, build_report.py, report_draft.md synced to current crypto numbers (factual). Two docx interpretive claims flagged, not edited.

## Not done (left for the student)
- **Re-export the PDF** from `Project_B_report_word.docx` (still missing crypto updates + Appendix E in the current `Project_B_report.pdf`).
- Decide on the two flagged comparison claims (§2 HRP near-tie; "HRP does not outperform max-sharpe").
- Code + regenerated `results/` + these doc syncs are uncommitted (commit not requested this turn).
