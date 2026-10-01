#!/usr/bin/env python3
"""Native raw-file processor for MENB task datasets."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
OUTPUT = BASE / "outputs" / "tools" / "MENB.csv"

TOOL = "MENB"
SOURCE_UNIT = "N"
MENB_BASE = PROJECT / "input_original" / "manual_downloads" / "MENB" / "DatasetsSpecifications"

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
    (
        [
            "MENB-H|V&H,V/Corona",
            "New Hosts/Corona/Test",
            "Test sets 20 Corona-Orthomyxo/Corona/Test",
            "Dataset 90 seqs Corona/Full Train Anlaysis",
            "Dataset 90 seqs Corona/Non overlapping for Training and Tests",
        ],
        "Coronaviridae",
    ),
    (
        [
            "MENB-H|V&H,V/Flavi",
            "New Hosts/Flavi/Test ",
        ],
        "Flaviviridae",
    ),
    (
        [
            "MENB-H|V&H,V/Orthomyxo",
            "New Hosts/Orthomyxo/Test",
            "Test sets 20 Corona-Orthomyxo/Orthomyxo/Test",
        ],
        "Orthomyxoviridae",
    ),
    (
        [
            "MENB-H|V&H,V/Picorna",
            "New Hosts/Picorna/Test",
        ],
        "Picornaviridae",
    ),
    (
        [
            "New Viruses/Arteriviridae/Swine1.csv",
            "New Viruses/Arteriviridae/Swine2.csv",
            "New Viruses/Arteriviridae/Swine3.csv",
        ],
        "Arteriviridae",
    ),
    (
        [
            "New Viruses/Calicivirus/Test/Avian.csv",
            "New Viruses/Calicivirus/Test/Human.csv",
            "New Viruses/Calicivirus/Test/Swine.csv",
        ],
        "Caliciviridae",
    ),
    (
        [
            "New Viruses/Paramyxoviridae/Avian1.csv",
            "New Viruses/Paramyxoviridae/Avian2.csv",
            "New Viruses/Paramyxoviridae/Avian3.csv",
        ],
        "Paramyxoviridae",
    ),
    (
        [
            "New Viruses/Rabhdoviridae/Human1.csv",
            "New Viruses/Rabhdoviridae/Human2.csv",
            "New Viruses/Rabhdoviridae/Human3.csv",
        ],
        "Rhabdoviridae",
    ),
]


def count_csv_rows(path: Path) -> int:
    return max(sum(1 for _ in path.open(encoding="utf-8", errors="ignore")) - 1, 0)


def expand_sources(source_spec: str | list[str]) -> list[Path]:
    rel_paths = source_spec if isinstance(source_spec, list) else [source_spec]
    paths: list[Path] = []
    for rel in rel_paths:
        path = MENB_BASE / rel
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.csv")))
        else:
            paths.append(path)
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("Missing MENB input file(s): " + "; ".join(missing))
    return paths


def source_file_label(source_spec: str | list[str]) -> str:
    rel_paths = source_spec if isinstance(source_spec, list) else [source_spec]
    return "; ".join(f"input_original/manual_downloads/MENB/DatasetsSpecifications/{rel}" for rel in rel_paths)


def main() -> None:
    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    rows = []

    for source_spec, family in TASKS:
        if family not in current_families:
            raise SystemExit(f"MENB mapped family not found in ICTV reference: {family}")
        files = expand_sources(source_spec)
        source_record_count = sum(count_csv_rows(path) for path in files)
        rows.append(
            {
                "Tool": TOOL,
                "Current_ICTV_family": family,
                "Source_unit": SOURCE_UNIT,
                "Source_record_count": source_record_count,
                "Source_file": source_file_label(source_spec),
                "Source_label": family,
                "Mapping_method": "explicit_task_dataset_identity_to_current_family",
                "Verification_status": "confirmed_from_structured_dataset",
                "Notes": (
                    "Family-level presence inferred from MENB task dataset identity; row count sums listed CSV records across "
                    "available train/test task partitions. Generic MENB-H pooled host-model files are not counted here because "
                    "family identity is not encoded in their paths and would require separate accession-level remapping."
                ),
            }
        )

    out = pd.DataFrame(rows)[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")
    write_table(out, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {out.shape[0]} current families")


if __name__ == "__main__":
    main()
