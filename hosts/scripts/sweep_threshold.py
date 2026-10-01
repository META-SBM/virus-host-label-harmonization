# -*- coding: utf-8 -*-
"""What the scheme looks like at every retention threshold, not just the chosen one.

    python3 sweep_threshold.py

Writes scripts/threshold_sweep.csv.
"""
import csv
import os
import subprocess
import sys

SC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SC, "threshold_sweep.csv")
PREFIX = "_sweep"
THRESHOLDS = range(1, 9)
# Kept in step with SPECIES_STANDALONE_THRESHOLD in build_general_scheme.py.
CHOSEN = int(__import__("os").environ.get("SPECIES_STANDALONE_THRESHOLD", 5))
SUFFIXES = ["_matrix.csv", "_matrix_wide.csv", "_row_fate.csv", "_unnamed_detail.csv"]


def clean() -> None:
    for s in SUFFIXES:
        p = os.path.join(SC, PREFIX + s)
        if os.path.exists(p):
            os.remove(p)


def read(name: str) -> list:
    with open(os.path.join(SC, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_data() -> dict:
    """How many dataset instances name each species. Two different species
    counts follow from this, and the difference is not a rounding error: a
    species can clear the bar and still be pooled, because the vector and
    crustacean mappings are finer than the threshold."""
    n_instances = {}
    for r in read("species_matrix.csv"):
        if r["Rank"] == "species" and float(r["Count"]) > 0:
            n_instances.setdefault(r["Row"], set()).add(r["Tool"])
    return {"instances_per_species": n_instances}


def build_at(threshold: int) -> tuple:
    """Rebuild the scheme under a temporary prefix, so the sweep writes beside
    the committed files rather than over them."""
    env = dict(os.environ,
               SPECIES_STANDALONE_THRESHOLD=str(threshold),
               GENERAL_SCHEME_PREFIX=PREFIX)
    r = subprocess.run([sys.executable, os.path.join(SC, "build_general_scheme.py")],
                       cwd=SC, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit(f"builder failed at threshold {threshold}")
    return read(PREFIX + "_matrix.csv"), read(PREFIX + "_row_fate.csv")


def process_data(data: dict) -> tuple:
    n_instances = data["instances_per_species"]
    rows, n_inst = [], None
    try:
        for t in THRESHOLDS:
            matrix, fate = build_at(t)
            n_inst = len({m["Tool"] for m in matrix})  # same corpus every time; checked below
            rows.append({
                "Threshold": t,
                "Share of instances": f"{100 * t / n_inst:.0f}%",
                "Categories": len({m["Row"] for m in matrix}),
                "Species clearing the bar": sum(1 for v in n_instances.values() if len(v) >= t),
                "Species drawn as their own row": sum(1 for f in fate
                                                      if f["Fate"] == "standalone_species"),
                "Records": round(sum(float(m["Count"]) for m in matrix)),
            })
    finally:
        clean()

    # Every setting must move the same records around, or the sweep is comparing
    # different data rather than different displays of one dataset.
    totals = {r["Records"] for r in rows}
    assert len(totals) == 1, f"thresholds disagree on the record total: {totals}"
    return rows, n_inst


def save(rows: list, n_instances: int) -> None:
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print("saved ->", OUT)
    width = max(len(str(r["Categories"])) for r in rows)
    for r in rows:
        mark = "  <- used" if r["Threshold"] == CHOSEN else ""
        print(f"  >={r['Threshold']} of {n_instances} ({r['Share of instances']:>3})  "
              f"{r['Categories']:>{width}} categories, "
              f"{r['Species clearing the bar']:>4} species clear it, "
              f"{r['Species drawn as their own row']:>4} drawn as their own row{mark}")


if __name__ == "__main__":
    save(*process_data(load_data()))
