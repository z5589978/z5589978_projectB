"""FinVADER-Extended idioms — extract candidate phrases (bigrams + trigrams).

From the idiom corpus (title + lead), build content-word bigrams and trigrams,
drop proper-noun phrases and stopword-only phrases, exclude anything already
evaluated in a previous idiom round or already in VADER's SPECIAL_CASE_IDIOMS,
rank by frequency, and write the next round's candidate list.

Phrases (2-3 words) are what VADER's idiom mechanism (SPECIAL_CASE_IDIOMS) can
actually fire on -- single-word lexicon entries cannot capture "profit warning"
(scored +0.13 by finVADER, i.e. backwards).

Usage: python scripts/lexicon/11_extract_idioms.py [round_no]
Output: results/lexicon/idiom_round{N}_candidates.csv  (phrase, frequency)
"""
from __future__ import annotations

import pathlib
import re
import sys
from collections import Counter

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
RAW = ROOT / "data" / "lexicon_extension"
PUB = ROOT / "results" / "lexicon"
TRACKER = PUB / "idiom_evaluations.csv"

MIN_FREQ = 2
CAP = 500
CAP_SHARE_MAX = 0.6

from _lexicon_common import stopwords, cap_share


def main(round_no: int | None = None) -> None:
    raw_text = (RAW / "corpus_text_idioms.txt").read_text(encoding="utf-8", errors="ignore")
    stops = stopwords()
    caps = cap_share(raw_text)

    def content(tok: str) -> bool:
        return len(tok) >= 3 and tok not in stops and caps.get(tok, 0.0) < CAP_SHARE_MAX

    def proper(tok: str) -> bool:
        return caps.get(tok, 0.0) >= CAP_SHARE_MAX

    bi, tri = Counter(), Counter()
    for line in raw_text.lower().splitlines():
        toks = re.findall(r"[a-z]+", line)
        for i in range(len(toks) - 1):
            a, b = toks[i], toks[i + 1]
            if content(a) and content(b):
                bi[f"{a} {b}"] += 1
        for i in range(len(toks) - 2):
            a, m, b = toks[i], toks[i + 1], toks[i + 2]
            if content(a) and content(b) and not proper(m):
                tri[f"{a} {m} {b}"] += 1

    # existing SPECIAL_CASE_IDIOMS + already-evaluated
    from nltk.sentiment.vader import VaderConstants
    existing = set(VaderConstants().SPECIAL_CASE_IDIOMS)
    if TRACKER.exists():
        tr = pd.read_csv(TRACKER)
        existing |= set(tr["phrase"])
        round_no = round_no or int(tr["round"].max()) + 1
    else:
        round_no = round_no or 1

    ranked = [(p, c) for p, c in (bi + tri).most_common()
              if c >= MIN_FREQ and p not in existing]
    batch = ranked[:CAP]
    out = pd.DataFrame(batch, columns=["phrase", "frequency"])
    out_path = PUB / f"idiom_round{round_no}_candidates.csv"
    out.to_csv(out_path, index=False)

    print(f"=== idiom extraction (round {round_no}) ===")
    print(f"  content bigrams: {len(bi)}  trigrams: {len(tri)}")
    print(f"  candidates at freq>={MIN_FREQ}, not already evaluated: {len(ranked)}")
    print(f"  this round batch (cap {CAP}): {len(batch)}")
    if batch:
        print(f"  frequency range: {batch[-1][1]}-{batch[0][1]}")
        print("  top 30:")
        for p, c in batch[:30]:
            print(f"    {p:<28} {c}")
    print(f"\n  saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
