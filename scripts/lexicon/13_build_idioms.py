"""FinVADER-Extended idioms — build the accepted idiom table from the tracker.

Keeps the passing phrases (|mean| >= 0.5 AND std < 2.0) and writes the single
source of truth the scorer loads into VADER's SPECIAL_CASE_IDIOMS:

  results/lexicon/kept_idioms.csv   (phrase, mean_valence)
"""
from __future__ import annotations

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PUB = ROOT / "results" / "lexicon"


def main() -> None:
    tracker = pd.read_csv(PUB / "idiom_evaluations.csv")
    kept = tracker[tracker["pass"]].copy()
    out = (kept[["phrase", "mean"]]
           .rename(columns={"mean": "mean_valence"})
           .sort_values("mean_valence")
           .reset_index(drop=True))
    out.to_csv(PUB / "kept_idioms.csv", index=False)

    print("=== FinVADER-Extended: build accepted idioms ===")
    print(f"  phrases evaluated (all rounds): {len(tracker)}")
    by_round = tracker.groupby("round")["pass"].agg(["size", "sum"])
    for rnd, r in by_round.iterrows():
        print(f"    round {rnd}: {int(r['sum'])}/{int(r['size'])} passed")
    print(f"  accepted idioms:                {len(out)}")
    print(f"  valence range:                  {out['mean_valence'].min()} .. {out['mean_valence'].max()}")
    print(f"\n  saved results/lexicon/kept_idioms.csv")


if __name__ == "__main__":
    main()
