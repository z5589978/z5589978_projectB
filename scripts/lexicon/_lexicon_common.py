"""Shared helpers for the FinVADER-Extended lexicon-mining rounds.

Used by the candidate-extraction and round scripts so the filtering rules
(finVADER lexicon exclusion, stopwords, proper-noun detection) are defined once.
"""
from __future__ import annotations

import re
from collections import Counter


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
        for tok in str(k).lower().split():
            keys.add(tok)
    return keys


def stopwords() -> set[str]:
    """NLTK English stopwords plus news/web/publisher junk."""
    import nltk
    try:
        from nltk.corpus import stopwords as sw
        base = set(sw.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords as sw
        base = set(sw.words("english"))
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


def cap_share(raw_text: str) -> dict[str, float]:
    """Share of mid-sentence occurrences where a token is Capitalised.

    Sentence-initial words are skipped. High share flags a proper noun / entity.
    """
    toks = re.findall(r"\S+", raw_text)
    cap, low = Counter(), Counter()
    for i, tok in enumerate(toks):
        w = re.sub(r"[^A-Za-z]", "", tok)
        if not w:
            continue
        prev_end = toks[i - 1][-1] if i > 0 else "."
        if i == 0 or prev_end in ".!?":
            continue
        (cap if w[0].isupper() else low)[w.lower()] += 1
    return {w: cap[w] / (cap[w] + low[w]) for w in (set(cap) | set(low))
            if (cap[w] + low[w]) > 0}


def common_candidates(raw_text: str, min_freq: int = 2, min_len: int = 3,
                      cap_share_max: float = 0.6) -> list[tuple[str, int]]:
    """Full ranked list of common-word candidates not in finVADER's lexicon.

    Returns [(word, frequency), ...] descending, proper nouns and finVADER terms
    removed. No cap — callers slice / exclude already-evaluated words themselves.
    """
    text = raw_text.lower()
    tokens = re.findall(r"[a-z]+", text)
    stops = stopwords()
    lex = finvader_lexicon_keys()
    caps = cap_share(raw_text)
    kept = [t for t in tokens if len(t) >= min_len and t not in stops and t not in lex]
    freq = Counter(kept)
    ranked = [(w, c) for w, c in freq.most_common() if c >= min_freq]
    return [(w, c) for w, c in ranked if caps.get(w, 0.0) < cap_share_max]
