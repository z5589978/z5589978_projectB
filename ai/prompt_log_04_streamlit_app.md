# Prompt Log 04 - Finish and Deploy the Streamlit App (Station 4)

**Session date:** 2026-08-08
**Task:** Audit the existing Streamlit app, fix/verify it, check against the Station 4 HD bar, run mandatory checks, and prepare the repo for browser-based deploy.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Finish and Deploy the Streamlit App (Station 4)
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> We need to get the Streamlit app finished, verified, and pushed to GitHub so I can do the browser-based deploy. `streamlit_app.py` already exists with four pages (Compare Funds, Fund Fact Sheet, My Allocation, Sentiment Analytics) reading from `results/`, and `results/data/` already has `fund_returns.csv`, `fund_weights.csv`, `sector_sentiment_index.csv`, and `results/tables/performance_metrics.csv` populated. **Don't rebuild it from scratch — audit what's there first, then fix, verify, and prepare it for deploy.**
>
> ## 1. Audit before touching anything
> - Read the current `streamlit_app.py` in full.
> - Read `PROJECT.md`'s "Known issues to fix" section — it flags a bug in `scripts/run_part_b.py` lines ~344-350 (Figure 6 Panel A: x/y transposed on the first `ax.plot()` call, and "Base (Equity MS)" plotted twice). Confirm whether this has already been fixed by checking the current file and re-running `python scripts/run_part_b.py` — if the bug is still there, fix it and regenerate `results/`.
> - Check `requirements.txt` (should stay slim — pandas, numpy, scipy, matplotlib, streamlit, requests, pyarrow — **no nltk, no finvader**) and `requirements-dev.txt` (nltk/finvader belong here only, for local builds). Confirm the app itself never imports either at runtime.
> - Check `.streamlit/config.toml` exists and is sensible.
>
> ## 2. Test locally, page by page
> Run `streamlit run streamlit_app.py` and walk through all four pages yourself (read the rendered output/logs, don't just assume it works): [Compare Funds; Fund Fact Sheet; My Allocation incl 0%/not-100% edge cases; Sentiment Analytics]. Fix anything that errors, looks broken, or renders inconsistent numbers (e.g. cross-check a fund's Sharpe on the Compare page against its Fact Sheet page — they should match `performance_metrics.csv` exactly).
>
> ## 3. Check it against the Station 4 HD bar, not just "does it run"
> The rubric wants: a reliable app that loads the hosted data and supports the full investor journey, runs on a basic machine, and — for the top band specifically — has a polished, coherent design, ideally with an original design system rather than default Streamlit styling. Look at the current custom CSS/colour palette and tell me honestly whether it reads as a deliberate design system or just default Streamlit with a few colours added — suggest concrete improvements if it's the latter, but don't over-engineer past what a basic Streamlit Cloud instance can render fast. Confirm explicitly: the app must never import `nltk` or `finvader`, never call VADER/finVADER at runtime, and never recompute the backtest — grep the file to prove this rather than eyeballing it.
>
> ## 4. Run the mandatory checks
> - `python scripts/check_handin.py` — fix every `[FAIL]`, tell me which `[WARN]`s are just reminders vs worth fixing anyway.
> - Confirm nothing in `results/` is stale relative to the latest `run_part_b.py` run (regenerate if needed).
> - Update `PROJECT.md`'s App checklist section to reflect the real state once everything above is confirmed working — verify each one honestly rather than just ticking them.
>
> ## 5. Prepare the repo, then stop at the browser step
> There's no `.git` in this folder yet. Once everything above passes: init git, add a `.gitignore` that excludes raw `.parquet`/source data and any secrets; commit the code, requirements, `.streamlit/`, and the precomputed `results/` artifacts; create a **new, separate GitHub repository** (private while building) and push, if my CLI is authenticated — tell me clearly if it isn't. Then stop and hand it to me explicitly for: (1) sign in to share.streamlit.io and create a new app, entrypoint `streamlit_app.py`; (2) confirm the live app loads; (3) at hand-in, make repo public and give me the exact submission text.
>
> ## 6. Log it
> Log this session (this prompt verbatim, what you found in the audit, what you fixed, and the final state of the App checklist) to the next `ai/prompt_log_0X_streamlit_app.md`.

---

## What the audit found

1. **Figure 6 bug — already fixed** in Stage 3 (prompt log 02). Current run_part_b.py
   lines 344-347 compute base/fusion wealth once and plot each series once. No action.
2. **results/ not stale** — built 2026-08-05 12:28 from run_part_b.py (12:27); src/
   unchanged since (2026-06-17). Did NOT need to regenerate.
3. **requirements split correct** — app deps slim; nltk+finvader in -dev only.
4. **App runtime is clean** — grep proved no nltk/finvader/VADER/backtest/import src.
   Only imports: pathlib, pandas, streamlit (top); matplotlib, numpy (inline).
5. **FALSE caption (real problem)** — Sentiment Analytics page claimed "Extended
   finance lexicon applied (~80 domain terms)". The index is actually PLAIN VADER
   (Stage 5 finVADER switch still pending). Left as-is this would be a false
   methodology claim in a graded, deployed app.

## What I fixed

1. **Sentiment caption** — rewrote to truthfully describe plain VADER, equal-weight
   sector averaging, 1-day lag. Removed the false "extended lexicon (~80 terms)" claim.
2. **My Allocation blend correctness** — funds have different inception dates
   (crypto 2020-09-10 vs equity/combined 2021-01-04). Old `dropna(how="all")` +
   pandas skipna would report a partial-portfolio return on early dates for a mixed
   blend. Changed to `dropna(how="any")` so the blend spans only dates where every
   selected fund is live. Verified via headless test on a 50/50 crypto+equity blend.
3. **Deprecated API** — `use_container_width=True` (removed after 2025-12-31)
   migrated to `width="stretch"` in 3 dataframes; bumped nothing in requirements
   (streamlit>=1.35 already; local 1.58 confirms API). Deploy-safety fix.
4. **config.toml** — removed `enableCORS=false` (conflicted with XSRF protection,
   logged a warning; Cloud manages this anyway).
5. **Design system upgrade** — replaced the thin CSS (h1/h2/h3 navy only) with a
   coherent system: documented palette (navy/crimson/forest/gold + ink/muted/line/
   panel), system font stack, a branded gradient hero header on every page
   (render_header helper), styled metric cards, sidebar branding + methodology
   footer, bordered dataframes. CSS-only, renders fast on the free tier.

## Verification

- Headless `streamlit.testing.v1.AppTest` on all 4 pages: **zero exceptions**.
- My Allocation edge cases: 0% (info message), 30% (warning, no crash),
  mixed crypto+equity 50/50 blend (OK after the inception-alignment fix).
- Cross-check: all 12 funds' Sharpe recomputed the My Allocation way (x252)
  match performance_metrics.csv exactly — pages are numerically consistent.
- `python scripts/check_handin.py`: **21 passed**. WARNs: __pycache__ (cleaned),
  no report.pdf (Stage 9, expected).

## Honest design assessment (section 3 answer)

Before: default Streamlit + 4 colours + 3 lines of CSS = NOT a design system.
After: a deliberate, documented design system (header treatment, cards, typography,
sidebar branding, consistent palette) — supports the Station 4 HD "original design
system" bar without heavy components that would slow the free tier.

## Repo preparation

- Cleaned __pycache__/*.pyc.
- Wrote `.gitignore` excluding *.parquet, *.zip, secrets.toml, .env, caches, OS junk;
  explicitly KEEPS results/*.csv (the app needs them; free tier can't rebuild).
- `git init`, staged all, **safety-grepped: no .parquet/.zip/secrets staged**.
- Committed on `main`: "AlphaBlend Part B: funds, sentiment index, and Streamlit app".

## Blocked — handed to user

- **`gh` CLI is NOT installed**, so I could not create the GitHub repo or push.
  Git identity is set (z5589978). Local commit is ready; user must create the
  remote and push, then do the browser deploy.

## Final App checklist state

Done: app built, investor journey, results-only (grep-proven), locally tested,
numbers cross-checked, design system, config, requirements, API migration,
check_handin passes. Outstanding: create+push GitHub remote (needs user auth),
and the browser deploy on share.streamlit.io (user-only step).
