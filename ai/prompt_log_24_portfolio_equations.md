# Prompt Log 24 - Add formal equations for all 5 portfolio methods
**Session date:** 2026-08-13
**Task:** Add numbered, typeset equations for all five portfolio-weighting methods to the report, each ending in a comma and followed by a "where ..." definition sentence, in the style of a paper's Model section.

## Prompt used (verbatim)
> # Prompt for Claude Code — Add Formal Equations for All 5 Portfolio Methods
>
> Paste this into Claude Code in my `<zID>_projectB` folder.
>
> ---
>
> I want numbered, formally typeset equations for all five portfolio-weighting methods in the report, in the style of an academic paper's "Model" section: each equation centred with its number flush right (e.g. `(1)`), ending in a **comma**, immediately followed by a "where ..." sentence defining every symbol — not a plain-English paraphrase instead of the actual formula.
>
> ## 1. Read first
>
> Read `src/portfolio.py` in full (all five functions) and `report/report_draft.md`/`report/report.docx`/`report/OUTLINE.md` as they currently stand, so the equations match what's actually implemented, not a generic textbook version, and so you know where the methods are already discussed qualitatively in Section 1.
>
> ## 2. The five equations — match these exactly to the code, don't reformulate them
>
> **Equal Weight:**
> $$w_i = \frac{1}{N}, \quad i = 1, \dots, N,$$
> where $N$ is the number of assets in the fund.
>
> **Minimum Variance:**
> $$\min_{w} \; w^\top \Sigma w \quad \text{s.t.} \; \mathbf{1}^\top w = 1,\; 0 \le w_i \le 1,$$
> where $\Sigma$ is the sample covariance matrix of daily returns over the estimation window.
>
> **Maximum Sharpe (tangency portfolio):**
> $$\max_{w} \; \frac{w^\top (\mu - r_f)}{\sqrt{w^\top \Sigma w}} \quad \text{s.t.} \; \mathbf{1}^\top w = 1,\; 0 \le w_i \le 1,$$
> where $\mu$ is the sample mean daily return vector and $r_f$ is the mean daily risk-free rate over the same estimation window (the real Fama/French rate, not zero — this is the post-feedback version).
>
> **Risk Parity:**
> $$\min_{w} \; \sum_{i=1}^{N} \left( \frac{w_i (\Sigma w)_i}{w^\top \Sigma w} - \frac{1}{N} \right)^2 \quad \text{s.t.} \; \mathbf{1}^\top w = 1,\; w_i \ge 0,$$
> where $w_i(\Sigma w)_i / (w^\top \Sigma w)$ is asset $i$'s fractional contribution to total portfolio risk, equalised across all assets at the optimum.
>
> **Hierarchical Risk Parity** (three equations, one per step — cite López de Prado (2016)):
> $$d_{i,j} = \sqrt{\tfrac{1}{2}(1 - \rho_{i,j})},$$
> where $\rho_{i,j}$ is the sample correlation between assets $i$ and $j$, used to build the distance matrix for tree clustering.
> $$V_C = w_C^\top \Sigma_C w_C, \quad w_{C,i} = \frac{1/\sigma_i^2}{\sum_{j \in C} 1/\sigma_j^2},$$
> where $V_C$ is a cluster's variance under inverse-variance weighting, used to compare two candidate sub-clusters at each split.
> $$\alpha = 1 - \frac{V_L}{V_L + V_R}, \quad w_i \leftarrow \alpha w_i \; (i \in L), \quad w_i \leftarrow (1-\alpha) w_i \; (i \in R),$$
> where $L$ and $R$ are the two sub-clusters at a split and $\alpha$ allocates more of the parent's weight to the lower-variance side, recursively down to single assets.
>
> All five methods are long-only and fully invested ($w_i \ge 0$, $\sum_i w_i = 1$) by construction or by constraint, consistent with the rest of the report.
>
> ## 3. Formatting — match the screenshot's typeset quality as closely as you can
>
> Use native Word equation objects (OMML) if you can generate them reliably via `python-docx`/direct XML manipulation, so they're properly typeset and still editable in Word. If that's not reliably achievable in this environment, fall back to LaTeX-rendered images (e.g. via matplotlib's mathtext) embedded centred with the equation number in a right-aligned tab stop, which gets visually closest to the screenshot without needing a full LaTeX toolchain. Tell me which approach you used and why.
>
> ## 4. Decide whether this fits in the main body or needs to go in an appendix — actually check, don't guess
>
> The report was at 4,255 words as of the last check, against the ~5,000-word cap — but that count does **not** yet include the prose I still owe: the two `[STUDENT TO WRITE:]` placeholders and the several HUMAN EDIT REQUIRED flags from the RF update, all of which are currently just markers, not finished text. Estimate realistically how many words those will add once I fill them in (skim their placeholder instructions for a sense of how much each needs), work out the actual remaining headroom, and only then decide:
> - If there's genuinely enough room, add the full equations block to Section 1 where the methods are already discussed.
> - If it's tight, put the full equations in an appendix instead (the brief explicitly excludes appendix content from the word cap) and add one short pointer sentence in Section 1 ("see Appendix D for the formal specification of each method") — this is a completely normal way to handle it and costs almost nothing against the cap.
>
> Tell me which you chose and the actual numbers behind the decision, don't just pick one silently.
>
> ## 5. Rebuild and verify
>
> - Rebuild `report/report.docx` from `scripts/build_report.py` (or whatever the established pipeline is) so the two stay in sync.
> - Open/inspect the regenerated docx to confirm the equations actually render correctly, not just that the code ran without error.
> - Recheck the word count against the cap given your decision in step 4.
> - Confirm zero em dashes, same rule as before.
>
> ## 6. Log it
>
> Log this to the next `ai/prompt_log_2X_portfolio_equations.md` — this prompt verbatim, which formatting approach you used, and the word-budget reasoning behind the main-body-vs-appendix decision.
>
> Start with step 1.

## AI output summary

### Step 1 — code/report read
Re-read `src/portfolio.py` (all five functions) and confirmed each equation matches the implementation, not a textbook version:
- `equal_weight`: `np.full(n, 1/n)` = eq (1).
- `min_variance`: minimise `w'Σw` s.t. sum=1, bounds [0,1] = eq (2). The `_clean_cov` ridge is a numerical-stability detail the equation omits.
- `max_sharpe`: minimise `-(w'(μ-rf))/sqrt(w'Σw)` = maximise the Sharpe = eq (3); `excess = mu - rf` where `rf` is the window-mean daily rate.
- `risk_parity`: minimise `Σ_i (w_i(Σw)_i/(w'Σw) - 1/N)²` s.t. sum=1, w_i≥0 = eq (4).
- `hierarchical_risk_parity`: `d=sqrt(0.5(1-corr))` (5); `_cluster_var` returns `ivp@sub@ivp` with inverse-variance weights = V_C (6); `alpha = 1 - cv_l/(cv_l+cv_r)`, left*=alpha, right*=(1-alpha) (7). All match.

### Step 3 — formatting approach used: matplotlib mathtext images (not OMML)
`python-docx` has no native Word-equation (OMML) API. The reliable OMML routes need either hand-written OMML XML for fractions/sums/roots (error-prone and not verifiable in this headless environment) or Word's `MML2OMML.XSL` transform (not available here). So I used the prompt's sanctioned fallback: render each equation from LaTeX with matplotlib's mathtext (no LaTeX toolchain needed) to a transparent PNG at 200 dpi, embedded centred via a centre tab stop with the equation number right-flushed via a right tab stop. mathtext needed two symbol swaps from the prompt's LaTeX: `\le`/`\ge` -> `\leq`/`\geq` and `\tfrac` -> `\frac` (verified by test-rendering all seven before wiring in). The equation content is identical; only the rendering dialect changed. Trade-off: the images are not editable as equations inside Word (an OMML object would be), but they are correctly typeset and verifiable.

### Step 4 — placement decision: Appendix D + a pointer sentence (with the numbers)
- Current body: 4,255 words (pre-change).
- The five still-unwritten markers in the counted body hold 318 words of placeholder/flag instruction text that the author will swap for real prose. Realistic finished prose for them is roughly 340 to 480 words, so the net addition is about +20 to +160 (and could be more if written generously).
- The equations' seven "where" sentences plus lead-ins are about 180 words of prose, and the equation objects themselves consume main-body page space against the report's ~10-page main-body limit.
- Body in the main-body case would land around 4,600 to 4,900+ once the author fills the markers, which is tight, and the page limit tightens further.
- The brief excludes appendix content from the word cap. Putting the equations in Appendix D costs ~0 against the cap; the only body cost is the one pointer sentence ("The formal specification of each method, with every symbol defined, is in Appendix D.").
Decision: **Appendix D**, full equations there, one pointer sentence in Section 1.2. This de-risks both the word cap and the page limit.

### Implementation (scripts/build_report.py)
- Added matplotlib/PIL imports, an `EQ_DIR = results/figures/eq/`, an `H3()` helper, a `_render_eq()` LaTeX->PNG renderer, and an `EQUATION()` helper that embeds the centred image with a right-flush `(n)` and then emits the "where ..." sentence as normal prose (uncounted, since it is in the appendix).
- New **Appendix D "Formal specification of the portfolio methods"** with an intro, an H3 per method, equations (1)-(7), and a "where ..." sentence under each. HRP has three equations under one heading, citing López de Prado (2016).
- One pointer sentence added to Section 1.2.

### Step 5 — rebuild and verify
- Rebuilt report.docx and report_draft.md from build_report.py (in sync).
- Inspected the regenerated docx (not just that it ran): 14 inline shapes (7 figures + 7 equations); Appendix D heading present; all seven equation paragraphs end in a right-flush (1)-(7); all seven "where" sentences present; all five method H3 headings present; the Section 1.2 pointer present. Visually inspected the rendered equation PNGs (eq4 with the summation and squared fraction, eq7 with the recursion arrows) - both typeset cleanly.
- Body word count: 4,269 (was 4,255; +14 from the pointer sentence), comfortably under the ~5,000 cap. Appendix content is not counted.
- Em dashes across outputs: 0.
- check_handin.py: 22 pass, 0 FAIL.

## What I checked / verified
- Test-rendered all seven equations standalone before wiring them in, to catch the mathtext symbol issues (`\le`/`\ge`/`\tfrac`).
- Verified the docx embeds 14 inline shapes and that every equation number, "where" sentence, and method heading is present.
- Word count and em-dash count both within limits; check_handin clean.

## What was wrong or risky
- OMML was not reliably achievable; used images and said so, per the prompt.
- mathtext rejects `\le`, `\ge`, `\tfrac`; swapped to `\leq`, `\geq`, `\frac` (same meaning).
- The "where" sentences use Unicode Greek (Σ, μ, ρ, σ, α) and inline subscripts (w_i, r_f, V_C) in plain Word text rather than typeset math; acceptable for a definition clause, but if you want those symbols typeset too, that would need the same image treatment.
- Equation images are not editable as Word equation objects. If you specifically need in-Word editable equations, tell me and I can attempt the OMML XML route, accepting it is harder to verify.

## Corrections made
- None to revert.

## Not done (left for you)
- If you prefer native (editable) Word equations over images, that is a follow-up.
- The existing STUDENT TO WRITE placeholders and HUMAN EDIT flags are still yours to write; PDF export from Word remains your step.
