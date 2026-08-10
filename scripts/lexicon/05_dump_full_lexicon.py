"""FinVADER-Extended, step 5 — dump the full combined lexicon as one artifact.

The scorer assembles its lexicon in memory (VADER base + SentiBigNomics x0.1 +
Henry + our 20 words). This script writes the complete merged term list to a single
inspectable CSV for the report appendix, tagging each term's source and flagging
where a later layer overrode an earlier one.

Output (committable): results/lexicon/finvader_extended_full.csv
  columns: term, valence, source
  source in {vader_base, sentibignomics_x0.1, henry, finvader_extension}
"""
from __future__ import annotations

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PUB = ROOT / "results" / "lexicon"
PUB.mkdir(parents=True, exist_ok=True)


def main() -> None:
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from finvader.SentiBignomics import lexicon1
    from finvader.Henry import lexicon2
    from src.sentiment import FINVADER_EXTENSION

    # Build each layer in the same order the scorer applies them, tracking source.
    source: dict[str, str] = {}
    valence: dict[str, float] = {}

    for term, val in SentimentIntensityAnalyzer().lexicon.items():
        valence[term] = float(val); source[term] = "vader_base"
    for term, val in lexicon1().items():
        valence[term] = float(val) * 0.1; source[term] = "sentibignomics_x0.1"
    for term, val in lexicon2().items():
        valence[term] = float(val); source[term] = "henry"
    for term, val in FINVADER_EXTENSION.items():
        valence[term] = float(val); source[term] = "finvader_extension"

    df = (pd.DataFrame({"term": list(valence),
                        "valence": [round(valence[t], 4) for t in valence],
                        "source": [source[t] for t in valence]})
            .sort_values(["source", "term"])
            .reset_index(drop=True))
    df.to_csv(PUB / "finvader_extended_full.csv", index=False)

    print("=== FinVADER-Extended: full combined lexicon ===")
    counts = df["source"].value_counts()
    for src in ["vader_base", "sentibignomics_x0.1", "henry", "finvader_extension"]:
        print(f"  {src:<22} {counts.get(src, 0):>6} terms (final owner after overrides)")
    print(f"  {'TOTAL':<22} {len(df):>6} terms")
    print(f"\n  saved results/lexicon/finvader_extended_full.csv")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    main()
