#!/usr/bin/env python3
"""Processor for VirHostPRED audited protein-accession taxonomy table."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
INPUT = PROJECT / "intermediate" / "virhostpred_accession_taxonomy.csv"
OUTPUT = BASE / "outputs" / "tools" / "VirHostPRED.csv"

TOOL = "VirHostPRED"
SOURCE_UNIT = "P"

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


def join_unique(values: pd.Series) -> str:
    return "; ".join(sorted({str(v).strip() for v in values.dropna() if str(v).strip()}))


def source_files(values: pd.Series) -> str:
    return "; ".join(
        f"input_original/manual_downloads/VirHostPRED/{v}"
        for v in sorted({str(v).strip() for v in values.dropna() if str(v).strip()})
    )


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing VirHostPRED audited taxonomy table: {INPUT}")

    raw = pd.read_csv(INPUT)
    mapped = raw[raw["Current_ICTV_family"].notna()].copy()
    if mapped.empty:
        raise SystemExit("VirHostPRED produced no mapped ICTV families")

    grouped = (
        mapped.groupby("Current_ICTV_family", as_index=False)
        .agg(
            Source_record_count=("Protein_accession", "nunique"),
            Source_file=("Dataset_file", source_files),
            Mapping_method=("Mapping_method", join_unique),
        )
        .sort_values("Current_ICTV_family")
    )
    grouped["Tool"] = TOOL
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Source_label"] = grouped["Current_ICTV_family"]
    grouped["Verification_status"] = "confirmed_from_audited_mapping_table"
    grouped["Notes"] = (
        "Family-level presence from audited VirHostPRED protein-accession taxonomy mapping. "
        "Source counts are unique protein accessions per current ICTV family."
    )

    out = grouped[REQUIRED_COLUMNS]
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
