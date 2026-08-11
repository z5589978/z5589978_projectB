"""FinVADER-Extended — prepare the next mining round's candidate list.

1. Ensure the persistent audit tracker exists (seed from round 1 if absent).
2. Recompute the full common-candidate pool from the current corpus.
3. Exclude every word already evaluated in any previous round.
4. Write the next round's candidate list (ranked by frequency), optionally capped.

Tracker: results/lexicon/lexicon_evaluations.csv
  columns: word, round, agent_01..agent_10, mean, std, n_nonzero, pass
Round candidates: results/lexicon/round{N}_candidates.csv
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
RAW = ROOT / "data" / "lexicon_extension"
PUB = ROOT / "results" / "lexicon"
TRACKER = PUB / "lexicon_evaluations.csv"

MEAN_MIN = 0.5     # magnitude floor (adopted bar)
STD_MAX = 2.0      # agreement gate
BATCH_CAP = 450    # max candidates to hand to one round (keeps agent JSON reliable)

from _lexicon_common import common_candidates


def seed_tracker_from_round1() -> pd.DataFrame:
    """Build the tracker from round 1's ratings_matrix.csv."""
    m = pd.read_csv(PUB / "ratings_matrix.csv")
    m.insert(1, "round", 1)
    m["pass"] = (m["mean"].abs() >= MEAN_MIN) & (m["std"] < STD_MAX)
    return m


def main() -> None:
    if TRACKER.exists():
        tracker = pd.read_csv(TRACKER)
    else:
        tracker = seed_tracker_from_round1()
        tracker.to_csv(TRACKER, index=False)
        print(f"Seeded tracker from round 1: {len(tracker)} words "
              f"({int(tracker['pass'].sum())} passed)")

    evaluated = set(tracker["word"])
    next_round = int(tracker["round"].max()) + 1

    pool = common_candidates((RAW / "corpus_text.txt").read_text(encoding="utf-8", errors="ignore"))
    fresh = [(w, c) for w, c in pool if w not in evaluated]
    batch = fresh[:BATCH_CAP]

    out = pd.DataFrame(batch, columns=["word", "frequency"])
    out_path = PUB / f"round{next_round}_candidates.csv"
    out.to_csv(out_path, index=False)

    print(f"\n=== Round {next_round} candidate prep ===")
    print(f"  words already evaluated (all rounds): {len(evaluated)}")
    print(f"  cumulative survivors so far:          {int(tracker['pass'].sum())}")
    print(f"  common candidates in corpus:          {len(pool)}")
    print(f"  fresh (never-evaluated) candidates:   {len(fresh)}")
    print(f"  this round's batch (cap {BATCH_CAP}):        {len(batch)}")
    if batch:
        print(f"  frequency range: {batch[-1][1]}-{batch[0][1]}")
    print(f"\n  saved {out_path.relative_to(ROOT)}")
    if len(fresh) < 50:
        print("\n  NOTE: corpus nearly exhausted of fresh candidates — a new scrape "
              "(wider dates/categories) is needed for further rounds.")


if __name__ == "__main__":
    main()
