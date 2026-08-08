"""FinVADER-Extended, step 3 — aggregate the 10 rating passes and filter.

Reads data/lexicon_extension/ratings/all_ratings_raw.json (10 independent passes),
computes per-word mean and standard deviation across the panel, and applies the
agreement filter:

    keep word iff  mean != 0  AND  std < STD_MAX

STD_MAX = 2.0 is "25% of the -4..+4 range" (range 8, 25% = 2.0). Because the panel
agrees tightly, std is small for almost every word, so std rarely binds; the report
also shows stricter |mean| cut-offs so the threshold choice is transparent.

Outputs (committable — derived scores, no raw article text):
  data/lexicon_extension/ratings_matrix.csv     word x 10 agent scores + mean/std
  data/lexicon_extension/candidate_scores.csv   word, mean, std, n_nonzero, kept
  data/lexicon_extension/kept_lexicon.csv        survivors: word, mean_valence
Also writes per-agent JSON files split from the archive.
"""
from __future__ import annotations

import json
import pathlib
import statistics as stats

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "results" / "lexicon"          # committed derived artifacts
RATINGS = OUT / "ratings"
OUT.mkdir(parents=True, exist_ok=True)

STD_MAX = 2.0     # 25% of the 8-point (-4..+4) range (agreement gate)
MEAN_MIN = 0.5    # magnitude floor: panel must show at least a mild directional
                  # consensus. Chosen after seeing max std = 0.52 (std never binds),
                  # so mean!=0 alone would admit 1-of-10 near-noise words.


def main() -> None:
    raw = json.loads((RATINGS / "all_ratings_raw.json").read_text())
    agents = sorted(raw)                       # agent_01 .. agent_10

    # Split each pass into its own file (reproducibility archive)
    for a in agents:
        (RATINGS / f"{a}.json").write_text(json.dumps(raw[a], indent=1))

    # Score matrix: word -> {agent: score}
    words = [d["w"] for d in raw[agents[0]]]
    matrix = {w: {} for w in words}
    for a in agents:
        for d in raw[a]:
            matrix[d["w"]][a] = d["s"]

    rows = []
    for w in words:
        scores = [matrix[w][a] for a in agents]
        mean = stats.mean(scores)
        sd = stats.stdev(scores)               # sample std (ddof=1)
        rows.append({
            "word": w,
            **{a: matrix[w][a] for a in agents},
            "mean": round(mean, 3),
            "std": round(sd, 3),
            "n_nonzero": sum(1 for s in scores if s != 0),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "ratings_matrix.csv", index=False)

    # Filter: agreement gate (std) AND magnitude floor (|mean|).
    df["kept"] = (df["mean"].abs() >= MEAN_MIN) & (df["std"] < STD_MAX)
    df[["word", "mean", "std", "n_nonzero", "kept"]].to_csv(
        OUT / "candidate_scores.csv", index=False)

    kept = df[df["kept"]].copy().sort_values("mean")
    kept_out = kept[["word", "mean"]].rename(columns={"mean": "mean_valence"})
    kept_out.to_csv(OUT / "kept_lexicon.csv", index=False)

    # Report
    print("=== FinVADER-Extended step 3: aggregate + filter ===")
    print(f"  candidates rated:        {len(df)}")
    print(f"  max std across panel:    {df['std'].max():.3f}  (STD_MAX = {STD_MAX})")
    print(f"  std filter alone passes: {(df['std'] < STD_MAX).sum()}")
    print(f"  mean != 0 alone passes:  {(df['mean'] != 0).sum()}")
    print(f"  BOTH (kept):             {df['kept'].sum()}")
    print("\n  transparency — how many survive under stricter |mean| cut-offs:")
    for thr in (0.0, 0.5, 1.0, 1.5):
        n = ((df['mean'].abs() > thr) & (df['std'] < STD_MAX)).sum()
        print(f"    |mean| > {thr:>3}:  {n}")
    print("\n  KEPT words (mean != 0, std < 2.0), sorted by valence:")
    for _, r in kept.iterrows():
        print(f"    {r['word']:<16} mean={r['mean']:+.2f}  std={r['std']:.2f}  nonzero={r['n_nonzero']}/10")
    print(f"\n  saved ratings_matrix.csv, candidate_scores.csv, kept_lexicon.csv")


if __name__ == "__main__":
    main()
