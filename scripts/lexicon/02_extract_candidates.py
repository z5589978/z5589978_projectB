"""FinVADER-Extended, step 2 — extract candidate words.

From the scraped corpus (title + lead), tokenize, lowercase, strip
punctuation/numbers/stopwords, and drop any word already scored by finVADER's
combined lexicon (VADER base + SentiBigNomics + Henry). The point is to surface
genuine gaps — finance vocabulary finVADER does not already cover — not to
rediscover words it can already score.

Ranks the remainder by corpus frequency and writes a candidate list for the
10-agent rating step. Output (committable — derived counts, no raw article text):
  data/lexicon_extension/candidate_words.csv   (word, frequency)
"""
from __future__ import annotations

import re
import pathlib
from collections import Counter

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
RAW = ROOT / "data" / "lexicon_extension"          # gitignored raw corpus
PUB = ROOT / "results" / "lexicon"                 # committed derived artifacts
PUB.mkdir(parents=True, exist_ok=True)

CAP = 150            # max candidates to hand to the raters
MIN_FREQ = 2         # a candidate must appear at least twice
MIN_LEN = 3          # drop 1-2 letter tokens
CAP_SHARE_MAX = 0.6  # drop likely proper nouns: capitalised in >=60% of
                     # mid-sentence occurrences (entities are not lexicon material)


def cap_share(raw_text: str) -> dict[str, float]:
    """Share of mid-sentence occurrences where a token is Capitalised.

    Sentence-initial words are skipped (capitalisation there is uninformative).
    A high share flags a proper noun / entity (Trump, SpaceX, Reuters).
    """
    from collections import Counter
    toks = re.findall(r"\S+", raw_text)
    cap, low = Counter(), Counter()
    for i, tok in enumerate(toks):
        w = re.sub(r"[^A-Za-z]", "", tok)
        if not w:
            continue
        prev_end = toks[i - 1][-1] if i > 0 else "."
        if i == 0 or prev_end in ".!?":      # sentence-initial: skip
            continue
        (cap if w[0].isupper() else low)[w.lower()] += 1
    return {w: cap[w] / (cap[w] + low[w]) for w in (set(cap) | set(low))
            if (cap[w] + low[w]) > 0}


def finvader_lexicon_keys() -> set[str]:
    """The combined finVADER lexicon (lowercased single-token keys)."""
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from finvader.SentiBignomics import lexicon1
    from finvader.Henry import lexicon2
    sia = SentimentIntensityAnalyzer()
    sia.lexicon.update({t: v * 0.1 for t, v in lexicon1().items()})
    sia.lexicon.update(lexicon2())
    keys = set()
    for k in sia.lexicon:
        keys.add(str(k).lower())
        for tok in str(k).lower().split():   # also index multi-word-phrase tokens
            keys.add(tok)
    return keys


def stopwords() -> set[str]:
    import nltk
    try:
        from nltk.corpus import stopwords as sw
        base = set(sw.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords as sw
        base = set(sw.words("english"))
    # News/web + publisher junk that is not sentiment-bearing.
    junk = {
        "reuters", "cnbc", "marketwatch", "said", "says", "say", "also", "new",
        "one", "two", "us", "u", "s", "inc", "corp", "co", "ltd", "amp", "com",
        "www", "http", "https", "read", "more", "year", "years", "week", "day",
        "month", "quarter", "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday", "january", "february", "march", "april",
        "june", "july", "august", "september", "october", "november", "december",
        "could", "would", "may", "might", "since", "amid", "per", "vs",
    }
    return base | junk


def main() -> None:
    corpus_path = RAW / "corpus_text.txt"
    if not corpus_path.exists():
        raise SystemExit("Run scripts/lexicon/01_scrape_corpus.py first.")
    raw_text = corpus_path.read_text(encoding="utf-8", errors="ignore")
    text = raw_text.lower()

    tokens = re.findall(r"[a-z]+", text)
    total_tokens = len(tokens)

    stops = stopwords()
    lex = finvader_lexicon_keys()
    caps = cap_share(raw_text)

    kept = [t for t in tokens if len(t) >= MIN_LEN and t not in stops and t not in lex]
    freq = Counter(kept)

    # Candidates at freq >= MIN_FREQ, ranked by frequency
    ranked = [(w, c) for w, c in freq.most_common() if c >= MIN_FREQ]
    # Drop likely proper nouns, then refill from the pool up to CAP
    proper = [w for w, _ in ranked if caps.get(w, 0.0) >= CAP_SHARE_MAX]
    common = [(w, c) for w, c in ranked if caps.get(w, 0.0) < CAP_SHARE_MAX]
    candidates = common[:CAP]

    df = pd.DataFrame(
        [(w, c, round(caps.get(w, 0.0), 2)) for w, c in candidates],
        columns=["word", "frequency", "cap_share"],
    )
    df.to_csv(PUB / "candidate_words.csv", index=False)

    print("=== FinVADER-Extended step 2: extract candidates ===")
    print(f"  corpus tokens (raw):            {total_tokens:,}")
    print(f"  unique tokens:                  {len(freq):,}")
    print(f"  finVADER lexicon keys filtered: {len(lex):,}")
    print(f"  candidates at freq >= {MIN_FREQ}:        {len(ranked)}")
    print(f"  dropped as proper nouns:        {len(proper)}")
    print(f"  common-word candidates:         {len(common)}")
    print(f"  candidates kept (cap {CAP}):      {len(candidates)}")
    print(f"\n  frequency range: {candidates[-1][1]}–{candidates[0][1]}")
    print("\n  top 40 candidates:")
    for w, c in candidates[:40]:
        print(f"    {w:<18} {c}")
    print(f"\n  saved results/lexicon/candidate_words.csv ({len(df)} words)")


if __name__ == "__main__":
    main()
