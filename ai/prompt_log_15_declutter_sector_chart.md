# Prompt Log 15 - Declutter the Sector Sentiment Chart

**Session date:** 2026-08-12
**Task:** Make the 5-line sector sentiment chart on the Sentiment Analytics page
readable — bigger, per-chart hover, distinguishable lines, cleaner window control.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Declutter the Sector Sentiment Chart
>
> The sector sentiment chart on the Sentiment Analytics page (bottom of `streamlit_app.py`, the `sector_sent` block around line 470) is too cluttered — five constantly-crossing lines are hard to read, the rolling-window slider above it looks messy, and hovering shows every sector at once instead of just the line I'm pointing at. Fix all of this.
>
> ## 1. Make the chart bigger
> It currently renders via `apply_theme(fig, height=440)`. Increase the height (try ~560–600) so vertical separation between the sector lines is easier to read ...
>
> ## 2. Fix the hover behaviour — this chart only, not app-wide
> `apply_theme()` sets `hovermode="x unified"` (line ~116) ... Override `hovermode="closest"` locally on this chart's figure only, after calling `apply_theme()` — don't change the shared default ... Confirm the existing per-trace `hovertemplate` (`"%{y:.3f}<extra>%{fullData.name}</extra>"`) still shows the sector name and value correctly ...
>
> ## 3. Make individual lines easier to tell apart
> - Thicken the lines slightly (currently `width=1.6`) and check the `COLORWAY` palette ... NAVY and TEAL (the first and fifth colours) are both blue-leaning ... swap in a colour with more contrast ... or add a distinct dash pattern ...
> - Add a way to highlight one sector at a time on top of the existing multiselect: e.g. a "Highlight" selectbox (None + each selected sector) that ... renders the chosen line at full opacity/normal width and fades the others to ~25% opacity ... If Plotly's native legend click-to-isolate already works out of the box here, mention that ... consider adding a one-line caption ...
>
> ## 4. Clean up the rolling-window control
> Look at the current implementation (the `st.segmented_control("Quick window", ...)` preset pills plus the `st.slider(...)` ... synced via `st.session_state`). ... check whether the preset pills are actually rendering above it as intended (they don't appear in what I'm seeing) and fix if not. Then tighten the visual presentation ... consider grouping them in a bordered/padded container consistent with the rest of the app's card styling ...
>
> ## 5. Anything else you notice
> Look at this specific chart section ... for anything else that reads as cluttered or unfinished, and fix it — tell me what you changed beyond the four items above.
>
> ## 6. Test and verify
> [streamlit run + confirm less cluttered, nearest-line hover, intentional control; spot-check Compare Funds & Market Fear & Greed still unified hover; check_handin; commit + push, confirm push lands.]
>
> ## 7. Log it
> [log verbatim + changes.]
>
> Start with step 1.

---

## What changed

1. **Bigger chart:** height 440 -> **580**.
2. **Per-chart hover:** added `fig.update_layout(hovermode="closest")` AFTER apply_theme,
   on this chart only. Verified scoping by grep: apply_theme still sets `x unified`
   (shared default, line 126) and the only override is the sector chart (line 523) — so
   Compare Funds / Fund Fact Sheet / My Allocation / Market Fear & Greed keep unified
   hover. Existing hovertemplate kept (`%{y:.3f}<extra>%{fullData.name}</extra>`) — shows
   sector name + value on the nearest line.
3. **Distinguishable lines:**
   - New `SECTOR_PALETTE` reordered so the default first-five are maximally distinct
     (NAVY, CRIMSON, FOREST, GOLD, VIOLET) — TEAL pushed to 6th so no two blue-leaning
     colours sit adjacent. Line width 1.6 -> **2.6**.
   - Added a **"Highlight" selectbox** (None + each selected sector): the chosen line
     stays full-opacity/2.6px, the rest fade to 0.22 opacity / 1.5px.
   - Noted Plotly's **native legend click/double-click isolate** works for free —
     added to the caption ("click a sector in the legend to toggle it, double-click to
     isolate one").
4. **Window control cleanup:** grouped the preset pills + fine slider inside a
   `st.container(border=True)` card with a bold label, so it reads as one deliberate unit
   (matches the app's expander/alert border-radius treatment). Preset segmented_control
   label collapsed (the card heading labels it).

## Section 5 — extra changes beyond the four items
- Put the **Highlight** control in its own bordered card beside the smoothing card
  (two-column `st.columns([3,2])`) so the controls read as an intentional toolbar row.
- Added an **empty-state** `st.info("Select at least one sector …")` when the multiselect
  is cleared (previously the chart + caption just vanished with no explanation).
- Tightened the caption (folded the "fund tilt's input" note in, added the legend tip).

## Also in this commit (from the previous turn, not yet committed)
- **Sidebar nav visibility fix:** the redesign's `label div:first-child {display:none}`
  was hiding the nav option TEXT (so the sidebar showed no options and the user was stuck
  on page 1). Replaced with a safe rule that only scales/fades the small radio dot; active
  page = navy pill with white text. Nav options now visible.

## Verify
- All 5 pages pass headless AppTest. hovermode grep confirms only the sector chart uses
  "closest". check_handin passes. Committed + pushed to origin/main.
