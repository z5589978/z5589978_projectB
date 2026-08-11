"""FinVADER-Extended — build the accepted lexicon from the round tracker.

Reads results/lexicon/lexicon_evaluations.csv (every word ever evaluated across
all rounds), keeps the passing words (|mean| >= 0.5 AND std < 2.0), and writes the
single source of truth the scorer loads:

  results/lexicon/kept_lexicon.csv   (word, mean_valence)  -- all rounds combined
"""
from __future__ import annotations

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PUB = ROOT / "results" / "lexicon"


def main() -> None:
    tracker = pd.read_csv(PUB / "lexicon_evaluations.csv")
    kept = tracker[tracker["pass"]].copy()
    out = (kept[["word", "mean"]]
           .rename(columns={"mean": "mean_valence"})
           .sort_values("mean_valence")
           .reset_index(drop=True))
    out.to_csv(PUB / "kept_lexicon.csv", index=False)

    print("=== FinVADER-Extended: build accepted lexicon ===")
    print(f"  words evaluated (all rounds): {len(tracker)}")
    by_round = tracker.groupby('round')['pass'].agg(['size', 'sum'])
    for rnd, r in by_round.iterrows():
        print(f"    round {rnd}: {int(r['sum'])}/{int(r['size'])} passed")
    print(f"  accepted lexicon size:        {len(out)}")
    print(f"  valence range:                {out['mean_valence'].min()} .. {out['mean_valence'].max()}")
    print(f"\n  saved results/lexicon/kept_lexicon.csv")


if __name__ == "__main__":
    main()
