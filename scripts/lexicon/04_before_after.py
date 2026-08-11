"""FinVADER-Extended, step 4 — before/after effect on the project headlines.

Scores every distinct project headline under three models and reports how many
are non-neutral (|compound| > 0.05, VADER's standard neutral band):
  1. plain VADER            (general-purpose lexicon)
  2. finVADER               (+ SentiBigNomics + Henry)
  3. FinVADER-Extended      (+ our 20 mined, panel-rated words)

The marginal column isolates OUR contribution: headlines that finVADER scored
neutral but FinVADER-Extended scores non-neutral.

Output (committable): data/lexicon_extension/before_after.csv
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.etl import load_clean_news
from src.sentiment import _get_analyzer, apply_idioms

NEUTRAL_BAND = 0.05


def plain_vader():
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    return SentimentIntensityAnalyzer()


def main() -> None:
    news, _ = load_clean_news()
    titles = pd.Series(news["title"].dropna().unique(), name="title")
    print(f"Scoring {len(titles):,} distinct headlines under three models ...")

    va = plain_vader()
    fv = _get_analyzer(extended=False)
    fx = _get_analyzer(extended=True)

    def comp(analyzer, idioms=False):
        return titles.map(lambda t: analyzer.polarity_scores(
            apply_idioms(str(t)) if idioms else str(t))["compound"])

    s_va, s_fv = comp(va), comp(fv)
    s_fx = comp(fx, idioms=True)   # FinVADER-Extended: words + collapsed idiom phrases

    def nonneutral(s):
        return (s.abs() > NEUTRAL_BAND)

    n = len(titles)
    rows = [
        {"model": "plain VADER",       "non_neutral": int(nonneutral(s_va).sum())},
        {"model": "finVADER",          "non_neutral": int(nonneutral(s_fv).sum())},
        {"model": "FinVADER-Extended", "non_neutral": int(nonneutral(s_fx).sum())},
    ]
    for r in rows:
        r["pct_non_neutral"] = round(100 * r["non_neutral"] / n, 2)
    out = pd.DataFrame(rows)

    # Marginal effect of OUR 20 words: finVADER-neutral -> Extended-non-neutral
    newly = int((~nonneutral(s_fv) & nonneutral(s_fx)).sum())

    (ROOT / "results" / "lexicon").mkdir(parents=True, exist_ok=True)
    out.to_csv(ROOT / "results" / "lexicon" / "before_after.csv", index=False)

    print("\n" + out.to_string(index=False))
    print(f"\nDistinct headlines:                         {n:,}")
    print(f"Newly non-neutral from our extension:       {newly:,} "
          f"({100*newly/n:.2f}% of headlines)")
    print(f"finVADER -> Extended non-neutral gain:      "
          f"{out.loc[2,'pct_non_neutral'] - out.loc[1,'pct_non_neutral']:+.2f} pts")
    print("\nsaved results/lexicon/before_after.csv")


if __name__ == "__main__":
    main()
