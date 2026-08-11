"""FinVADER-Extended idioms — aggregate one idiom round into the idiom tracker.

Reads the 10 per-agent idiom rating files for a round (each a JSON array of
{"p": phrase, "s": score}), computes per-phrase mean + sample std across the 10
passes, applies the fixed filter (|mean| >= 0.5 AND std < 2.0), appends every
evaluated phrase to the persistent idiom tracker, and reports round + cumulative
survivors.

Usage: python scripts/lexicon/12_idiom_aggregate.py <round_no>
Tracker: results/lexicon/idiom_evaluations.csv
"""
from __future__ import annotations

import json
import pathlib
import statistics as stats
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PUB = ROOT / "results" / "lexicon"
RATINGS = PUB / "ratings"
TRACKER = PUB / "idiom_evaluations.csv"

MEAN_MIN = 0.5
STD_MAX = 2.0
AGENTS = [f"agent_{i:02d}" for i in range(1, 11)]


def main(round_no: int) -> None:
    phrases = pd.read_csv(PUB / f"idiom_round{round_no}_candidates.csv")["phrase"].tolist()
    universe = set(phrases)

    maps = {}
    for a in AGENTS:
        data = json.loads((RATINGS / f"idiom_round{round_no}_{a}.json").read_text())
        m = {d["p"]: int(d["s"]) for d in data}
        missing = [p for p in phrases if p not in m]
        stray = [p for p in m if p not in universe]
        if missing:
            print(f"  WARN {a}: {len(missing)} phrases missing (default 0), e.g. {missing[:3]}")
        if stray:
            print(f"  WARN {a}: {len(stray)} stray phrases ignored, e.g. {stray[:3]}")
        maps[a] = m

    rows = []
    for p in phrases:
        scores = [maps[a].get(p, 0) for a in AGENTS]
        mean = stats.mean(scores)
        sd = stats.stdev(scores)
        rows.append({
            "phrase": p, "round": round_no,
            **{a: maps[a].get(p, 0) for a in AGENTS},
            "mean": round(mean, 3), "std": round(sd, 3),
            "n_nonzero": sum(1 for s in scores if s != 0),
            "pass": (abs(mean) >= MEAN_MIN) and (sd < STD_MAX),
        })
    new = pd.DataFrame(rows)

    if TRACKER.exists():
        tracker = pd.read_csv(TRACKER)
        new = new[~new["phrase"].isin(set(tracker["phrase"]))]
        combined = pd.concat([tracker, new], ignore_index=True)
    else:
        combined = new
    combined.to_csv(TRACKER, index=False)

    surv = new[new["pass"]].sort_values("mean")
    print(f"=== idiom round {round_no} aggregate ===")
    print(f"  phrases evaluated this round: {len(new)}")
    print(f"  survivors this round:         {int(new['pass'].sum())}")
    print(f"  cumulative evaluated:         {len(combined)}")
    print(f"  cumulative survivors:         {int(combined['pass'].sum())}")
    print(f"\n  strongest 25 survivors this round:")
    ext = surv.reindex(surv["mean"].abs().sort_values(ascending=False).index)
    for _, r in ext.head(25).iterrows():
        print(f"    {r['phrase']:<26} mean={r['mean']:+.2f} std={r['std']:.2f} nz={r['n_nonzero']}/10")
    tgt = 200 - int(combined["pass"].sum())
    print(f"\n  cumulative idiom survivors {int(combined['pass'].sum())}/200 "
          f"({'REACHED' if tgt <= 0 else str(tgt)+' to go'})")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
