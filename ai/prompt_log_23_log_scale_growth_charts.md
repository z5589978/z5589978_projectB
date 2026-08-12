# Prompt Log 23 - Make every growth-of-$1 chart log scale
**Session date:** 2026-08-12
**Task:** Put the growth-of-$1 y-axis on a log scale on all three charts in the app (Compare Funds, Fund Fact Sheet, My Allocation).

## Prompt used (verbatim)
> # Prompt for Claude Code — Make Every Growth-of-$1 Chart Log Scale
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> ---
>
> Change the growth-of-$1 y-axis to a log scale everywhere it appears in the app, not just Compare Funds.
>
> ## 0. Scope correction before you start
>
> There are actually **three** growth-of-$1 charts in `streamlit_app.py`, not one:
> 1. **Compare Funds** (~line 259/288) — already has a `log_scale` toggle from an earlier change (`type="log" if log_scale else "linear"`), currently defaulting to linear.
> 2. **Fund Fact Sheet** (~line 330/340) — the growth+drawdown subplot, currently always linear, no toggle.
> 3. **My Allocation** (~line 396) — the blended-portfolio growth chart, currently always linear, no toggle.
>
> Apply the log-scale change to all three for consistency across the app.
>
> ## 1. Compare Funds — flip the default
>
> Keep the existing toggle (it's still useful for single-family filtered views where the magnitude spread is smaller), but change its default state so the chart opens in **log scale**, not linear.
>
> ## 2. Fund Fact Sheet and My Allocation — add log scale
>
> Set the y-axis on both of these growth-of-$1 charts to `type="log"` as well. Since each of these only ever shows one line (a single fund, or a single blended allocation), a toggle is less necessary than on Compare Funds — default to log directly unless you think a toggle is worth adding here too for consistency with Compare Funds' UI; your call, but tell me what you chose and why.
>
> ## 3. Sanity-check before shipping it
>
> A log-scale y-axis can't render values at or below zero. Before finalising, check that no fund's cumulative growth-of-$1 series ever touches zero or goes negative across the full backtest (it shouldn't, for a long-only portfolio, but confirm rather than assume) — if any series does dip to zero somewhere, tell me rather than silently letting Plotly drop those points.
>
> ## 4. Keep everything else as it is
>
> Don't touch the axis formatting (`tickprefix="$"`, `tickformat=".2f"`), the colour/dash encoding from the earlier declutter fix, or the hover behaviour — this change is scoped to the axis scale only.
>
> ## 5. Test and verify
>
> - `streamlit run streamlit_app.py`: Compare Funds (all four family filters), Fund Fact Sheet (a couple of different funds), and My Allocation (a blended selection) — confirm all three render correctly on log scale and remain readable.
> - `python scripts/check_handin.py`, fix any `[FAIL]`.
> - Commit and push.
>
> ## 6. Log it
>
> Log this to the next `ai/prompt_log_2X_log_scale_growth_charts.md` — this prompt verbatim, and note which of the two remaining charts got a toggle vs. a fixed log default.
>
> Start with step 1.

## AI output summary

Three edits in `streamlit_app.py`, scoped to the axis scale only:

1. **Compare Funds** (line 265): `st.toggle("Log scale", value=False → value=True)`. Toggle kept; help text extended to note you can turn it off for a single-family view. The axis line (`type="log" if log_scale else "linear"`) was already correct and unchanged.
2. **Fund Fact Sheet** (line 341): added `type="log"` to the growth-of-$1 y-axis (row 1 of the growth+drawdown subplot). The drawdown axis (row 2, percent) is untouched.
3. **My Allocation** (line 397): added `type="log"` to the blended-portfolio growth-of-$1 y-axis.

**Toggle vs fixed decision (step 2):** both Fund Fact Sheet and My Allocation got a **fixed log default, no toggle**. Reason: each renders a single series, so the linear/log comparison a toggle offers adds nothing useful; a fixed default keeps the UI clean (matching the app's declutter ethos) and makes growth-of-$1 read consistently on log across all pages. Compare Funds keeps its toggle because it is multi-series (up to 15 funds), where dropping back to linear is occasionally useful on a single-family filter.

Untouched as instructed: `tickprefix="$"`, `tickformat=".2f"`, the colour/dash encoding, and hover behaviour.

## Step 3 sanity-check result (before shipping)

Checked `results/data/fund_returns.csv` across all 15 funds:
- Worst single daily return anywhere: **-0.3034** (Crypto Equal Weight) — nowhere near -1.0, so no wealth series can be zeroed.
- Lowest cumulative growth-of-$1 point across all funds: **0.5315** (Crypto Max Sharpe) — strictly positive.
- Highest: 10.75, so the growth spread is ~20x (log scale genuinely helps).
- Because the worst daily return is well above -1, any convex combination of fund returns (a blended My Allocation) also stays above -1, so blended wealth is positive too.

Conclusion: **no series touches zero or goes negative on any of the three charts** (individual funds or blends), so log scale drops no points. No issue to flag.

## What I checked / verified
- Grepped to confirm exactly three growth-of-$1 y-axes exist and all three are now log (`value=True` toggle + two `type="log"` lines, plus the existing Compare Funds conditional).
- `python -c ast.parse` syntax check passed.
- Restarted the app headless: boots to HTTP 200 with no errors in the log.
- `python scripts/check_handin.py`: 22 checks pass, 0 FAIL.

## What was wrong or risky
- Log axes cannot show values <= 0; verified empirically (min wealth 0.53) rather than assuming, per step 3. The `add_hline(y=1)` reference line is safe on a log axis (log10(1)=0 renders normally).
- I could not visually confirm rendering (no browser in this environment), but the axis type is set in code and all data points are positive, so Plotly renders every point.

## Corrections made
- None.

## Not done (left for you)
- A visual eyeball of all four Compare Funds family filters, a couple of Fund Fact Sheet funds, and a blended My Allocation in the browser (the app is running locally on http://localhost:8501).
