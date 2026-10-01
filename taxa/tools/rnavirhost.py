#!/usr/bin/env python3
"""Native raw-file processor for RNAVirHost."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
GENUS_REF = PROJECT / "intermediate" / "ictv_genus_to_family_reference_msl41_v1.csv"
INPUT = PROJECT / "input_original" / "manual_downloads" / "RNAVirHost" / "virus_label(1).csv"
OUTPUT = BASE / "outputs" / "tools" / "RNAVirHost.csv"

TOOL = "RNAVirHost"
SOURCE_UNIT = "N"
SOURCE_FILE = "input_original/manual_downloads/RNAVirHost/virus_label(1).csv"

REQUIRED_COLUMNS = [
    "Tool",
    "Current_ICTV_family",
    "Source_unit",
    "Source_record_count",
    "Source_file",
    "Source_label",
    "Mapping_method",
    "Verification_status",
    "Notes",
]


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing RNAVirHost input: {INPUT}")

    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    genus_ref = pd.read_csv(GENUS_REF)
    genus_to_family = dict(
        zip(genus_ref["classification"].astype(str), genus_ref["Current_ICTV_family"].astype(str))
    )

    raw = pd.read_csv(INPUT, usecols=["y|virus family", "y|virus genus"])
    mapped_rows = []
    skipped = 0
    for _, row in raw.iterrows():
        source_family = str(row["y|virus family"]).strip()
        source_genus = str(row["y|virus genus"]).strip()
        if source_family in current_families:
            mapped_rows.append((source_family, source_family, "exact_current_family"))
        elif source_family == "Totiviridae" and source_genus in genus_to_family:
            mapped_rows.append((genus_to_family[source_genus], source_family, "legacy_family_resolved_by_current_genus"))
        else:
            skipped += 1

    if not mapped_rows:
        raise SystemExit("RNAVirHost produced no mapped ICTV families")

    mapped = pd.DataFrame(mapped_rows, columns=["Current_ICTV_family", "Source_label", "Mapping_method"])
    counts = (
        mapped.groupby(["Current_ICTV_family", "Source_label", "Mapping_method"], as_index=False)
        .size()
        .rename(columns={"size": "Source_record_count"})
    )
    counts["Tool"] = TOOL
    counts["Source_unit"] = SOURCE_UNIT
    counts["Source_file"] = SOURCE_FILE
    counts["Verification_status"] = "confirmed_from_structured_dataset"
    counts["Notes"] = (
        "Family-level presence from RNAVirHost lineage table. "
        "Legacy Totiviridae rows are resolved to current ICTV families by genus where possible; unmapped/unclassified rows are excluded."
    )

    out = counts[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families; skipped rows={skipped}")


if __name__ == "__main__":
    main()
