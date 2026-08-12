
# Prompt Log 19 - Full HD-grounded report draft (FT style, no em dashes)

**Session date:** 2026-08-12
**Task:** Produce a full AI-assisted DRAFT of report/report.docx (+ report/report_draft.md)
from OUTLINE.md and the verified results/ numbers, FT house style, no em dashes, ~5,000
words, for the author to review/verify/rewrite before submission. Draft status disclosed
at the top of the output and logged transparently (Part A logged the same in
ai/prompt_log_06_report_rewrite.md; the brief lists drafting as permitted AI use).

## Prompt used (verbatim)

> # Prompt for Claude Code — Write a Full HD-Grounded Draft From OUTLINE.md, FT Style
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> ---
>
> Write a full draft of the report, in `report/OUTLINE.md`'s structure, using everything actually in this project. This is a **draft for me to review, verify, and rewrite into my own words before submission** — not a finished document to hand in as-is. Say so explicitly at the top of the output file, and log this whole drafting pass transparently in `ai/`, the same way `ai/prompt_log_06_report_rewrite.md` in Part A logged AI-assisted report drafting. The brief lists "drafting" as permitted AI use, but the written analysis and economic interpretation still have to become genuinely mine through that review, not be submitted verbatim.
>
> ## 1. Re-ground yourself in everything first
>
> Re-read `report/OUTLINE.md`, every `ai/prompt_log_*.md` (01 through the latest), `PROJECT.md`, `src/portfolio.py`/`backtest.py`/`sentiment.py`, and every file in `results/data/`, `results/tables/`, `results/lexicon/`. Pull real numbers, not approximations — the outline already has most of them, but verify against the actual CSVs before writing.
>
> Also re-read the rubric section of `PROJECT_BRIEF.md` (Part B criteria) closely. For each of the six criteria (Funds 15%, Sentiment Index & Fusion 10%, Innovation & Data-Driven Results 30%, Streamlit App 15%, Economic Interpretation & Critical Reflection 10%, AI Workflow & Transparency 20%), write content that visibly satisfies the HD-band language specifically, not just adequate content — e.g. the HD band for Innovation wants an extension "shown with evidence," not just proposed, so make sure every innovation claim is backed by the actual numbers in `results/`.
>
> ## 2. Write the full draft, following the OUTLINE.md structure exactly
>
> All six sections, abstract, references, and appendix pointers, in order. Use the real findings already surfaced in the outline (Combined Max-Sharpe as the best risk-adjusted performer, Crypto Max-Sharpe's instability, HRP's lower drawdowns, the 204-vs-473-idiom dilution finding, the plain-VADER-vs-finVADER non-neutral rate comparison, the fusion tradeoff between Sharpe and drawdown) and actually reason through them with correct finance mechanism, not just restate the numbers. Every figure and table must be referenced and interpreted in the surrounding text, not dropped in raw.
>
> ## 3. Style: Financial Times house style
>
> - Lead each paragraph with the fact or number, then explain it — don't bury the finding at the end of a paragraph.
> - Short, declarative sentences. One idea per sentence. Active voice over passive.
> - Plain English over jargon; where a technical term is necessary (Sharpe ratio, look-ahead bias, quasi-diagonalisation, expanding window), define it briefly in-line the first time it's used.
> - Authoritative but not hyperbolic — state what the data shows and its limits, don't oversell a modest result (the fusion's +0.015 Sharpe improvement is a real but small effect, write it that way, not as a breakthrough).
> - No throat-clearing openers ("It is important to note that...", "This section will discuss..."). Start with substance.
> - No filler adjectives/adverbs. No emoji.
>
> ## 4. No em dashes anywhere
>
> Use a comma, colon, semicolon, or a full stop and a new sentence instead, whichever reads better. Before you finish, grep the whole output file for the em dash character (—) and fix every instance you find. Confirm the count is zero.
>
> ## 5. Length and format
>
> Target ~5,000 words / 10 pages excluding appendix and references, matching the brief's cap — check the actual word count when done and trim if over.
>
> Write the draft directly into `report/report.docx` — this is the brief's actual editable source (`report/report.docx is the editable source ... submit it as report/report.pdf`), not a planning aid, so produce the real Word document, not just markdown. Check first whether a `scripts/build_report.py`-style pattern already exists from Part A's approach (Part A's `ai/prompt_log_06_report_rewrite.md` references one) and reuse that pattern/tooling if it does, otherwise build the docx with `python-docx` (or an equivalent library already available): proper heading levels for the six sections, a title page, tables rendered as real Word tables (not pasted-in text) for the performance metrics and fusion comparison, and figures from `results/figures/` embedded as images where the outline calls for them. Keep a `report/report_draft.md` alongside it too, purely so I have an easy plain-text version to read and mark up before editing the docx directly.
>
> ## 6. Flag what needs my personal review hardest
>
> At the end of the draft, add a short "needs review" list: the specific interpretive claims that are the AI's best reasoning from the data but most need my own judgement and possible correction before they're truly mine (e.g. the explanation for why more idioms diluted the fusion benefit, or why Crypto Min-Variance beat every equity fund on Sharpe) — don't bury this, make it a clear checklist at the end of the file.
>
> ## 7. Log it
>
> Log this to the next `ai/prompt_log_1X_full_report_draft.md` — this prompt verbatim, confirmation of the em-dash check (zero found), the final word count, and the "needs review" list from step 6 restated so it's captured in the AI log too, not just the draft file.
>
> Start with the audit in section 1.

## AI output summary

- Built `scripts/build_report.py` (reuses Part A's docx pattern: Aptos font, navy
  headings, A4 geometry, page-number + TOC fields, navy/tinted styled tables, figure
  caption boxes). One prose source renders BOTH `report/report.docx` and a plain-text
  `report/report_draft.md`; a build-time word counter and figure/number loaders keep the
  draft tied to the CSVs.
- `report/report.docx` produced: cover page, amber DRAFT banner disclosing draft status,
  Abstract, TOC field, Sections 1-6 following OUTLINE.md exactly, References, Appendix
  (A HRP validation, B borderline idioms, C lexicon artifacts), and a Needs Review page.
- Real Word tables: Table 1 (15-fund performance) and Table 2 (fusion before/after).
- 7 figures embedded from results/figures/ (cumret_by_family, drawdown_combined,
  weights_over_time, sharpe_barplot, aggregate_sentiment_standardised, sector_sentiment,
  fusion_comparison), each with an interpreting caption and referenced in text.
- FT style throughout: number-first paragraph openers, short declaratives, terms defined
  inline on first use, modest framing of the +0.015 fusion result.

## What I checked / verified

- Verified every headline number against the actual CSVs before writing:
  - performance_metrics.csv: all 15 rows (e.g. Combined MS Sharpe 1.0334/ret 25.48%;
    Crypto MS 0.224/MaxDD -89.28%; Crypto MV 1.0466; HRP MaxDD equity -16.94/combined
    -18.41/crypto -78.05; Equity RP 0.724 > HRP 0.674 > MS 0.587).
  - fusion_comparison.csv: base ret 10.70%/Sharpe 0.587/MaxDD -26.07%; +tilt 11.00%/0.602/
    -26.66%.
  - before_after.csv: plain 51.13 / finVADER 39.27 / Extended 47.17 (recomputed +7.90 pt).
  - sentiment_coverage.csv: 80%/12.81, 99%/7.30, 100%/2.86.
  - aggregate_sentiment_index.csv: score_100 range 45.3-62.8; above 50 on 98.2% of days;
    z_expanding vs z_full corr 0.9983; latest z 2.251 (Extreme greed); span 2020-01-02 to
    2023-12-29.
  - lexicon counts: 123 words + 204 idioms (file line counts 124/205 incl header).
- Em-dash check done properly by extracting word/document.xml from the docx zip and
  scanning the md: em dash (U+2014) = 0 in both; en dash (U+2013) = 0 in both.
- 7 media images confirmed embedded in the docx.
- Grounded §5.3 target user in Part A's actual value proposition (>=$10,000, moderate-to-
  high risk, quantitative preference) read from Part A's build_report.py.
- `scripts/check_handin.py`: 23 checks passed.

## Em-dash confirmation

Zero. `word/document.xml` U+2014 count = 0; `report_draft.md` U+2014 count = 0 (en dashes
also 0 in both).

## Final word count

Body prose, Abstract through Section 6 (the brief's cap scope, excluding references,
appendix, and the needs-review page): **3,876 words**. Under the ~5,000-word cap, with two
tables and seven figures filling out the ~10-page length. Deliberately dense rather than
padded; leaves the author headroom to expand in their own words.

## Needs Review list (restated from the draft, step 6)

1. Section 2, crypto Minimum Variance Sharpe 1.047 vs equity funds framed as confounded by
   the different sample window (1,208 vs 753 days). Confirm the comparison is not
   like-for-like.
2. Section 2, combined Max Sharpe beating either class alone via diversification of the
   tangency portfolio. AI reasoning; restate in own words and check against mean-variance
   theory.
3. Section 3.2, plain VADER's higher non-neutral rate framed as finVADER correcting false
   positives (not being worse). Verify the reading and the Loughran & McDonald (2011) tie.
4. Section 4.2, 204 idioms beating 473 via quality-falls-as-frequency-threshold-drops.
   Confirm the mechanism; check borderline examples against kept_idioms.csv.
5. Section 4.4, deeper drawdown attributed to concentration into recently favoured sectors.
   Interpretation, not a measured decomposition; soften if unsupported.
6. Section 5.3, target user must match Part A exactly. Draft used Part A's value proposition;
   re-read the Part A report to confirm wording.
7. Section 6.3 rec 3, transaction costs hitting high-turnover Max Sharpe hardest.
   Directionally argued from Figure 3, not quantified; keep qualitative.
8. All references: verify every field and reconcile against Part A before submission
   (accents on Lopez de Prado / Korab stripped in draft, restore correct forms on verify).
9. Whole draft: AI-drafted prose. Rewrite the economic interpretation in own words per the
   AI-use policy before submission.

## What was wrong or risky

- The docx is a zip, so an initial in-script byte scan for em dashes was unreliable; I
  re-checked by extracting document.xml (authoritative result: 0).
- Draft prose is the AI's reasoning, not the author's. Draft status is disclosed in an
  in-document banner, the md header, and this log; the interpretation must still be
  rewritten by the author to satisfy the AI-use policy.
- Reference accents were stripped for encoding safety and are flagged for the author to
  restore and verify (citation-verification rule).

## Corrections made

- Switched the em-dash verification from a byte scan to a document.xml extraction so the
  zero-count is trustworthy; also checked en dashes (0) and both output files.
- Formatted all table numbers and negatives from the CSVs with ASCII hyphen-minus to keep
  the outputs dash-clean.
