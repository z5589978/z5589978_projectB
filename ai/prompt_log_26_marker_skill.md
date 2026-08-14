# Prompt Log 26 - Build a reusable rubric-marker skill + run it
**Session date:** 2026-08-14
**Task:** Build a reusable, strict, evidence-based Claude Code skill that marks the project against the real Part B rubric, and run it once to produce a self-assessment.

## Prompt used (verbatim)
> # Prompt for Claude Code — Reusable Strict Rubric Marker for Part B
>
> I want a reusable Claude Code skill that acts as a strict, evidence-based marker against the actual Part B rubric, so I can re-run it any time the project changes and see exactly where I currently sit before I hand in. This is a diagnostic tool only — it grades and cites evidence, it does not write or fix report content itself.
>
> 1. Ground it in the real rubric text, not a paraphrase
>
> Read report/project_brief_FINS3645 (1).pdf in full and pull out the exact Part B marking rubric (Section 9), all six criteria with their weights and full band text (HD/D/C/P/F), plus the "Mandatory Requirements" list and the "Required exhibits (Part B)" / "Required output filenames" lists from Section 5. For your reference, the six criteria and weights are:
>
> Funds: Optimal Portfolios & OOS Backtest (Station 3) — 15%
> Sentiment Index (standalone) & Fusion Extension (Station 3) — 10%
> Innovation & Data-Driven Results — 30%
> Streamlit App & Implementation (Station 4) — 15%
> Economic Interpretation, Critical Reflection & Writing — 10%
> AI Workflow & Transparency — 20%
>
> Pull the exact HD/D/C/P/F wording for each straight from the PDF rather than trusting my summary above — I only gave you the names and weights so you know what to look for.
>
> 2. Build the skill
>
> Create .claude/skills/mark-project-b/SKILL.md (create the .claude/skills/ directory if it doesn't exist) as a proper Claude Code skill. It should instruct whoever invokes it to act as an impartial, strict marker who:
>
> Grades each of the six criteria independently, citing specific evidence for every claim: exact file paths, line counts, grep results, table values pulled from results/tables/, word counts, whether required files exist under their exact required names (results/data/fund_returns.csv, results/data/fund_weights.csv, results/data/sector_sentiment_index.csv, results/tables/performance_metrics.csv). Never assert a band without pointing to the file/number that justifies it.
> For each criterion, states: the current best-supported band (HD/D/C/P/F), the specific evidence for that call, the single biggest gap preventing the next band up, and one concrete, actionable next step to close that gap.
> Separately checks the "Mandatory Requirements" as pass/fail gates, since failing one caps the relevant criterion regardless of how good the work is: own AGENTS.md/CLAUDE.md/.claude files actually replaced (not the placeholder stubs) and prompt logs present; the report's written analysis reads as the student's own (spot-check for verbatim-sounding AI prose in the graded interpretation sections); public GitHub repo at hand-in; deployed app never imports nltk or recomputes backtests at runtime.
> Explicitly does NOT rewrite, fix, or draft any report content, analysis, or interpretation — if it finds a gap that's a writing/analysis problem, it names the gap and stops there, it does not fill it in. This tool assesses, it does not author.
> Is honest about uncertainty — if something can't be verified from the repo alone (e.g. whether the live Streamlit URL actually works, since that requires a browser), it says so explicitly rather than assuming a pass.
> 3. Run it once now
>
> Invoke the skill you just built against the current state of the project, and save the output to ai/self_assessment_<today's date>.md. I want to see where things actually stand right now, criterion by criterion, before I do anything else with this.
>
> 4. Log it
>
> Log this to the next ai/prompt_log_2X_marker_skill.md — this prompt verbatim, confirmation the skill file was created, and a copy of (or pointer to) the self-assessment output from step 3.
>
> Start with step 1.

## AI output summary

**Step 1 — rubric extracted verbatim from the brief.** `pdftotext -layout report/project_brief_FINS3645 (1).pdf` → pulled Section 9 (Part B criteria table, all six with weights and full HD/D/C/P/F band text), the Mandatory Requirements block, and the Section 5 "Required exhibits (Part B)" (7 exhibits) and "Required output filenames" (4 exact paths). The band wording is embedded verbatim in the skill so it is self-contained and reproducible.

**Step 2 — skill created:** `.claude/skills/mark-project-b/SKILL.md` (created the `.claude/skills/` directory, which did not exist at the project's new location). The skill has YAML frontmatter (name/description) and instructs the invoker to act as an impartial strict marker with: hard rules (cite evidence for every band; assess-don't-author; honest about the unverifiable; grade current state not intentions; strict/lower-when-borderline); a Step 0 evidence-gathering checklist (required filenames, exhibits, fund coverage, look-ahead/annualisation, sentiment lag, app runtime safety, report artifact/word count/markers, AI files, repo visibility, check_handin); the full verbatim rubric for all six criteria; the Mandatory Requirements as pass/fail gates; and a fixed output format (evidence summary, mandatory table, per-criterion blocks with band + evidence + biggest gap + one next step, bottom line, unverified items).

**Note on project location:** at the start of this task the project folder had been **moved** from `fins2026/z5589978_projectB` to `fins-agent/z5589978_projectB` (the old path no longer existed). Located it via `find`, verified it was intact (its own git repo, brief PDF, results, etc.), and ran everything from the new path.

**Step 3 — skill run; output saved to `ai/self_assessment_2026-08-14.md`.** Summary of the marks (full evidence in that file):

| Criterion | Wt | Band | One-line reason |
|---|---|---|---|
| 1 Funds & OOS Backtest | 15% | **D** | All HD breadth (15 funds, no look-ahead, all exhibits) BUT crypto annualised √252 not √365 (`backtest.py:32`; crypto n_days=1208 on 365-cal) |
| 2 Sentiment & Fusion | 10% | **HD** | Validated sector index + look-ahead-safe fusion measured & assessed (0.534→0.552, +0.018) |
| 3 Innovation | 30% | **HD** | Custom 123-word/204-idiom lexicon w/ before-after + honest negative result; HRP; custom Plotly design system |
| 4 App & Implementation | 15% | **D** (HD contingent) | Full journey, public repo, runtime-safe — but **live load UNVERIFIED** (needs browser) |
| 5 Interpretation & Writing | 10% | **D** | 3 concrete recommendations in own words; own-words full authorship only spot-checkable |
| 6 AI Workflow | 20% | **HD** | Own AGENTS.md/CLAUDE.md/.claude + 25 curated logs with corrections |

Mandatory gates: AI submission PASS; own-writing PASS (spot-check, partly unverified); academic integrity PASS (spot-check); deployment PASS on repo+app, live-load UNVERIFIED.

**Top-3 highest-leverage fixes flagged:** (1) crypto annualisation √252→√365 (C1, 15%); (2) verify the live app loads in a browser (C4, 15% + deployment gate); (3) own-words/every-exhibit-interpreted pass + drop 3 uncited references (C5, 10% + mandatory gate).

## What I checked / verified
- Extracted the rubric text directly from the PDF (not a paraphrase); embedded verbatim in the skill.
- Ran real evidence commands from the project root and cited concrete outputs (file existence, `performance_metrics.csv` grouping, grep line numbers in `backtest.py`/`sentiment.py`/`streamlit_app.py`, word counts, marker counts, `gh` visibility, `check_handin`).
- Confirmed the surviving methodological finding (crypto √252 vs √365) against both the code (`ANNUALISE=252`) and the data (`n_days=1208`).

## What was wrong or risky
- The project folder had been moved; the original path 404'd. Located and used the new path rather than failing.
- The report is the student's hand-edited PDF (docx deleted), so `report_draft.md`/`build_report.py` are now stale relative to the final PDF — I graded the PDF, not the draft.
- Authorship and live-app-load genuinely cannot be verified from the repo; both are marked UNVERIFIED rather than assumed pass.

## Corrections made
- None — this task builds an assessment tool and runs it; it does not modify report content (by design).

## Not committed
- The skill, self-assessment, and this log are new files under the (moved) project repo; commit/push were not requested in this prompt.
