#!/usr/bin/env python3
"""Native raw-file processor for VIDHOP task datasets."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
OUTPUT = BASE / "outputs" / "tools" / "VIDHOP.csv"

TOOL = "VIDHOP"
SOURCE_UNIT = "N"
VIDHOP_BASE = PROJECT / "input_original" / "manual_downloads" / "VIDHOP" / "train_data"

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

TASKS = [
    ("small_paper_version_Influ_strict/species", "Orthomyxoviridae", "Influenza species-level task dataset"),
    ("small_paper_version_Rabies_strict/species", "Rhabdoviridae", "Rabies species-level task dataset"),
    ("small_paper_version_Rota_strict/species", "Sedoreoviridae", "Rotavirus species-level task dataset"),
]


def count_data_rows_no_header(path: Path) -> int:
    return sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))


def main() -> None:
    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    rows = []

    for rel_dir, family, label in TASKS:
        if family not in current_families:
            raise SystemExit(f"VIDHOP mapped family not found in ICTV reference: {family}")
        task_dir = VIDHOP_BASE / rel_dir
        if not task_dir.exists():
            raise SystemExit(f"Missing VIDHOP input directory: {task_dir}")
        x_files = sorted(task_dir.glob("X_*.csv"))
        if not x_files:
            raise SystemExit(f"No VIDHOP X_*.csv files found in {task_dir}")
        source_record_count = sum(count_data_rows_no_header(path) for path in x_files)
        source_file = f"input_original/manual_downloads/VIDHOP/train_data/{rel_dir}"
        rows.append(
            {
                "Tool": TOOL,
                "Current_ICTV_family": family,
                "Source_unit": SOURCE_UNIT,
                "Source_record_count": source_record_count,
                "Source_file": source_file,
                "Source_label": label,
                "Mapping_method": "explicit_task_dataset_identity_to_current_family",
                "Verification_status": "confirmed_from_structured_dataset",
                "Notes": "Family-level presence inferred from VIDHOP task dataset identity; row count sums X_train/X_val/X_test records.",
            }
        )

    out = pd.DataFrame(rows)[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
