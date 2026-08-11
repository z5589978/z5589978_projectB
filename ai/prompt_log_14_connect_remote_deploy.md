# Prompt Log 14 - Connect Repo to GitHub + Deploy

**Session date:** 2026-08-12
**Task:** Link this local-only repo to GitHub, push all history, and hand off the
browser-based Streamlit Cloud deploy.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Connect the Repo to GitHub and Get Every Page Actually Live
>
> Confirmed: `git remote -v` is empty — this repo has never been linked to GitHub, so nothing (the redesign, HRP, the Fear & Greed page, any of it) has ever actually been pushed or deployed anywhere. Fix that properly now so every page is actually visible, not just present in the local files.
>
> ## 1. Verify locally first, independent of git/deploy
> Before touching git: run `streamlit run streamlit_app.py` locally (not just the headless AppTest from before) and actually click through all 5 pages yourself — Compare Funds, Fund Fact Sheet, My Allocation, Market Fear & Greed, Sentiment Analytics. Confirm each renders fully with real content, not just "no exception thrown." This isolates the problem to git/deploy, not the code, before we go further.
>
> ## 2. Set up the GitHub remote and push everything
> - Check whether I already have a GitHub repo created for this project anywhere (ask me if you're not sure — don't assume one exists or doesn't).
> - If none exists, create a new repository for this folder using your CLI if it's authenticated (**private** while I'm still building, per the brief's rule — I make it public myself at hand-in).
> - Add it as the `origin` remote and push `main`, with full history (all the commits currently sitting local-only — the redesign, HRP, idiom revert, everything).
> - If your CLI isn't authenticated to GitHub, stop and tell me exactly what you need from me (e.g. run `gh auth login`, or give you a repo URL to add manually) rather than getting stuck.
> - Confirm afterward with `git remote -v` and `git log origin/main -1` that the push actually landed and matches local `HEAD`.
>
> ## 3. Hand off the deploy step clearly
> The push gets the code to GitHub; the actual Streamlit Cloud deploy is browser-based and has to be me. Once the push is confirmed, tell me exactly what to do:
> - If no app has ever been deployed: go to share.streamlit.io, sign in, create a new app from the repo, entrypoint `streamlit_app.py`, pick the `main` branch.
> - If an app was deployed before from somewhere else (a different repo, or a much earlier version): tell me to check its settings on the Streamlit Cloud dashboard and either repoint it at this repo or reboot it, since a dependency change (`plotly` was added to `requirements.txt`) sometimes needs a manual reboot to pick up.
>
> ## 4. Final check
> Once I confirm I've deployed (or redeployed), don't just assume it worked — ask me to paste the live URL back to you if you're able to fetch it, or ask me to confirm directly that all 5 pages, including Market Fear & Greed and Sentiment Analytics, are visible and showing real numbers matching `results/tables/performance_metrics.csv` and `results/tables/fusion_comparison.csv`.
>
> ## 5. Log it
> Log this to the next `ai/prompt_log_1X_connect_remote_deploy.md` — this prompt verbatim, the local verification result from step 1, the push confirmation from step 2, and final confirmation from step 4 once I've done my part.
>
> Start with step 1 now.

---

## Step 1 — local verification (PASSED)

`streamlit run` live at http://localhost:8501 (HTTP 200). Per-page content check
(real rendered elements, not just no-exception):

| Page | markdown | tables | metrics | + charts |
|------|----------|--------|---------|----------|
| Compare Funds | 4 | 1 (perf metrics) | 0 | growth-of-$1 |
| Fund Fact Sheet | 4 | 1 (weights) | 4 (KPI cards) | growth+drawdown |
| My Allocation | 5 | 0 | 0 (until 100% set) | blended growth |
| Market Fear & Greed | 7 | 0 | 0 | gauge + z + 0-100 |
| Sentiment Analytics | 5 | 2 (fusion, coverage) | 3 (before/after) | sector index |

All 5 render real content. Problem is isolated to git/deploy, NOT the code.

## Step 2 — remote setup

- `git remote -v` empty; **14 commits on `main`**, all local-only (HEAD 719670c
  "Redesign app: migrate all charts to Plotly + UI polish").
- `gh` CLI was NOT installed. User chose "install gh and let Claude do it all."
- Installed gh 2.97.0 via Homebrew. `gh auth status`: not logged in.
- **Handed off to user:** run `! gh auth login` (GitHub.com -> HTTPS -> browser) in
  the session. Awaiting confirmation, then Claude creates private repo + pushes.

## Step 2 (cont.) — push confirmed

- User authenticated gh via device flow (2nd code, after the first expired) as
  **z5589978** (keyring, scopes gist/read:org/repo).
- `gh repo create z5589978_projectB --private --source=. --remote=origin --push`
  created the repo + set origin, but the initial push hit `HTTP 400 send-pack
  disconnect` (default 1 MB http.postBuffer vs a 7.5 MB pack).
- Fix: `git config http.postBuffer 524288000` + `http.version HTTP/1.1`, then
  `git push -u origin main` -> **[new branch] main -> main**.
- **Confirmed:** local HEAD == origin/main == 719670c; 14 commits on origin/main;
  repo PRIVATE at https://github.com/z5589978/z5589978_projectB.

## Step 3 — deploy handoff (user's browser step)

No app was ever deployed before (repo is brand new), so it's a fresh create on
Streamlit Community Cloud:
1. https://share.streamlit.io -> sign in with GitHub (z5589978).
2. Create app -> Repository: z5589978/z5589978_projectB, Branch: main,
   Main file path: streamlit_app.py -> Deploy.
3. First build installs requirements.txt (now includes plotly) — a few minutes.

## Step 4 — (pending) verify live
_To be filled once the user deploys and confirms all 5 pages render live with numbers
matching performance_metrics.csv / fusion_comparison.csv._
