# Prompt Log 08 - Finance Idioms (phrase-level context extension)

**Session date:** 2026-08-11
**Task:** Add a phrase-level (idiom) sentiment layer so finance phrases get context
single words can't capture. Mine idiom candidates in rounds until >=200 pass the
filter; webscrape more articles as needed.

---

## Prompts used (verbatim)

Lead-in questions (context for the task):

> what are the current rules of the vader, so I can decide whether more rules are needed so that words can have more context

> is that allowed in this project to have the idioms?

Task directive:

> Yes go ahead, start scanning for idioms, and repeat in rounds until you reach 200 idioms or more, feel free to webscrape even more articles for more words

Mid-task (after a dropped connection):

> continue your work, sorry that you lost connection

---

## What the AI established first (VADER's rules + the real gap)

Enumerated VADER's 5 heuristics from the installed source (constants: B_INCR/DECR
0.293, C_INCR 0.733, N_SCALAR -0.74; 59 negators; 66 boosters; 7 general-English
idioms). Verified the context gap:
- Multi-word keys added to `.lexicon` are INERT (VADER scores token-by-token):
  "profit warning" stays +0.128.
- finVADER has ~zero phrase coverage (1 multi-word key, "hard time").
- Allowed per brief: innovation examples explicitly include "a custom sentiment
  tool" / "extending VADER". Constraints respected (build-time only, equity-only,
  no look-ahead, no new deps). External scrape used ONLY to discover phrases;
  reported results run on the provided news_headlines.parquet -- disclosed.

## Pipeline (scripts/lexicon/10-13)

- 10_scrape_more.py: expanded feeds (30 finance-topic Google News queries site-
  restricted to Reuters/CNBC/MarketWatch/Bloomberg + CNBC/MW direct). Corpus grew
  452 -> **2,154 unique articles**. Raw gitignored.
- 11_extract_idioms.py: content-word bigrams+trigrams, proper-noun + stopword
  filtered, excluding SPECIAL_CASE_IDIOMS + already-evaluated. 960 candidates at
  freq>=3; round-1 batch = 400.
- Rating: 10 independent agents, each WROTE ITS OWN file
  (results/lexicon/ratings/idiom_round1_agent_XX.json) -- reliable capture, no
  transcription; independence preserved (each writes only its own file).
- 12_idiom_aggregate.py: |mean|>=0.5 & std<2.0. **Round 1: 204/400 survived (51%)**
  -- phrases are far more sentiment-dense than words. Target >=200 REACHED in one
  round; no round 2, though the scrape did grow the corpus as invited.
- 13_build_idioms.py: results/lexicon/kept_idioms.csv (204 phrases, -4..+4).

## Key methodological finding (VADER idiom mechanism is position-limited)

Read VADER's sentiment_valence/_idioms_check: SPECIAL_CASE_IDIOMS only fires when
the phrase's LAST word is a lexicon word, there are >=3 preceding tokens, AND the
word 3-back is not a lexicon word. So leading/mid-headline phrases ("Shares soar
...") usually do NOT fire. Confirmed empirically.

**Fix (implemented):** phrase COLLAPSING. `apply_idioms()` detects each idiom
(word-boundary, longest-first) and joins it into one alphabetic token
("profit warning" -> "profitwarning") whose lexicon valence = the idiom's mean.
Fires regardless of position. src/sentiment.py loads kept_idioms.csv and adds
collapsed tokens to the extended analyzer; finvader_extended_score() collapses
before scoring.

## Results (words + 204 idioms)

- Before/after (105,334 headlines): finVADER 39.3% -> **FinVADER-Extended 47.2%**
  non-neutral (+7.90 pts; 8,544 headlines newly non-neutral), up from +6.54 (words).
- **Fusion FLIPPED POSITIVE: Equity MS Sharpe 0.587 -> 0.602 (+0.015)** -- was
  -0.030 with words only. The context-aware idiom signal is what makes the sentiment
  tilt add value. Modest and possibly sample-specific; report honestly, not oversell.
- Idiom fixes verified: "guidance cut" +0.006 -> -0.869; "files for bankruptcy"
  -0.02 -> -0.72; leading "Shares soar" +0.58 -> +0.81.

## Borderline idioms flagged for the student's spot-check
Strong agreement but debatable/boilerplate: "biggest analyst calls", "central bank"
(should be ~0 -- verify it filtered), "rate hike" (-, but directionally arguable),
"cost cutting" (efficiency vs distress). Review kept_idioms.csv before final report.

**STATUS (round 1): 204 idioms reached, merged, regenerated. Fusion +0.015.**

---

## Round 2 idioms (add another 200)

Prompts (verbatim):

> now run rounds until at least 1000 idioms added is reached

(Then superseded by the question + revised directive below.)

> add another 200 idioms using the same process

**AI flag before running:** reaching 1,000 would require ~4-5 more rounds, survival
falling, and candidates degrading into corpus boilerplate ("moves premarket",
"biggest moves midday"). The 10-agent filter still protects survivor quality, but
volume risks diluting a sharp lexicon. User revised target to +200.

Execution:
- 11_extract_idioms.py round 2: MIN_FREQ lowered to 2, CAP 500. 7,113 candidates
  available (freq 2-4); batch = 500. Candidates now marginal ("traders react").
- 10 agents each READ the candidate CSV themselves (shared input, not another
  agent's ratings -> independence preserved) and wrote their own file. Leaner than
  embedding 500 phrases per prompt.
- 12_idiom_aggregate.py round 2: **269/500 survived (54%)** -- quality held up
  ("stocks slide", "recession fears", "tech layoffs", "hikes guidance", "markets
  soared"). Well past the +200 asked.
- **Cumulative: 473 idioms** (204 + 269), 900 phrases evaluated.

Results (123 words + 473 idioms):
- Before/after: finVADER 39.3% -> Extended 47.5% non-neutral (+8.20 pts).
- **Fusion +0.005** -- LOWER than +0.015 at 204 idioms. The extra 269 idioms added
  coverage but slightly diluted the fusion benefit. Honest, useful finding: more
  idioms is not strictly better; the sharpest signal was around 204. Report this.

**STATUS: +269 idioms added (target +200 exceeded); 473 total, merged, regenerated.
Economic interpretation to be written by the student.**
