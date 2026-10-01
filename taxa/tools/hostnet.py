#!/usr/bin/env python3
"""Native raw-file processor for HostNet task datasets."""

from __future__ import annotations

from pathlib import Path
import sys
import zipfile

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
OUTPUT = BASE / "outputs" / "tools" / "HostNet.csv"

TOOL = "HostNet"
SOURCE_UNIT = "N"
HOSTNET_DATASETS = PROJECT / "input_original" / "public_sources" / "hostnet" / "hostnet" / "datasets"
FLAVI_DIR = HOSTNET_DATASETS / "Flavivirus"
RABIES_DIR = HOSTNET_DATASETS / "Rabies"

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


def csv_data_rows(path: Path) -> int:
    return max(sum(1 for _ in path.open(encoding="utf-8", errors="ignore")) - 1, 0)


def csv_or_zip_data_rows(path: Path) -> int:
    if path.exists():
        return csv_data_rows(path)
    zip_candidates = [path.with_suffix(".zip"), path.with_suffix(path.suffix + ".zip")]
    zip_path = next((candidate for candidate in zip_candidates if candidate.exists()), None)
    if zip_path is None:
        raise SystemExit(
            "Missing HostNet partition file: "
            + str(path)
            + " or "
            + " or ".join(str(candidate) for candidate in zip_candidates)
        )
    total = 0
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise SystemExit(f"No CSV files found inside HostNet archive: {zip_path}")
        for name in csv_names:
            with archive.open(name) as handle:
                total += max(sum(1 for _ in handle) - 1, 0)
    return total


def count_task_partitions(task_dir: Path) -> int:
    if not task_dir.exists():
        raise SystemExit(f"Missing HostNet task directory: {task_dir}")
    return sum(csv_or_zip_data_rows(task_dir / f"X_{partition}.csv") for partition in ("train", "val", "test"))


def main() -> None:
    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    for family in ["Flaviviridae", "Rhabdoviridae"]:
        if family not in current_families:
            raise SystemExit(f"HostNet mapped family not found in ICTV reference: {family}")

    flavivirus_rows = count_task_partitions(FLAVI_DIR)
    rabies_rows = count_task_partitions(RABIES_DIR)

    rows = [
        {
            "Tool": TOOL,
            "Current_ICTV_family": "Flaviviridae",
            "Source_unit": SOURCE_UNIT,
            "Source_record_count": flavivirus_rows,
            "Source_file": "input_original/public_sources/hostnet/hostnet/datasets/Flavivirus",
            "Source_label": "Flavivirus task dataset",
            "Mapping_method": "explicit_task_dataset_identity_to_current_family",
            "Verification_status": "confirmed_from_structured_dataset",
            "Notes": "Family-level presence inferred from HostNet Flavivirus task dataset identity; row count sums X_train/X_val/X_test records.",
        },
        {
            "Tool": TOOL,
            "Current_ICTV_family": "Rhabdoviridae",
            "Source_unit": SOURCE_UNIT,
            "Source_record_count": rabies_rows,
            "Source_file": "input_original/public_sources/hostnet/hostnet/datasets/Rabies",
            "Source_label": "Rabies lyssavirus task dataset",
            "Mapping_method": "explicit_task_dataset_identity_to_current_family",
            "Verification_status": "confirmed_from_structured_dataset",
            "Notes": "Family-level presence inferred from HostNet Rabies task dataset identity; row count sums X_train/X_val/X_test records.",
        },
    ]
    out = pd.DataFrame(rows)[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
