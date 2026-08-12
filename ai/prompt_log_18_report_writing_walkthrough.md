# Prompt Log 18 - Report Writing Walkthrough (coaching, not drafting)

**Session date:** 2026-08-12
**Task:** Coach the student through writing report/report.docx section by section from
report/OUTLINE.md — explain what each part needs, define terms in plain English, walk
through the evidence, ask guiding questions for each [STUDENT TO WRITE] placeholder
(NOT answer them), and review the student's own paragraphs without rewriting them.

---

## Prompt used (verbatim)

> Read report/OUTLINE.md. I want to actually write report/report.docx myself, section by section, with you coaching me through it rather than drafting it for me.
>
> Go through the outline in order — Section 1, then 1.x within it, then Section 2, and so on. For each subsection:
>
> Tell me plainly what this part needs to say and why it matters for the grade (which rubric criterion it feeds).
> Break down any technical term in it in plain English before I write about it — Sharpe ratio, max drawdown, look-ahead bias, quasi-diagonalisation, recursive bisection, expanding window, cross-sectional median split, whatever's relevant to that bit — assume I need it explained simply, not just named.
> Walk me through the actual numbers/evidence the outline points to for this section, so I understand what they show before I try to explain it.
> For any [STUDENT TO WRITE: ...] placeholder, don't answer it — ask me guiding questions that help me work out my own explanation, and only after I've had a go, tell me if I've missed something important or got the mechanism wrong.
> Once I've written my own paragraph for that bit, you can review it for clarity and accuracy, but don't rewrite my sentences for me — tell me what's unclear or wrong and let me fix it.
>
> Pause after each subsection and wait for me before moving to the next one — don't run ahead through the whole outline at once.
>
> Log this session to the next ai/prompt_log_1X_report_writing_walkthrough.md as we go — this prompt verbatim, and a note of which sections we got through.

---

## Progress log (sections covered)

- Section 1.1 (Walk-forward design) — coaching delivered (what/why, plain-English terms,
  evidence, 4 guiding questions for the "defensible design" placeholder). Student moved
  on before pasting a paragraph; 1.1 placeholder still open to revisit.
- Section 1.2 (Five optimisation methods) — coaching delivered (plain-English on Σ + all
  5 methods, HRP's 3 steps in depth, synthetic-validation evidence 0.901 vs 0.099;
  3 guiding questions for the HRP-validation one-liner placeholder). Student moved on.
- Section 1.3 (Fund universe & innovation flag) — coaching delivered (15 funds vs the
  ~2 minimum; wider=15 funds, newer=HRP; rubric-wording link; caution not to over-claim
  vs the Section-4 lexicon headline; 3 guiding questions). Awaiting student. Section 1
  complete on the coaching side.

- Section 2.2 (Results worth discussing) — coaching delivered: defined Sharpe ratio +
  max drawdown plainly, recapped the Section-1.2 mechanisms + kurtosis + 252-vs-365
  annualisation caveat, walked the exact numbers for all 5 flagged results
  (Combined MS 1.033; Crypto MS 0.224/−89.28%; Crypto MV 1.047 vs equity; HRP lowest
  MaxDD every family; Equity RP 0.724 > HRP 0.674 > MS 0.587), and gave guiding
  questions for each of the 5 [STUDENT TO WRITE] interpretations (did NOT answer them).
  Skipped 2.1 (the reference table needs no interpretation). Awaiting student.

- Section 2.3 (Required exhibits checklist) — coaching delivered: the self-contained +
  interpreted-in-text rule (Presentation 15%, the "never drop raw" mark), the 5 exhibit
  files, plain-English on each figure (growth-of-$1, drawdown, weights-over-time, Sharpe
  barplot), guiding questions for the one-sentence-per-figure interpretation, and Word
  mechanics (use results/figures PNGs not app screenshots; Caption style + cross-refs;
  verify axes/units/period). Awaiting student. Section 2 complete on coaching side.

- Section 3.1 (Scoring model: FinVADER-Extended) — coaching delivered: plain-English on
  VADER/compound score/lexicon, finVADER base (SentiBigNomics ~7,295 + Henry 189, Koráb
  2023/Week 9 — off-the-shelf) vs the student's own layer (123 words + 204 idioms), the
  10-agent panel + agreement filter (|mean|≥0.5, std<2.0), phrase-collapsing gist
  (detail deferred to §4). Emphasised borrowed-vs-built attribution (integrity mark) and
  scope discipline (don't duplicate §4). 3 guiding questions for the framing; flagged two
  review checks (no claiming finVADER as own; filter = agreement not hand-pick). Awaiting.

- Section 3.2 (Before/after coverage) — coaching delivered: plain-English on
  non-neutral/coverage, false positives, Loughran & McDonald (2011); the three numbers
  (plain 51.13 > finVADER 39.27; Extended 47.17 = +7.9 over finVADER); the "finVADER
  looks worse but it's a correction" trap; 4 guiding questions for the [STUDENT TO WRITE]
  interpretation; and the coverage≠accuracy honesty caveat (quantity not quality; the
  "profit warning +0.13" qualitative evidence). 3 review checks flagged. Awaiting student.

- Section 3.3 (Sector-level construction) — coaching delivered: plain-English on
  equal-ticker-weight aggregation, the shift(+1) lag (= same no-look-ahead rule as §1.1),
  and the two-part missing-day rule (ffill = persistence assumption; leading 0 = neutral
  prior). 4 guiding questions for the [STUDENT TO WRITE] justification (ffill risk of
  staleness; why 0 not drop; why-not-drop tied to the fixed-calendar/merge requirement
  the tilt needs; equal-ticker vs headline weighting). Flagged a verify-first: confirm
  whether the 0-fill happens on the raw compound series (0=neutral) or the 0-100 series
  (50=neutral) and state the correct scale. 3 review checks flagged. Awaiting student.

- Section 3.4 (Coverage evidence) — coaching delivered: plain-English on coverage %,
  day-to-day SD as a noise measure, and the ~4.5x noise reduction (12.81->2.86) with the
  mechanism (pooling cancels idiosyncratic noise, common signal survives = diversification
  of noise). Numbers: stock 80%/SD12.81, sector 99%/SD7.30, aggregate 100%/SD2.86.
  3 guiding questions for the [STUDENT TO WRITE]: coverage-up-and-noise-down trade-off;
  the KEY sector-not-aggregate point (cross-sectional tilt needs sectors to differ);
  the smoothing!=accuracy honest limit. Flagged verify-against-CSV + Word caption/scale.
  3 review checks flagged. Awaiting student.

- Section 3.5 (Week 9 index-construction material) — coaching delivered: walked the
  4-step pipeline in order — 0-100 rescale (compound+1)/2*100 (50=neutral); equal-ticker
  aggregate; z-standardisation + WHY (level above 50 on 98.3% of days, range 45.3-62.8, so
  level uninformative; z = distance from mean in SDs); expanding vs full-sample (look-ahead;
  corr ~0.998 = safe version nearly free); Z_BANDS + latest Extreme greed z~2.25. 3 guiding
  questions for the [STUDENT TO WRITE] "why expanding is mandatory" line (frame as real-time
  UNAVAILABILITY not inaccuracy; use 0.998 as costs-nothing; name the right defect). Flagged
  the "extreme greed relative to 2020-2023 window incl COVID/2022" caveat + verify-vs-CSV.
  Reminded attribution boundary (index=Week9, tilt=brief, deferred to 3.6). 3 review checks.

- Section 3.6 (Attribution note) — coaching delivered: purpose is academic-integrity
  precision (protects the 20% AI-logging/integrity + honest-attribution marks), 2-3 flat
  factual sentences not analysis. Drew the two-source distinction: index construction
  (rescale->aggregate->z->bands) = Week 9 lecture; fusion/tilt (move fund weights on lagged
  sector sentiment) = project brief, and Week 9 prescribes NO tilt. Guiding prompts to write
  one sentence per attribution + optional forward-pointer (index results §3.5, tilt §4.4).
  3 review checks: both present & not conflated; state Week9-defines-no-tilt; keep it a short
  factual note. Section 3 complete on the coaching side. Awaiting student.

## Section 4 (Extensions & innovations, 30% - highest weighted)

- Section 4.1 (Primary innovation: lexicon-mining pipeline) — coaching delivered:
  the 4-stage pipeline (mine ~2,154/452-article external corpus -> 10 independent-agent
  -4..+4 rating -> |mean|>=0.5 AND std<2.0 filter, noting the std gate rarely binds so the
  |mean| floor is the real constraint -> layer 123 words+204 idioms). Framed the innovation
  as the RULE-BASED 10-agent method vs subjective hand-picking. Corpus boundary disclosure
  (external = candidate discovery ONLY; all reported results run on provided
  news_headlines.parquet). Phrase-collapsing bug explained mechanically (VADER
  SPECIAL_CASE_IDIOMS 3 positional conditions -> headline-leading idioms never fire; fix =
  collapse idiom to one token, fires anywhere; worked ex "profit warning" +0.13->negative).
  Guiding questions for the [STUDENT TO WRITE] boundary sentence + framing (which innovation
  to lead with; how to show not assert the bug fix). 4 review checks flagged. Awaiting.

- Section 4.2 (Honest negative result: 204 vs 473 idioms) — coaching delivered: why this
  subsection is rubric-rewarded (careful extension that doesn't beat baseline still earns
  the band; integrity 20% + innovation 30%). Numbers: round1 204 -> fusion 0.587->0.602
  (+0.015); round2 +269 (=473) diluted to +0.005; reverted to 204, archived 473 (not
  deleted). Plain-English: dilution, frequency threshold (lowered to reach 473), boilerplate
  phrases (central bank/rate hike/cost cutting/biggest analyst calls, appendix). 4 guiding
  questions for the [STUDENT TO WRITE] "why dilution" mechanism (quality drops as threshold
  lowers; bad idiom adds noise on many headlines swamping signal; selectivity>breadth as a
  small sample-specific principle; frame revert+archive as disciplined experimentation).
  2 guardrails: +0.015/+0.005 both TINY (under-claim); sample-specific not a law. 4 checks.

- Section 4.3 (Second innovation: HRP) — coaching delivered: short subsection, one job =
  claim HRP as the distinct "newer method" innovation (vs lexicon = data/signal innovation),
  two separate innovation claims worth more than one. Cross-ref §1.2 for mechanics, don't
  re-derive. Recap draw-on facts: no covariance inversion (López de Prado 2016); synthetic
  0.901 vs 0.099; rank-corr 1.00 w/ RP but not identical; §2.2 lowest MaxDD every family.
  3 guiding questions for [STUDENT TO WRITE] one-liner (what HRP does instead of inverting =
  what failure mode it avoids; one concrete result proving it's not just a 5th line; keep the
  two innovations distinct). 2 guardrails: don't claim top Sharpe (Equity RP 0.724>HRP 0.674>
  MS 0.587) — anchor edge on drawdown/stability; don't re-derive the 3 steps. 4 checks.

- Section 4.4 (Fusion result nuance) — coaching delivered: where Section 3 sentiment meets
  Section 1 portfolio; hold BOTH sides of the trade. Numbers (Equity MS, fusion_comparison
  .csv): base ret 10.70%/Sharpe 0.587/MaxDD -26.07% -> +tilt ret 11.00%/Sharpe 0.602
  (+0.015)/MaxDD -26.66% (worse). Plain-English recap: tilt mechanism (lagged sector
  sentiment, cross-sectional median split toward high-sentiment sectors); Sharpe-up = better
  risk-adjusted; MaxDD-deeper = worse worst case (concentration into what's in favour). 4
  guiding questions for [STUDENT TO WRITE]: name the trade; why tilt deepens drawdown; small
  magnitude -> modest tilt not primary signal; sample-specific (one fund one period). 3
  guardrails: don't call +0.015 strong; don't hide the drawdown; don't generalise past the
  one fund tested. Section 4 complete on coaching side. 4 review checks. Awaiting student.

## Section 5 (App & investor journey, ~600 words)

- Section 5.1 (App structure) — coaching delivered: job is to present the 5 pages as a
  COHERENT investor journey, not a flat feature list. Pages: Compare Funds -> Fund Fact
  Sheet -> My Allocation -> Market Fear & Greed -> Sentiment Analytics; walked what each does
  for the user and the dependency chain (survey -> study -> commit -> sanity-check context ->
  deep-dive). Two things student writes: the journey narrative (what question each page
  leaves that the next answers) + a clause on the results-only architecture (reads precomputed
  results/ CSVs, no runtime recompute = deployable/fast/listed-mistake-avoided). Guardrails:
  don't just list pages; keep ~120-150 words; defer Plotly/gauge/colour to 5.2; no invented
  features. 4 review checks flagged. Awaiting student.

- Section 5.2 (Design system) — coaching delivered: targets the "original figure & design
  system" band; marker test = couldn't be produced by default widgets. Evidence to draw on:
  shared apply_theme() Plotly migration (consistent/interactive), custom go.Indicator fear-
  greed gauge, method->colour/family->line-style encoding (15 funds uniquely identifiable,
  fixed the 10-colour repeat bug from log 16), shared header/metric-card CSS + documented
  palette. Plain-English on why each beats default. 4 guiding questions for [STUDENT TO WRITE]
  2-3 lines: pick strongest 2-3 exhibits; pair each with the deficiency it fixes; frame
  encoding as information design (enables a task); restraint/subtraction (decluttering logs
  15-16). 3 guardrails: gauge = custom implementation not invented concept; concrete
  mechanisms not empty UX adjectives (watch banned words); keep ~150-200 words. 4 checks.

- Section 5.3 (Target user) — coaching delivered: binding constraint = MATCH Part A's value
  proposition (z5589978_projectA/report/report.pdf), don't reinvent; Part A wins over the
  outline's parenthetical, verify exact wording first (offered to read Part A and pull the
  value-prop wording without drafting). A target user answers: risk tolerance, capital/
  horizon, preference/style (systematic rules-based = the value prop). 4 guiding questions:
  derive user from the product menu not asserted; risk reality-check vs Crypto MS -89% MaxDD
  (can't be a capital-preservation persona); value prop in one line; consistency guard vs
  Part A. 3 guardrails: fidelity to Part A > "better" new persona; persona must fit actual
  fund risk; keep ~100-120 words concrete segment. Section 5 complete on coaching side. 4
  review checks. Awaiting student.

- Section 5.4 (Deployment constraint) — coaching delivered: state plainly the app only
  READS precomputed results/ CSVs, no runtime recompute/nltk/finvader (grep-verified logs
  04,13). Two architectures (recompute-live vs thin-reader); built the thin-reader on purpose
  for 3 reasons: free-tier feasibility (the listed common mistake), speed, reproducibility/
  separation of concerns. No [STUDENT TO WRITE] slot but still their prose: frame as strength
  not confession; lead with strongest reason (free-tier); include the "verified via grep"
  evidence clause. 3 guardrails: don't frame as weakness; don't duplicate 5.1 (5.1 flags,
  5.4 owns); 2-4 sentences. Noted 5.5 (Links) = URLs at hand-in only, repo private->public at
  submission, nothing to coach. Section 5 fully complete on coaching side. 4 review checks.

## Section 6 (Critical reflection: 3 recommendations, ~750 words)

- Section 6.1 (What worked / didn't / why) — coaching delivered: SYNTHESIS only, no new
  material/numbers; value is balanced judgement + causal "why". Pulled-forward material:
  worked = HRP lowest MaxDD every family (§2.2), Combined MS Sharpe 1.033/25.48% (§2.2),
  sentiment coverage +7.9pts (§3.2/§3.4); didn't = idiom dilution 204->473 +0.015->+0.005
  (§4.2), Crypto MS 0.224/-89.28% (§2.2), tilt return-vs-drawdown (§4.4). 4 guiding questions:
  name the connecting theme (stability/diversification worked vs concentrated return didn't);
  failure vs understood trade-off framing per item; attach a one-clause mechanism to each
  verdict; no-new-material discipline check. 4 guardrails: no new numbers; genuine balance;
  ~150-200 words synthesis not re-run; watch banned words. 4 review checks. Awaiting student.

- Section 6.2 (What the index can and cannot tell you, Week 9 slide 33) — coaching delivered:
  bound the index honestly in own words (NOT slide reworded). Can: pool noisy headlines into
  one signal (§3.4), flag relatively fearful/greedy days once standardised (§3.5). Cannot:
  judge truth or importance (scores tone not veracity/materiality), always get sign right
  (noisy proxy; own "profit warning" +0.13 wrong-sign case §4.1), standalone buy/sell rule
  (why §4.4 used a modest tilt). 4 guiding questions: ground each limit in OWN evidence not
  the slide; connect each "cannot" to a design choice already made (sector aggregation §3.4,
  modest tilt §4.4); tone-vs-truth-vs-importance in own example; avoid useless/predicts-prices
  extremes. 4 guardrails: genuinely own words; balance can/cannot; ground >=2 limits in own
  results; ~150 words watch banned words. 4 review checks. Awaiting student.

- Section 6.3 (Three recommendations) — coaching delivered: each must be claim -> evidence
  (a cited number) -> action. Rec1: match method to client type — HRP/RP for drawdown-averse
  (lowest MaxDD every family §2.2) vs Combined MS for return-chaser (25.48%/1.033 §2.2);
  name the trade-off; keep consistent w/ §5.3 persona. Rec2: sentiment as modest tilt not
  primary signal — evidence +0.015 & worse MaxDD (§4.4) + dilution 204->473 (§4.2); bridge
  from §6.2 "not standalone"; say what it constrains operationally. Rec3: replace rf=0 /
  zero-tx-cost — add real rf proxy + turnover/cost model (brief calls cost model an
  innovation); guiding on turnover x monthly-rebalance mechanism + DIRECTION rf/costs move
  Sharpe/returns + which funds hit hardest. 5 guardrails: cite a number each; actionable;
  consistent; no invented future numbers; ~250 words. Section 6 + all body sections complete
  on coaching side. 4 review checks per rec. Awaiting student.

*(update this list as we work through each subsection.)*
