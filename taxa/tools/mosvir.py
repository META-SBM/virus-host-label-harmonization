#!/usr/bin/env python3
"""Processor for MosViR audited taxonomic mapping table."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
INPUT = PROJECT / "intermediate" / "mosvir_family_mapping_raw.csv"
OUTPUT = BASE / "outputs" / "tools" / "MosViR.csv"

TOOL = "MosViR"
SOURCE_UNIT = "N"

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


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing MosViR audited mapping table: {INPUT}")

    raw = pd.read_csv(INPUT)
    mapped = raw[
        raw["Mapping_status"].eq("mapped")
        & raw["Current_ICTV_family"].notna()
        & raw["Include_in_eukaryotic_main_figure"].eq("yes")
    ].copy()
    if mapped.empty:
        raise SystemExit("MosViR produced no mapped eukaryote-associated ICTV families")

    grouped = (
        mapped.groupby("Current_ICTV_family", as_index=False)
        .agg(
            Source_record_count=("Source_rows", "sum"),
            Source_file=("Source_file", join_unique),
            Mapping_method=("Mapping_rule", join_unique),
        )
        .sort_values("Current_ICTV_family")
    )
    grouped["Tool"] = TOOL
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Source_label"] = grouped["Current_ICTV_family"]
    grouped["Verification_status"] = "confirmed_from_audited_mapping_table"
    grouped["Notes"] = (
        "Deduplicated union of current ICTV families across unique virus TaxIDs in MosViR Supplementary Table S1. "
        "Host-association rows and 500 bp fragments are not counted as independent taxa; source counts sum source rows from the audited mapping table."
    )

    out = grouped[REQUIRED_COLUMNS]
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
