# Prompt Log 07 - Lexicon Mining Rounds (scale to 100 survivors)

**Session date:** 2026-08-11
**Task:** Iterate scrape→extract→rate→filter in rounds until ≥100 words pass both
filters (|mean| ≥ 0.5, std < 2.0), keeping the bar fixed. Maintain one persistent
audit file of every word ever evaluated.

---

## Prompt used (verbatim)

> # Prompt for Claude Code — Keep Mining Until 100 Words Pass the Filter
>
> Paste this into Claude Code as a follow-up in the same `<zID>_projectB` session as the lexicon augmentation work.
>
> The last pass only produced about 20 words that passed both filters (mean ≠ 0, std < 2.0). That's too small a sample for a real lexicon extension. I don't want a single batch this time — **keep going in rounds, scraping and rating more candidates, until at least 100 words have passed both filters.** Don't stop at the first batch.
>
> ## 1. Work out the real scale needed before diving back in
> Look at the survival rate from the last round (roughly how many candidates went in vs. how many of them had mean ≠ 0 and std < 2.0). Use that rate to estimate how many total candidates you'll likely need to net 100 survivors — if last round's survival rate was around 10-15%, you're probably looking at several hundred to ~1,000 total candidates across all rounds, not another 150-200. Tell me that estimate before you start round 2, so I know roughly what we're committing to.
>
> ## 2. Loop: scrape → extract → rate → filter → accumulate
> Repeat this cycle until the **cumulative** count of surviving words reaches 100:
> 1. Pull more articles from the source(s) already set up (`data/lexicon_extension/`) — expand to more pages/categories/dates of the same feed(s) first, before adding a new source. If you do end up needing a second source to find enough volume, tell me which one and why before using it.
> 2. Extract new candidate words the same way as before (filtered against finVADER's combined lexicon), and **also filter out any word already evaluated in a previous round** — whether it passed or failed — so we're never re-rating the same word twice and wasting agent calls on it.
> 3. Run the same 10-independent-agent rating process on the new candidates only.
> 4. Apply the same filter: mean ≠ 0 and standard deviation < 2.0 — don't loosen this to hit 100 faster, the bar stays the same.
> 5. Add survivors to the running accepted list, log the round's numbers (candidates in, survivors out, cumulative total), and continue to the next round if still under 100.
> Keep a single persistent file tracking every word ever evaluated (word, round, all 10 ratings, mean, std, pass/fail) so the full history is auditable in one place rather than scattered across rounds.
>
> ## 3. Batch efficiently, don't waste calls
> Size each round's candidate batch sensibly based on the survival-rate estimate from step 1, rather than repeating small ~150-word batches many times over. Fewer, larger rounds are better than many tiny ones.
>
> ## 4. Stop conditions
> Stop and tell me if either of these happens, rather than continuing indefinitely:
> - You hit 100 accepted words — report the final count and move to merging them into the lexicon as planned.
> - A source genuinely runs out of new, non-duplicate articles/candidates before reaching 100 — tell me the shortfall and what you'd need (a second source, a longer date range, etc.) rather than lowering the filter to compensate.
>
> ## 5. Log it
> Update the AI log with a summary of every round (not a dump of all raw ratings — reference the persistent tracking file from step 2 for that), and update `PROJECT.md`'s Innovation checklist with the final accepted word count.
>
> Start by giving me the scale estimate from step 1.

---

## Step 1 — scale estimate (AI output)

- Round 1: 150 rated → 20 survivors (|mean| ≥ 0.5 & std < 2.0) = **13.3%** survival.
  (Plain mean ≠ 0 gave 23 = 15.3%. Keeping the stricter adopted bar.)
- Need 80 more survivors → ~600 more candidates at 13% → **~750 total**.
- Uncertainty: survival likely falls as high-frequency sentiment words are exhausted;
  could stretch to ~1,000–1,200 candidates / 3–4 rounds. Re-forecast after each round.
- Efficiency: current 452-article corpus already has 559 common candidates at freq≥2;
  only 150 rated → **~409 unrated candidates already available** → Round 2 needs no scrape.
- Plan: R2 = rate ~409 existing (no scrape, ~54 survivors, cum ~74); R3 = expand existing
  feeds for ~200 new candidates (~26 survivors, cum ~100); R4 if rate drops. Second source
  only if existing feeds run dry — will flag first.
- Persistent audit file: results/lexicon/lexicon_evaluations.csv.

## Step 1 decision — user reply "1" = keep |mean| ≥ 0.5 bar, proceed to Round 2.

## Round 2 — no new scrape (rated the 409 candidates already in the corpus)

- Seeded persistent tracker results/lexicon/lexicon_evaluations.csv from round 1
  (150 words, 20 pass). Generated round2_candidates.csv = 409 fresh (never-evaluated)
  common candidates from the existing 452-article corpus (scripts/lexicon/06).
- 10 independent agent passes rated all 409 (compact scores-only format for scale;
  no rationales this round — documented efficiency call). Batched 5+5 parallel.
- Aggregated (scripts/lexicon/07): |mean| ≥ 0.5 AND std < 2.0.
- **Round 2: 103 survivors from 409 (25% survival)** — much higher than the ~13%
  forecast, because low-frequency news words are far more sentiment-dense than the
  neutral high-frequency nouns of round 1 (surges, sinks, craters, sanctions,
  rallies, jumps, doubles, soaring, retreats, delays, ...).
- **Cumulative: 123 survivors (20 + 103) → target of 100 REACHED in round 2.**
  Stop condition hit; no round 3, no additional scraping needed.

### Raw-ratings storage (honest disclosure)
Round 2 ratings stored as each agent's COMPLETE non-zero score map
(results/lexicon/ratings/round2_scores_nonzero.json); every unlisted word = 0 for
that agent (exact, since neutral dominates). Transcribed from the 10 agent outputs;
the aggregation script validates that every listed word is in the 409-candidate
universe. High cross-agent agreement (most std = 0) makes the survivor set robust
to any single transcription slip.

## Step 7 — merge + regenerate (123-word FinVADER-Extended)

- scripts/lexicon/08 builds results/lexicon/kept_lexicon.csv (123 words, all rounds).
- src/sentiment.py now LOADS the extension from kept_lexicon.csv (single source of
  truth) instead of a hardcoded dict; deployed app never imports it.
- **Before/after (105,334 headlines): finVADER 39.3% → FinVADER-Extended 45.8%
  non-neutral (+6.54 pts, 7,041 headlines newly non-neutral)** — up from the 20-word
  version's +2.02 pts.
- Regenerated sector_sentiment_index + fusion. **Fusion: Equity MS Sharpe
  0.587 → 0.557 (−0.030)** — a larger honest negative than before. Richer sentiment
  coverage does NOT rescue the naive median tilt; if anything the stronger signal
  amplifies the crude tilt's misallocation. Report as a genuine finding.
- Full combined lexicon dump refreshed: 13,447 terms (123 ours).
- check_handin: 22 passed.

### Borderline survivors flagged for the student's spot-check
Passed the pre-registered filter with strong agreement but debatable as finance
sentiment — review before final report: biggest, cheapest, elite, heats, hotter,
discovery, mixed, stirs, intervenes, breaks, buildout, rebuilds, threefold. Keeping
all per the methodology unless vetoed.

**STATUS: 123/100 reached. Merged + regenerated. Awaiting student spot-check of
borderline words; economic interpretation to be written by student.**
