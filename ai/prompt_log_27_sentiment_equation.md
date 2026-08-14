# Prompt Log 27 - Add the sentiment-scoring equation to the report (Appendix E)
**Session date:** 2026-08-14
**Task:** Add the equation used to score sentiment to the report docx, explained in the same appendix style as the five optimisation methods.

## Prompt used (verbatim)
> in the report under the docx file, could you also add in the equation used to score the sentiment, and explain the equation used to score the sentiment just like how you did in the appendix for the five optimisation methods

Follow-up (location clarified): "what I attached is a docx file but with the same report so you can edit it"

Follow-up (approved the two offers): "yes please" — (1) add a one-line pointer in §3.1 pointing to the new appendix, and (2) log it.

## AI output summary
Edited the student's hand-edited final report `report/Project_B_report_word.docx` directly (NOT via build_report.py, which is stale relative to this file). Added a new **Appendix E - Sentiment scoring**, styled identically to Appendix D's optimisation-method equations (centred mathtext image, right-flush equation number via tab stops, then a "where ..." definition sentence), continuing the global equation numbering at (8) and (9):

- **Equation (8), compound score:** `C = S / sqrt(S^2 + α)`, `S = Σ_i v_i`, `α = 15`. Where clause: C in [-1,+1] is the headline compound score; S is the sum of rule-adjusted token valences v_i, supplied by the FinVADER-Extended lexicon (123 words + 204 idioms); α = 15 is VADER's normalisation constant.
- **Equation (9), sector index:** `s̄_{k,t} = (1/|N_k|) Σ_{j∈N_k} C̄_{j,t-1}`. Where clause: equal-ticker-weight mean over sector k, lagged one trading day (no look-ahead), missing days carried forward then 0.

Also added a one-line pointer at the end of §3.1 ("The formal scoring equation, with every symbol defined, is in Appendix E."), mirroring the §1.2 -> Appendix D pointer.

Rendering approach: matplotlib mathtext -> PNG (same as Appendix D; python-docx has no reliable OMML path). Images saved to `results/figures/eq/eq8.png`, `eq9.png`.

## What I checked / verified
- **Verified α = 15 against the actual installed library**, not memory: `nltk.sentiment.vader` normalize is `score / sqrt(score*score + alpha)` with `alpha=15`. So equation (8) matches what `sia.polarity_scores()['compound']` actually computes; the FinVADER-Extended layer changes the valences v_i, not the formula.
- Test-rendered both equations and visually inspected the PNGs (eq8 the compound fraction, eq9 the barred sector-mean) - both typeset cleanly.
- Backed up the docx first (`report/Project_B_report_word.bak.docx`) before editing.
- Post-edit integrity check: inline shapes 14 -> 16; equations (1)-(9) all present; both new "where" sentences present; existing content intact (Appendix D, A/B/C, §6.3, §1, References all still there); pointer sits inside §3.1 before §3.2.
- Document structure confirmed the equations were the last content, so Appendix E appends cleanly.

## What was wrong or risky
- **Critical near-miss:** `report.docx` had been deleted and `build_report.py`/`report_draft.md` are now stale (they still hold the old flagged draft, not the student's hand-edits). Regenerating the docx from the pipeline would have destroyed all the student's own-words editing. Caught this before acting, surfaced it, and edited the student's supplied `Project_B_report_word.docx` in place instead.
- python-docx round-trips a Word file; complex features (TOC field, captions, page numbers) are preserved as opaque XML, but the student must open in Word and update fields so Appendix E appears in the TOC.
- The where-sentences use Unicode (α, subscripts) in plain Word text rather than typeset math - acceptable for a definition clause, consistent with Appendix D. No em dashes used.

## Corrections made
- None to revert. Non-destructive append; original backed up.

## Not done (left for the student)
- **Re-export the PDF.** The graded artifact `Project_B_report.pdf` does NOT yet contain Appendix E - open the updated docx in Word, update fields, export to PDF, and re-zip if the submission bundle was already built.
- Optional: delete the backup `report/Project_B_report_word.bak.docx` once satisfied.
