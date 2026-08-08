# Prompt Log 01 - Project B Kickoff & Scaffold

**Session date:** 2026-08-05
**Task:** Kick off Part B, set up AI logging, read Project A for context, read the starter folder and brief, create/update instruction files (CLAUDE.md, AGENTS.md, PROJECT.md), and produce a summary + proposed plan before any code is written.

---

## Prompt used (verbatim)

> Prompt for Claude Code — FINS3645 Project B Kickoff
>
> Paste everything below into Claude Code inside your <zID>_projectB folder.
>
> I'm starting Project B (Stations 3–4: Funds, Sentiment & App — 50% of the course, due Friday Week 11) for FINS3645. Project A (Stations 1–2: Data Foundation — 20%) is already done. Work through this in order:
>
> 0. Start AI logging now, with this exact prompt
>
> Before doing anything else, create/open the AI logging file for Project B (ai/prompt_log.md — match whatever log format I used in Project A's ai/ folder if one exists, otherwise start a clean one). Log this entire prompt verbatim, word-for-word, as the first entry, timestamped. Every subsequent prompt I give you, every non-trivial AI output you produce, and every fix/correction I make to your output must also be logged in this file as we go — this is graded (20% of Part B is "AI Workflow & Transparency"). Don't paraphrase my prompts in the log; log them verbatim.
>
> 1. Read Project A first
>
> Locate my <zID>_projectA folder (sibling folder under fins-agent/fins2026/, or wherever it lives in this repo). Read:
>
> report/report.pdf (or .docx) — understand what data foundation, cleaning decisions, and features I already built and justified.
> src/ and scripts/ — the actual ETL, cleaning, and feature-engineering code.
> results/data/, results/tables/ (especially dataset_inventory.csv and descriptive_stats_returns.csv), and any figures.
> README.md and my AGENTS.md/CLAUDE.md/.claude/ files from Project A — these tell you my app's name/value proposition and how I already instructed AI to work with me.
> ai/ prompt logs from Part A — see how I logged AI use so Part B logging stays consistent.
>
> Project A is the foundation Project B builds on. Do not redo Station 1–2 work (loading, cleaning, calendar alignment, text panel assembly). Reuse Project A's cleaned outputs and decisions directly in Project B — I'm allowed to reuse my own Part A in Part B per the brief.
>
> 2. Read the Project B starter folder and the project brief
>
> Read everything in the unzipped projectB_starter/ folder (or wherever I've placed it) — folder layout, provided src/data_access.py helper, any starter scripts, PROJECT_BRIEF.md, and context/ (data guide — treat as read-only, don't edit).
>
> Also read the full project brief (I've attached it — project_brief_FINS3645.pdf) for Part B in detail. Key things to hold yourself to:
>
> Part B required minimum (Station 3):
>
> A combined equity-plus-crypto fund with at least two optimisation methods (e.g. max-Sharpe/mean-variance tangency, min-variance, risk parity, equal-weight). Higher band = equity-only fund, crypto-only fund, extra/novel methods too, treating each (asset family, method) pair as its own fund.
> Walk-forward out-of-sample backtest: no look-ahead, weights formed only from past data, rebalance monthly-or-less-often, out-of-sample period starts after the initial estimation window. State first live backtest date, window length, rebalance frequency, risk-free assumption.
> One fact sheet per fund: growth of $1, annualised return, annualised volatility, Sharpe, max drawdown, current holdings/target weights. Compare funds.
> A sentiment model (VADER or another) scoring the assembled headlines → a standalone sector-level news-sentiment index, sector index built by averaging ticker-day sentiment within each sector, lag the sentiment signal by ≥1 trading day (no look-ahead), justify how no-headline ticker-days are treated (drop/carry-forward/neutral) and text-handling choices.
> Fuse sentiment into the equity funds (tilt/factor) and report a clear before-vs-after comparison — a negative result, explained, still counts as legitimate work, don't fake a win.
>
> Required exact output filenames (app + markers read these — don't rename):
>
> results/data/fund_returns.csv
> results/data/fund_weights.csv
> results/data/sector_sentiment_index.csv
> results/tables/performance_metrics.csv
>
> Station 4 (app):
>
> Build streamlit_app.py at the folder root: investor journey = compare funds, open a fund's fact sheet, set an allocation, view sentiment analytics.
> The deployed app must only read precomputed artifacts from results/ — never recompute backtests or import nltk/run VADER live (free tier can't handle it, and it's a listed common mistake that loses marks).
> Never commit raw .parquet/source data or secrets. Data only loads at build time through src/data_access.py.
> You (the agent) can prepare the repo, run scripts/check_handin.py, commit, and push to a new public GitHub repo. The actual share.streamlit.io deploy step needs my browser login — flag clearly when it's my turn to do that step.
>
> Run order specified by the brief: python scripts/run_part_b.py → streamlit run streamlit_app.py → python scripts/check_handin.py → git status.
>
> Report: report/report.docx → submit as report/report.pdf, max ~5,000 words/10 pages excl. appendix, structure: (1) funds & backtest design, (2) OOS results & fact sheets, (3) sentiment index, (4) extensions/innovations, (5) app & investor journey, (6) critical reflection with three concrete recommendations.
>
> 3. What an HD mark actually requires (don't just hit the minimum)
>
> Innovation & Data-Driven Results is 30% of Part B (the single largest criterion) and originality also lifts the Presentation, Economic Interpretation, and AI Workflow marks. A "prompt and paste" project that only does the required minimum will pass but will not reach HD. To land in the HD band (85-100) across the rubric, the work needs, across the whole project:
>
> At least one original, implemented, evidenced extension beyond the baseline and beyond what a simple AI prompt would produce — e.g. a wider/novel set of funds or optimisation methods, a new investment factor/signal (with its own equation), extending VADER's lexicon with finance terms, a new use of the news data (topic/entity tagging), a custom figure/design system rather than the provided style, a new robustness/data-quality test, or a genuinely valuable original app feature. One well-executed extension beats several shallow ones — don't spread thin.
> A correct walk-forward OOS backtest with correct 252-day equity vs 365-day crypto annualisation and no look-ahead anywhere (including the sentiment lag).
> All required exhibits self-contained (caption, labelled axes, units, sample period) and interpreted in prose, not dropped in raw.
> Fully reproducible end-to-end from a clean checkout against the hosted data.
> Economic interpretation and the written report must be in my own words — AI-generated reasoning submitted as mine is penalised, and verbatim AI prose is a listed way to lose marks. Draft with AI is fine; you (Claude Code) should flag anywhere you've written analysis/interpretation prose so I know to rewrite it myself before submission.
> A genuinely reflective, curated AI log (not just a prompt dump) showing where AI helped, where it was wrong, and what I corrected — this is 20% of the mark on its own.
> My own AGENTS.md/CLAUDE.md/.claude/ files actually replacing the placeholder stubs — an unreplaced placeholder caps the AI Workflow criterion at F.
>
> 4. Create context/instruction files — without clobbering what already exists
>
> Check what instruction/context files already exist in this <zID>_projectB folder (CLAUDE.md, .claude/, AGENTS.md, any other markdown). Do not overwrite or contradict anything already there. Specifically:
>
> If a CLAUDE.md/AGENTS.md already exists here (e.g. carried over or copied from Project A), read it fully first and only extend it with Part-B-specific instructions (required filenames, run order, "app never recomputes/imports nltk," logging requirement, etc.) rather than replacing sections that already cover shared conventions.
> If none exists yet, create CLAUDE.md (and .claude/ if useful) from scratch, populated with the Part B requirements above plus anything reusable from Project A's version (e.g. app name/value proposition, data provenance conventions) — but don't just copy Project A's file verbatim, since it was scoped to Stations 1–2.
> Create/update a PROJECT.md (or extend context/ if that's where I keep planning notes — but leave the provided context/ data-guide files themselves untouched, the brief says do not edit those) summarising: Part B scope, the four required output filenames, the run order, the mandatory hand-in structure (report/, src/, scripts/, results/, context/, ai/, AGENTS.md/CLAUDE.md, SUBMISSION_CHECKLIST.md), and a running checklist of the HD-band items from Section 3 above so we can track them as we build.
> Before writing any new file, check for naming/content collisions against existing markdown files in the folder and tell me explicitly if something I already have conflicts with what the brief requires, rather than silently overwriting it.
>
> 5. Confirm before heavy lifting
>
> Once you've done steps 1–4, give me a short summary of: what Project A gives us to reuse, what's missing/starter-only in Project B, and your proposed plan/order of work (funds → backtest → sentiment → fusion → app) plus your one proposed innovation angle — before you start writing substantial code.

---

## AI output summary

Claude Code (claude-sonnet-4-6) did the following:

1. Read all Project A files: CLAUDE.md, AGENTS.md, src/etl.py, src/features.py, ai/prompt_log_01_station1_etl.md (for format reference), results tables, context files.
2. Read all Project B starter files: src/data_access.py, src/backtest.py, src/portfolio.py, src/sentiment.py, src/etl.py (copy from Part A), scripts/run_part_b.py, scripts/check_handin.py, context/DATA_GUIDE.md, context/project_context.md, and the project brief PDF.
3. Noted that the starter results files (fund_returns.csv, fund_weights.csv, performance_metrics.csv) contain real computed data from a prior demo run — these will be regenerated by run_part_b.py.
4. Renamed `projectB_starter/` → `z5589978_projectB/` (check_handin.py validates this exact format).
5. Created: ai/prompt_log_01_kickoff.md (this file), CLAUDE.md, AGENTS.md, PROJECT.md, README.md, SUBMISSION_CHECKLIST.md, .streamlit/config.toml, requirements.txt, requirements-dev.txt.

One bug spotted in run_part_b.py lines 344–350 (Figure 6 Panel A): the first ax.plot() call has x/y axes transposed, and "Base (Equity MS)" is plotted twice on the same axis. Will note this in the plan summary and flag for correction before running.

---

## What I checked / verified

- Folder name: `z5589978_projectB` passes `re.fullmatch(r"z[0-9]{7}_project([AB])", name)`.
- Starter has NO existing CLAUDE.md, AGENTS.md, README.md, SUBMISSION_CHECKLIST.md — no collisions when creating.
- context/ files (DATA_GUIDE.md, project_context.md, verify_ai_output.md) are provided/read-only — NOT touched.
- Project A's ETL functions (load_clean_equities, load_clean_crypto, load_clean_news, build_combined_returns) are already copied verbatim into starter's src/etl.py — confirmed by matching imports in run_part_b.py.
- The results/ stub CSVs contain real data (equity OOS starts 2021-01-04, 753 days, as expected for a 252-day window over a 2020-2023 panel).

---

## What was wrong or risky (to verify before running)

1. **run_part_b.py Figure 6 bug (lines 344–350)**: first `ax.plot()` call has x and y transposed (`values` first, `index` second) and plots the same "Base (Equity MS)" series twice. Will produce a cluttered legend. Flag for fix before running.
2. **sector_sentiment_index.csv missing from starter** — not a bug; it's generated at build time and not a pre-seeded stub.
3. **streamlit_app.py does not exist yet** — to be written after plan is confirmed (Step 5).
4. **Innovation (extended VADER lexicon) not yet implemented** — proposed in plan summary, pending user sign-off.

---

## Corrections made

None yet — this is the first log entry. Subsequent entries will follow the same format.
