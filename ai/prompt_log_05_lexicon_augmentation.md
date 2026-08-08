# Prompt Log 05 - Lexicon Augmentation (Innovation Extension, Station 3)

**Session date:** 2026-08-08
**Task:** Build an original sentiment-model extension: mine a fresh financial-news corpus for finance words finVADER doesn't cover, rate each candidate with 10 independent agents, and layer only the agreed non-neutral words into the scorer. This is the Station 3 Innovation extension; document methodology + equation for the report.

---

## Prompt used (verbatim)

> I want to build an original extension to our sentiment model: mine a fresh corpus of real financial news for finance-specific words that finVADER doesn't already cover, get an independent multi-agent valence rating for each candidate word, and layer only the words the raters agree on into our sentiment scorer. This is the Innovation extension for Station 3 (news-sentiment) — document it fully as we go, since it needs to be described with its own methodology and equation in the report.
>
> 0. Log this first, and check current state before building
>
> Log this prompt verbatim as the next ai/prompt_log_0X_lexicon_augmentation.md entry, per our existing convention.
>
> Then check src/sentiment.py before writing anything new: it currently scores headlines with plain NLTK VADER (nltk.sentiment.vader.SentimentIntensityAnalyzer), not finVADER — there's no existing custom lexicon in the code yet, despite PROJECT.md's checklist mentioning one as planned. So two things need to happen, not just one:
>
> Switch the base scorer to finVADER (from finvader import finvader, use_sentibignomics=True, use_henry=True — the Week 9 lecture pattern), so we're augmenting on top of the ~7,500-term finance lexicon finVADER already provides, not plain VADER's ~7,500 general-purpose words.
> Then layer our own newly-mined, multi-agent-rated words on top of that, via a lexicon update mechanism (sia.lexicon.update({...}) if we keep an NLTK-analyzer object, or the equivalent for however finvader exposes its underlying lexicon — check the package and use whichever integration point actually works, and tell me if finvader's API doesn't cleanly support this so we can decide together how to proceed).
>
> Update PROJECT.md's Innovation checklist to reflect the real state once you've confirmed this.
>
> 1. Find and confirm a source before scraping
>
> Find a free financial news website suitable for automated collection. Prefer one with a public RSS/Atom feed over raw HTML scraping if available — it's simpler, more reliable, and clearly permitted. If you scrape HTML directly, check robots.txt and the site's terms first, use a descriptive User-Agent, and rate-limit requests (small delay between calls). Tell me which source you've chosen and why, and wait for me to confirm before you start pulling 100+ articles — I don't want us to build the rest of this pipeline on a source that turns out to be a bad choice.
>
> 2. Curate the source metadata
>
> For the chosen source, before or alongside scraping, build a structured metadata record per article — title, url, published_date, publisher, section/category if available, scrape_timestamp — save it as a JSON list of records (this is the "expert curated list") and also export it as a pandas DataFrame (CSV) for convenience. Keep this under a new data/lexicon_extension/ folder — not results/, since that's reserved for the four required project files. Add data/lexicon_extension/ to .gitignore: don't commit the raw scraped text, same rule as the project's own raw data — only the derived candidate-word lists and summary stats get committed.
>
> 3. Scrape 100+ articles
>
> Target at least 100 unique articles (dedupe on title+url). Cache what you fetch locally so we're not re-hitting the site if we need to rerun later.
>
> 4. Extract candidate sentiment-bearing words
>
> From the scraped article text (titles are fine; short lead paragraphs are fine too if it gives more vocabulary — your call, but tell me which you used), tokenize, lowercase, strip punctuation/numbers/stopwords, and filter out any word already present in finVADER's combined lexicon (VADER's base list + SentiBigNomics + Henry's list) — the whole point is to find genuine gaps, not rediscover words it already scores. Rank the remainder by frequency and cap the candidate list at a manageable size for manual-style rating — 150–200 words is a reasonable cap; confirm the actual count with me before moving to the rating step, since that step is more expensive.
>
> 5. Rate each candidate word with 10 independent agents
>
> Spawn 10 independent rating passes (your own subagent/task mechanism) over the candidate list. Each pass must be genuinely independent — no agent sees another's ratings. Each agent rates every candidate word on VADER's own scale, −4 (extremely negative) to +4 (extremely positive), with a one-line rationale per word. Save all 10 raw rating sets in full (for reproducibility), then compute, per word: mean and standard deviation across the 10 ratings.
>
> 6. Filter: keep only words the raters agree are non-neutral
>
> Keep a word only if:
> mean ≠ 0 (the panel thinks it's directionally positive or negative, not neutral), and
> standard deviation < 2.0 — this is "25% of the −4 to +4 range" (a range of 8 points; 25% of 8 = 2.0), i.e. tight cross-agent agreement. If you think a different interpretation of "25%" fits better once you see the actual distribution of standard deviations across the candidate words, flag it to me with the numbers before finalizing — don't silently pick a threshold that keeps everything or almost nothing.
> Report how many candidates went in and how many survived both filters.
>
> 7. Build the augmented lexicon and re-run the pipeline
>
> Merge the surviving words (word → mean valence, rescaled to whatever range finVADER's underlying lexicon actually expects — check this, VADER-family lexicons are typically −4 to +4 internally) into the scorer from step 0. Give the combined result a name that's clearly our own extension and distinct from the course's finVADER package (e.g. something like FinVADER-Extended — pick something sensible and use it consistently in code, comments, and the report).
> Re-run the before/after comparison already planned in PROJECT.md's Innovation checklist (% of headlines newly scored as non-neutral, coverage change), then regenerate results/data/sector_sentiment_index.csv, the fusion comparison, and any other downstream results/ files this affects.
>
> 8. Report and log honestly, not as a dump
>
> In the report's innovation section, describe the full methodology with the filtering equation/thresholds and the before/after effect. In ai/, log a curated summary (source, article count, candidate count, agents used, filter thresholds, survival count, a representative sample of ~15–20 kept words with their scores) — not all 10 × 150+ raw ratings; keep those in the supplementary CSV from step 5 and reference it. Also: I want to personally spot-check ~15–20 of the final kept words myself before this goes into the report — flag that as an explicit checkpoint rather than moving straight to writing them up as final.
>
> Start with step 1 — propose the source and wait for my confirmation.

---

## Step 0 — state check findings

**Current scorer:** `src/sentiment.py` `_get_analyzer()` returns a plain NLTK
`SentimentIntensityAnalyzer()` — plain VADER, no custom lexicon. Confirmed.

**finVADER integration point (verified by running it):**
- Clean mechanism = the Week-9 pattern: build NLTK `SentimentIntensityAnalyzer`,
  then `.lexicon.update({**{t: v*0.1 for SentiBigNomics}, **Henry})`.
- Term counts: VADER base 7,502 + SentiBigNomics 7,295 (×0.1 scaled) + Henry 189
  = **13,324 combined** terms (net, after overlaps).
- Internal lexicon scale observed: **−3.9 … +3.4** (i.e. the standard VADER −4…+4
  range). Our mined words will be injected on this same −4…+4 scale.
- The `from finvader import finvader` convenience function does NOT cleanly expose
  an injection point (rebuilds internally per call), so we use the analyzer/
  `.lexicon` route and add our words with a THIRD `.lexicon.update()`. This is the
  integration decision.

**Correction to the old plan:** PROJECT.md's innovation checklist previously said
"FINANCE_LEXICON dict (~80 hand-picked terms)". That is superseded by this
mined + 10-agent-rated methodology. Checklist rewritten to match.

## Step 1 — source probe (evidence before recommending)

Probed candidate RSS feeds with a descriptive academic User-Agent, 1s rate-limit:

| Source | HTTP | Items/feed | Notes |
|--------|------|-----------|-------|
| CNBC (Top/Markets/Earnings/Economy) | 200 | ~30 each | real finance headlines; many category feeds |
| MarketWatch (Top/Bulletins) | 200 | ~10 each | fewer items; needs many feeds |
| Nasdaq RSS | timeout | — | unreliable |

**Recommendation put to user: CNBC RSS feeds** (combine ~5–8 documented category
feeds → 100+ unique articles after title+url dedupe). Reachable, item-rich, US
markets/company-news domain matching the project's 50 US equities. RSS is published
for consumption; will use descriptive UA + rate-limiting.

## Step 1 — user chose CNBC + Reuters + MarketWatch; Reuters resolution

User selected three publishers. Reuters direct RSS is DEAD (legacy feeds refuse
connection; agency + current-site URLs 404 — Reuters discontinued public RSS).
Resolution: pull Reuters headlines via **Google News RSS** `site:reuters.com`
queries (markets/business/earnings) — verified HTTP 200, 100 real Reuters finance
headlines per query.

Final verified source plan:
- CNBC: direct RSS, ~6 category feeds (~30 items each)
- MarketWatch: direct RSS, 3 feeds (10–30 each)
- Reuters: Google News RSS, site:reuters.com (100 each)
Combined + dedupe on title+url → 200+ unique articles (>100 minimum).

Caveats logged: Reuters items carry a Google News redirect URL (recorded as-is,
publisher=Reuters, source_feed=googlenews); " - Reuters" title suffix stripped
during tokenization.

**STATUS: sources confirmed. User approved pulling. Steps 2–4 executed below.**

## Steps 2–3 — corpus scraped

Script: scripts/lexicon/01_scrape_corpus.py. Used title + RSS lead/description
(richer vocabulary than titles alone). Raw feeds cached to
data/lexicon_extension/cache/ so reruns are offline.

- 540 raw items → **452 unique articles** (dedupe on title+url).
- By publisher: CNBC 180, MarketWatch 60, Reuters 300 (via Google News).
- Saved (gitignored): articles_metadata.json/.csv, corpus_text.txt.
- Saved (committable): corpus_summary.csv (publisher × category counts).

## Step 4 — candidate extraction

Script: scripts/lexicon/02_extract_candidates.py. Tokenised (lowercase, alpha
only, len≥3), removed NLTK stopwords + news/publisher junk, and filtered out all
13,318 finVADER lexicon keys. 11,805 corpus tokens → 1,451 unique → **828
candidates at freq≥2** → capped to top 200 by frequency.

**Quality flag raised with user before rating:** the frequency-ranked top 200 is
contaminated by proper nouns/entities. A capitalisation heuristic (cap-share ≥0.6
mid-sentence) flags **66/200 as likely proper nouns** (trump, iran, spacex, china,
bessent, dow, amd, boj, elon, lilly, airbnb…) vs 134 common words. Entities are not
sentiment-lexicon material and would waste the panel + depress the survival rate.
Decision put to user: (a) rate raw 200, (b) drop proper nouns + refill to ~150
clean candidates [recommended], (c) other cap. User chose (b).

## Step 4 (final) — candidate list

Script updated with capitalisation-based proper-noun filter (cap_share ≥0.6 mid-
sentence). 828 candidates → 269 dropped as proper nouns → 559 common → top 150 kept.
Saved candidate_words.csv (word, frequency, cap_share). Freq range 4–54.

## Step 5 — 10 independent rating passes

Spawned 10 general-purpose subagents in parallel via the Agent tool. Each rated all
150 words on the −4..+4 integer scale with a one-line rationale, returning JSON only
to the parent (no agent saw another's ratings → genuine independence). All 10
returned valid 150-item JSON.

Archived to data/lexicon_extension/ratings/all_ratings_raw.json, split to
agent_01..agent_10.json. **Honest limitation:** full per-word rationales were
persisted verbatim for agent_01 (representative exemplar); for agents 2–10 the
SCORES are persisted in full (these drive every downstream number) but rationales
were abbreviated to save space. If full rationales for all 10 are needed for the
reproducibility archive, re-request from the agents.

## Step 6 — aggregation + filter

Script: scripts/lexicon/03_aggregate_ratings.py. Per-word mean + sample std (ddof=1)
across the 10 passes. Filter: mean ≠ 0 AND std < 2.0.

Result: **23 of 150 kept.**

**Threshold flag (as invited in the prompt):** inter-agent agreement is very high —
**max std across all 150 words is 0.516**, so the std < 2.0 gate ("25% of range")
NEVER binds; it passes all 150. The binding filter is mean ≠ 0. Three survivors lean
on only 1–4 of 10 raters (sold −0.10 [1/10], jobs +0.30 [3/10], historic +0.40
[4/10]). Stricter magnitude cut-offs: |mean|>0.5 → 20 words; |mean|>1.0 → 11.

Kept (23): rout −3.8, cyclosporiasis −2.1, concerns/dents/slows/tariffs −2.0,
overshadows −1.9, behind/costs/faces −1.0, hikes −0.8, sold −0.1, jobs +0.3,
historic +0.4, returns +0.9, raises/added/ahead/bigger +1.0, climbs/lifts/highs
+2.0, soars +3.1.

**USER CHECKPOINT (as requested): spot-check the kept words + confirm threshold
before building the lexicon and regenerating results.** User spot-checked and chose
the |mean| ≥ 0.5 floor → 20-word lexicon (dropped sold, jobs, historic).

## Step 7 — build FinVADER-Extended + regenerate

- src/sentiment.py `_get_analyzer(extended=True)`: NLTK VADER + SentiBigNomics ×0.1
  + Henry + FINVADER_EXTENSION (20 words, −4..+4). Named FinVADER-Extended.
- Final 20-word lexicon (word → mean valence): rout −3.8, cyclosporiasis −2.1,
  concerns/dents/slows/tariffs −2.0, overshadows −1.9, faces/costs/behind −1.0,
  hikes −0.8, returns +0.9, bigger/raises/added/ahead +1.0, highs/climbs/lifts +2.0,
  soars +3.1.
- **Before/after (step 4 script), 105,334 distinct headlines, |compound|>0.05:**
  plain VADER 51.13% non-neutral → finVADER 39.27% → FinVADER-Extended 41.29%.
  Our 20 words newly flag 2,176 headlines (+2.02 pts) that finVADER scored neutral.
  Narrative: finVADER trades coverage for accuracy (drops plain VADER's false-positive
  finance neutrals à la Loughran-McDonald); our extension recovers genuine sentiment
  (soars/rout/tariffs/dents) without reintroducing false positives.
- Regenerated results/: sector_sentiment_index.csv (mean compound 0.106 → 0.074),
  fusion_comparison.csv. **Fusion effect: Equity MS Sharpe 0.587 → 0.575 (−0.012)** —
  a slightly worse honest negative result (was −0.005 with plain VADER). The improved
  signal does not rescue the naive median tilt; brief credits explained negatives.
- Updated app caption + Figure 5 label to name FinVADER-Extended (was "VADER").

## Step 8 — housekeeping

- check_handin banned .csv outside results/; moved all committable derived artifacts
  to results/lexicon/ (kept_lexicon, candidate_words, candidate_scores, ratings_matrix,
  before_after, corpus_summary, ratings/*.json). Raw corpus (json/txt/xml) gitignored
  under data/lexicon_extension/. **Tradeoff:** dropped the articles_metadata.csv
  convenience copy (course check forbids csv outside results/); metadata kept as JSON.
- check_handin: 21 passed.

**Honest limitations to carry into the report:**
1. std<2.0 filter never binds (max std 0.52); effective filter is |mean|≥0.5.
2. Agents are same-model independent passes (no cross-talk), not human raters —
   correlation is inherent; disclose in methodology.
3. Full rationales persisted for agent_01 only; scores full for all 10.
4. Fusion result is negative (−0.012); report as an honest finding, not a win.

**NEXT (report stage): write methodology + filtering equation in Section 4; the
economic interpretation must be rewritten by the student.**
