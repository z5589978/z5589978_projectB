# Submission Checklist — Part B (z5589978_projectB)

Tick every item before zipping and submitting to Moodle.

## check_handin.py must pass all [FAIL] checks

- [ ] Run `python scripts/check_handin.py` — zero [FAIL] items.

## Folder name

- [ ] Folder is named exactly `z5589978_projectB`.

## Required files present

- [ ] `README.md`
- [ ] `SUBMISSION_CHECKLIST.md` (this file)
- [ ] `CLAUDE.md` — replaced placeholder with my own instructions
- [ ] `AGENTS.md` — replaced placeholder with my own instructions
- [ ] `streamlit_app.py`
- [ ] `requirements.txt`
- [ ] `.streamlit/config.toml`
- [ ] `context/DATA_GUIDE.md` (provided — not edited)
- [ ] `src/data_access.py`
- [ ] `report/report.pdf`
- [ ] `ai/` — at least one prompt log with curated entries

## Required output files

- [ ] `results/data/fund_returns.csv`
- [ ] `results/data/fund_weights.csv`
- [ ] `results/data/sector_sentiment_index.csv`
- [ ] `results/tables/performance_metrics.csv`

## Code and reproducibility

- [ ] `python scripts/run_part_b.py` runs end-to-end without errors from a clean state.
- [ ] `streamlit run streamlit_app.py` loads and shows the investor journey.
- [ ] No `.parquet` or source data files committed.
- [ ] No `.streamlit/secrets.toml` with real values committed.
- [ ] No `__pycache__/` or `.pyc` files in the zip (delete before zipping).

## Report

- [ ] `report/report.docx` is the editable source; `report/report.pdf` is the submission.
- [ ] Max ~5,000 words / 10 pages excluding appendix and references.
- [ ] Sections: (1) funds & backtest design, (2) OOS results & fact sheets,
      (3) sentiment index, (4) extensions/innovations, (5) app & investor journey,
      (6) critical reflection with 3 concrete recommendations.
- [ ] Every figure and table is self-contained (caption, labelled axes, units, sample period).
- [ ] Every exhibit is referenced and interpreted in the text.
- [ ] No unresolved `[HUMAN EDIT REQUIRED]` markers.
- [ ] No AI-drafted prose submitted as my own — all analysis rewritten in my words.
- [ ] No hard-banned words (delve, crucial, utilize, leverage-as-use, etc.).

## AI Workflow

- [ ] `CLAUDE.md` or `AGENTS.md` (at least one) has my own instructions — not the stub.
- [ ] AI prompt logs in `ai/` are curated: prompts verbatim, outputs summarised,
      bugs and corrections recorded.
- [ ] No leftover template placeholder text (the student zID placeholder) in any .md or .py files.

## Deployment (Part B specific)

- [ ] GitHub repo is PUBLIC at hand-in.
- [ ] Streamlit app is live at a share.streamlit.io URL.
- [ ] Live URL loads and shows the investor journey without errors.
- [ ] Submitted: live URL + public GitHub repo link alongside the Moodle zip.
