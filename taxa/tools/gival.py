#!/usr/bin/env python3
"""Native raw-file processor for GIVAL downstream task datasets."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
RAW_DIR = PROJECT / "input_original" / "manual_downloads" / "GIVAL"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
OUTPUT = BASE / "outputs" / "tools" / "GIVAL.csv"

TOOL = "GIVAL"
SOURCE_UNIT = "P"

DATASETS = [
    {
        "path": RAW_DIR / "S_without_test_set_DCR_sampled_with_ref.csv",
        "source_file": "input_original/manual_downloads/GIVAL/S_without_test_set_DCR_sampled_with_ref.csv",
        "family": "Coronaviridae",
        "source_label": "coronavirus downstream dataset",
    },
    {
        "path": RAW_DIR / "df_AIV_before_sample.csv",
        "source_file": "input_original/manual_downloads/GIVAL/df_AIV_before_sample.csv",
        "family": "Orthomyxoviridae",
        "source_label": "AIV",
    },
    {
        "path": RAW_DIR / "df_all_mpox.csv",
        "source_file": "input_original/manual_downloads/GIVAL/df_all_mpox.csv",
        "family": "Poxviridae",
        "source_label": "monkeypox",
    },
]

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
    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    rows = []
    for item in DATASETS:
        path = item["path"]
        if not path.exists():
            raise SystemExit(f"Missing GIVAL input: {path}")
        family = item["family"]
        if family not in current_families:
            raise SystemExit(f"GIVAL mapped family not found in ICTV reference: {family}")
        row_count = len(pd.read_csv(path, usecols=[0]))
        rows.append(
            {
                "Tool": TOOL,
                "Current_ICTV_family": family,
                "Source_unit": SOURCE_UNIT,
                "Source_record_count": row_count,
                "Source_file": item["source_file"],
                "Source_label": item["source_label"],
                "Mapping_method": "explicit_dataset_identity_to_current_family",
                "Verification_status": "confirmed_from_structured_dataset",
                "Notes": "Family-level presence inferred from GIVAL downstream task table identity and deduplicated to current ICTV families.",
            }
        )

    out = pd.DataFrame(rows)[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
