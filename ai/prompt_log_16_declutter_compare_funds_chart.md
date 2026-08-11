# Prompt Log 16 - Declutter the Compare Funds "Growth of $1" Chart

**Session date:** 2026-08-12
**Task:** Fix the Compare Funds growth-of-$1 chart — colour-repeat bug (10-colour
cycle vs 15 funds), unified hover clutter, wide magnitude range, and general clutter.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Fix the Compare Funds "Growth of $1" Chart
>
> Same two problems as the sector sentiment chart, now on the Compare Funds page's "Growth of $1" chart ... with all 15 funds shown ("All" family filter), the lines are too cluttered to read, and hovering shows the whole 15-item legend instead of just the line under the cursor. Fix both — plus there's a real underlying bug causing part of the clutter, not just a styling issue.
>
> ## 1. Root cause: the colour palette repeats after 10 funds ...
> Fix it properly ... encode method -> colour (5 methods: EW/MV/MS/RP/HRP, one colour each) and family -> line style (solid Equity, dashed Crypto, dotted Combined). ... semantically meaningful — the same colour always means the same method ...
>
> ## 2. Fix the hover — this chart only ... Override hovermode="closest" locally ... regardless of which family filter is selected.
>
> ## 3. Genuine scale problem ... Add a small toggle/checkbox ("Log scale") that switches the y-axis to type="log" ... Default to linear ... unless you think log should be the default specifically when "All" is selected — your call, but tell me what you chose and why.
>
> ## 4. Other decluttering — increase chart height; consider a "Highlight" selector (None + each fund) fading others to ~25%; consider grouping/moving the 15-item legend.
>
> ## 5. Test and verify — all four family filters; no two funds share identical colour+style; nearest-line hover; log toggle works; numbers unchanged; check_handin; commit+push (confirm it lands).
>
> ## 6. Log it ... the colour-repeat bug you found and how you fixed it, and what you chose for the log-scale default.
>
> Start with step 1.

---

## The colour-repeat bug + fix

`apply_theme()` sets `colorway=COLORWAY` (10 colours). With "All" selected, 15 funds
are plotted, so Plotly cycled the palette back to the start — funds 11-15 rendered in
the SAME colours as funds 1-5 (genuinely indistinguishable, not just busy).

**Fix (not just more colours):** a `fund_style(name)` helper encodes
- **method -> colour** (METHOD_COLOR: EW=steel, MV=navy, MS=forest, RP=crimson, HRP=violet)
- **family -> dash** (FAMILY_DASH: Equity solid, Crypto dashed, Combined dotted)

Verified this yields **15 unique (colour, dash) combinations** for the 15 funds (a
5x3 bijection) — and it's semantic: the same colour always means the same method, so
you can eyeball "Max-Sharpe across all three families" (three forest lines: solid/dashed/
dotted) at a glance.

## Other changes
- **Hover:** `fig.update_layout(hovermode="closest")` after apply_theme, on this chart
  only (grep-confirmed: shared default `x unified` at line 126; overrides only on this
  chart + the sector chart; Fund Fact Sheet / My Allocation / Market Fear & Greed keep
  unified). Applies to every family filter (same code path). Existing hovertemplate keeps
  name + $value on the nearest line.
- **Log scale toggle:** `st.toggle("Log scale", value=False)` -> y-axis
  `type="log" if log_scale else "linear"`.
- **Height:** 440 -> 560.
- **Highlight selectbox:** None + each fund; the chosen line stays 2.2px/full opacity,
  the rest fade to 0.22 opacity / 1.3px.
- **Legend:** when >6 funds ("All" = 15), moved to a vertical right-side legend (frees
  the top, was 3 stacked rows); family views (5 funds) keep the top horizontal legend.
- **Caption** explains the colour=method / style=family encoding + legend isolate tip.

## Log-scale default — my choice
**Defaulted to LINEAR for every filter** (current behaviour), log is one toggle away.
Reasoning: within a single family the fund magnitudes are similar, so linear is clearer
there and log would be overkill/confusing; keeping one consistent default across all
filters is more predictable than silently switching to log only on "All". The toggle's
help text points out log is the fix for the "All" view where crypto dwarfs equity/combined.

## Verify
- 15 funds -> 15 unique (colour,dash) combos (checked). All 5 pages + all 4 family
  filters + log-on pass headless AppTest. Rendering-only change — CSVs/numbers untouched.
- check_handin passes. Committed + pushed; origin/main == local HEAD.
