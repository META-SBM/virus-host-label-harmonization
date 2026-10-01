#!/usr/bin/env python3
"""Native raw-file processor for SPHAK."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
RAW_DIR = PROJECT / "input_original" / "manual_downloads" / "SPHAK"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
OUTPUT = BASE / "outputs" / "tools" / "SPHAK.csv"

TOOL = "SPHAK"
SOURCE_UNIT = "P"
FILES = [
    (
        RAW_DIR / "animal_virus_data.csv",
        "input_original/manual_downloads/SPHAK/animal_virus_data.csv",
        "utf-8",
    ),
    (
        RAW_DIR / "plant_virus_data.csv",
        "input_original/manual_downloads/SPHAK/plant_virus_data.csv",
        "latin1",
    ),
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


def join_unique(values: pd.Series) -> str:
    cleaned = sorted({str(v).strip() for v in values.dropna() if str(v).strip()})
    return "; ".join(cleaned)


def main() -> None:
    current_families = set(pd.read_csv(ICTV_REF)["Current_ICTV_family"].dropna().astype(str))
    frames = []
    for path, rel_path, encoding in FILES:
        if not path.exists():
            raise SystemExit(f"Missing SPHAK input: {path}")
        df = pd.read_csv(path, usecols=["Family"], encoding=encoding, keep_default_na=False)
        df["Family"] = df["Family"].astype(str).str.strip()
        df = df[df["Family"].str.len().gt(0)].copy()
        df["Source_file"] = rel_path
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    unknown = sorted(set(data["Family"]) - current_families)
    if unknown:
        raise SystemExit(f"SPHAK family labels not found in ICTV reference: {unknown}")

    grouped = (
        data.groupby("Family", dropna=False)
        .agg(
            Source_record_count=("Family", "size"),
            Source_file=("Source_file", join_unique),
        )
        .reset_index()
        .rename(columns={"Family": "Current_ICTV_family"})
    )
    grouped.insert(0, "Tool", TOOL)
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Source_label"] = grouped["Current_ICTV_family"]
    grouped["Mapping_method"] = "exact_current_family"
    grouped["Verification_status"] = "confirmed_from_structured_dataset"
    grouped["Notes"] = "Family-level presence inferred from SPHAK protein records and deduplicated to current ICTV families."
    grouped = grouped[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")

    write_table(grouped, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {grouped.shape[0]} current families")


if __name__ == "__main__":
    main()
