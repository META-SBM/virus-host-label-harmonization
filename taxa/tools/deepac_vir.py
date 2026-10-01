#!/usr/bin/env python3
"""Processor for DeePaC-vir audited taxonomic mapping table."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
INPUT = PROJECT / "intermediate" / "deepac_vir_family_mapping_raw.csv"
OUTPUT = BASE / "outputs" / "tools" / "DeePaC-vir.csv"

TOOL = "DeePaC-vir"
SOURCE_UNIT = "S"
SOURCE_FILE = "input_original/manual_downloads/DeePaC_vir/zenodo_4312525/*.rds"

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


def count_unique_taxa(values: pd.Series) -> int:
    cleaned = {str(v).strip() for v in values.dropna() if str(v).strip() and str(v).strip().lower() != "nan"}
    return len(cleaned)


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing DeePaC-vir audited mapping table: {INPUT}")

    raw = pd.read_csv(INPUT)
    mapped = raw[
        raw["Family_mapping_status"].notna()
        & raw["Current_ICTV_family"].notna()
        & raw["Species.taxid"].notna()
    ].copy()
    if mapped.empty:
        raise SystemExit("DeePaC-vir produced no mapped ICTV families")

    grouped = (
        mapped.groupby("Current_ICTV_family", as_index=False)
        .agg(
            Source_record_count=("Species.taxid", count_unique_taxa),
            Mapping_method=("Family_mapping_status", join_unique),
        )
        .sort_values("Current_ICTV_family")
    )
    grouped["Tool"] = TOOL
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Source_file"] = SOURCE_FILE
    grouped["Source_label"] = grouped["Current_ICTV_family"]
    grouped["Verification_status"] = "confirmed_from_audited_mapping_table"
    grouped["Notes"] = (
        "Deduplicated union of current ICTV families across DeePaC-vir VHDB source taxa. "
        "The simulated read FASTA files are not counted as independent taxa; source counts are unique Species.taxid values in the audited mapping table."
    )

    out = grouped[REQUIRED_COLUMNS]
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
