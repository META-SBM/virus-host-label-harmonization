#!/usr/bin/env python3
"""Processor for Host Taxon Predictor audited record-to-family mapping of the raw release."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
INPUT = PROJECT / "intermediate" / "host_taxon_predictor_family_mapping_raw.csv"
OUTPUT = BASE / "outputs" / "tools" / "Host_Taxon_Predictor.csv"

TOOL = "Host Taxon Predictor"
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
    return "; ".join(sorted({str(v).strip() for v in values.dropna() if str(v).strip() and str(v).strip().lower() != "nan"}))


def count_records(values: pd.Series) -> int:
    cleaned = {str(v).strip() for v in values.dropna() if str(v).strip() and str(v).strip().lower() != "nan"}
    return len(cleaned) if cleaned else len(values)


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing family mapping table: {INPUT}")
    raw = pd.read_csv(INPUT)
    mapped = raw[
        raw["Tool"].eq(TOOL)
        & raw["Included_in_matrix"].eq(1)
        & raw["Current_ICTV_family"].notna()
    ].copy()
    if mapped.empty:
        raise SystemExit("Host Taxon Predictor produced no mapped ICTV families")

    grouped = (
        mapped.groupby("Current_ICTV_family", as_index=False)
        .agg(
            Source_record_count=("Raw_record_ID", count_records),
            Source_file=("Source_file", join_unique),
            Mapping_method=("Mapping_method", join_unique),
        )
        .sort_values("Current_ICTV_family")
    )
    grouped["Tool"] = TOOL
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Source_label"] = grouped["Current_ICTV_family"]
    grouped["Verification_status"] = "confirmed_from_audited_mapping_table"
    grouped["Notes"] = (
        "Family-level presence from audited Host Taxon Predictor record-to-family mapping of the raw release. "
        "The main learn/test and extension learn/test GI split files were verified as represented in "
        "all_viruses_with_desired_attributes.dump; new_viruses_ids requires separate remapping."
    )
    out = grouped[REQUIRED_COLUMNS]
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
