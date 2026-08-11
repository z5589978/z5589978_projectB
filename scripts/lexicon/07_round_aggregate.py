"""FinVADER-Extended — aggregate one mining round's ratings into the tracker.

Reads a round's non-zero score maps (each agent's complete non-zero scores;
unlisted words = 0 for that agent), over the round's candidate universe. Computes
per-word mean + sample std across the 10 passes, applies the fixed filter
(|mean| >= MEAN_MIN AND std < STD_MAX), appends every evaluated word to the
persistent tracker, and reports the round + cumulative survivor count.

Usage: python scripts/lexicon/07_round_aggregate.py <round_number>
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
TRACKER = PUB / "lexicon_evaluations.csv"

MEAN_MIN = 0.5
STD_MAX = 2.0
AGENTS = [f"agent_{i:02d}" for i in range(1, 11)]


def main(round_no: int) -> None:
    words = pd.read_csv(PUB / f"round{round_no}_candidates.csv")["word"].tolist()
    raw = json.loads((RATINGS / f"round{round_no}_scores_nonzero.json").read_text())

    # Validate: every non-zero word must be in the candidate universe
    universe = set(words)
    for a in AGENTS:
        stray = [w for w in raw[a] if w not in universe]
        if stray:
            raise SystemExit(f"{a}: words not in candidate list: {stray[:10]}")

    rows = []
    for w in words:
        scores = [int(raw[a].get(w, 0)) for a in AGENTS]
        mean = stats.mean(scores)
        sd = stats.stdev(scores)
        rows.append({
            "word": w, "round": round_no,
            **{a: raw[a].get(w, 0) for a in AGENTS},
            "mean": round(mean, 3), "std": round(sd, 3),
            "n_nonzero": sum(1 for s in scores if s != 0),
            "pass": (abs(mean) >= MEAN_MIN) and (sd < STD_MAX),
        })
    new = pd.DataFrame(rows)

    tracker = pd.read_csv(TRACKER)
    # Drop any words already tracked (safety; extraction should have excluded them)
    new = new[~new["word"].isin(set(tracker["word"]))]
    combined = pd.concat([tracker, new], ignore_index=True)
    combined.to_csv(TRACKER, index=False)

    survivors = new[new["pass"]].sort_values("mean")
    print(f"=== Round {round_no} aggregate ===")
    print(f"  candidates evaluated this round: {len(new)}")
    print(f"  survivors this round:            {int(new['pass'].sum())}")
    print(f"  cumulative words evaluated:      {len(combined)}")
    print(f"  cumulative survivors:            {int(combined['pass'].sum())}")
    print(f"\n  round {round_no} survivors (|mean|>={MEAN_MIN}, std<{STD_MAX}):")
    for _, r in survivors.iterrows():
        print(f"    {r['word']:<15} mean={r['mean']:+.2f} std={r['std']:.2f} nz={r['n_nonzero']}/10")

    remaining = 100 - int(combined["pass"].sum())
    print(f"\n  cumulative survivors {int(combined['pass'].sum())}/100 "
          f"({'REACHED' if remaining <= 0 else str(remaining)+' to go'})")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
