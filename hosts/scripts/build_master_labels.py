# -*- coding: utf-8 -*-
"""Assemble master_labels.csv from the recomputed counts and the two curation
tables.

    python3 build_master_labels.py
"""
import glob
import os
import sys

import pandas as pd

from categories import CATS, DETAILED_SCHEME_REMAP, is_excluded

SC = os.path.dirname(os.path.abspath(__file__))
COUNTS_DIR = os.path.join(os.path.dirname(SC), "per_tool_counts_from_scratch_v2",
                          "counts_per_tool_v2")
ENRICHMENT = os.path.join(SC, "label_enrichment.csv")
CATEGORIES = os.path.join(SC, "label_categories.csv")
OUT = os.path.join(SC, "master_labels.csv")

CAT_LABELS = set(c[0] for c in CATS)
MASTER_COLUMNS = [
    "Tool", "Original_label", "Count", "Status", "Label_level", "Data_category",
    "Counting_unit", "Notes", "Level_1", "Level_2", "Level_3", "Level_4",
    "Terminal_category", "Mapping_confidence", "Parent_label", "Overlaps_with",
    "Potential_double_count", "Broad_scheme", "Intermediate_scheme", "Detailed_scheme",
]


def fail(msg: str) -> None:
    """Stop the pipeline loudly. run_all.py checks the return code."""
    print(f"\nFAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def load_data() -> dict:
    """The counts files, one row per (Tool, Original_label), and the two
    hand-curated tables."""
    raw_rows = []
    for f in sorted(glob.glob(os.path.join(COUNTS_DIR, "*_counts.csv"))):
        with open(f) as fh:
            lines = fh.readlines()
        tool = lines[0].split(",", 1)[1].strip().strip('"')
        data_start = next(i for i, l in enumerate(lines) if l.startswith("Label"))
        df = pd.read_csv(f, skiprows=data_start)
        df = df[df.iloc[:, 0] != "TOTAL"]
        df = df.dropna(subset=[df.columns[0]])
        for _, r in df.iterrows():
            raw_rows.append((tool, str(r.iloc[0]).strip(), r.iloc[1]))
    raw = pd.DataFrame(raw_rows, columns=["Tool", "Original_label", "Count"])
    enrichment = pd.read_csv(ENRICHMENT)
    categories = pd.read_csv(CATEGORIES)

    # Excluded instances keep their raw files, counts and curation rows; they
    # are dropped here so that nothing downstream has to know about them.
    for name, df in (("raw", raw), ("enrichment", enrichment), ("categories", categories)):
        keep = ~df["Tool"].map(is_excluded)
        if name == "raw":
            raw = df[keep]
        elif name == "enrichment":
            enrichment = df[keep]
        else:
            categories = df[keep]
    return {"raw": raw, "enrichment": enrichment, "categories": categories}


def check_curation_covers_counts(raw: pd.DataFrame, tables: dict) -> None:
    """A curation table must name every recomputed label and nothing else. A
    missing row would drop a label silently; a stale one means the curation
    still describes data that no longer exists."""
    raw_keys = set(zip(raw["Tool"], raw["Original_label"]))
    for name, df in tables.items():
        keys = set(zip(df["Tool"], df["Original_label"]))
        missing = raw_keys - keys
        stale = keys - raw_keys
        if missing:
            fail(f"{name} is missing {len(missing)} label(s) present in "
                 f"counts_per_tool_v2: {sorted(missing)[:5]}"
                 + (" ..." if len(missing) > 5 else ""))
        if stale:
            fail(f"{name} has {len(stale)} label(s) that no longer exist in "
                 f"counts_per_tool_v2 (stale curation row?): {sorted(stale)[:5]}"
                 + (" ..." if len(stale) > 5 else ""))


def check_every_category_resolves(master: pd.DataFrame) -> None:
    """A Detailed_scheme matching no category is dropped outright by the figure
    scripts rather than folded anywhere, so it must fail here instead."""
    checked = master[master["Data_category"].isin(["host", "unclear"])]
    remapped = checked["Detailed_scheme"].replace(DETAILED_SCHEME_REMAP)
    bad = checked[~remapped.isin(CAT_LABELS)]
    if len(bad):
        rows = list(zip(bad["Tool"], bad["Original_label"], bad["Detailed_scheme"], bad["Count"]))
        fail(f"{len(bad)} row(s) have a Detailed_scheme that matches no category in "
             f"categories.CATS (even after DETAILED_SCHEME_REMAP) -- these would silently "
             f"vanish from every figure instead of being counted:\n  " +
             "\n  ".join(f"{t} / {l!r} -> {d!r} ({c:,.0f} records)" for t, l, d, c in rows))


def process_data(data: dict) -> pd.DataFrame:
    """Join the counts to their curation, apply the count overrides, and check
    both invariants."""
    raw = data["raw"]
    check_curation_covers_counts(raw, {"label_enrichment.csv": data["enrichment"],
                                       "label_categories.csv": data["categories"]})
    master = raw.merge(data["enrichment"], on=["Tool", "Original_label"],
                       how="left", validate="one_to_one")
    master = master.merge(data["categories"], on=["Tool", "Original_label"],
                          how="left", validate="one_to_one")
    has_override = master["Count_override"].notna() & (master["Count_override"] != "")
    master.loc[has_override, "Count"] = pd.to_numeric(master.loc[has_override, "Count_override"])
    master = master.drop(columns=["Count_override"])
    check_every_category_resolves(master)
    return master[MASTER_COLUMNS]


def save(master: pd.DataFrame) -> None:
    """Write master_labels.csv."""
    master.to_csv(OUT, index=False)
    print(f"saved -> {OUT} ({len(master)} rows)")


if __name__ == "__main__":
    save(process_data(load_data()))
