#!/usr/bin/env python3
"""Native raw-file processor for VPF-Class.

The standardized output reports family-level breadth inferred from classified
viral protein family profiles. VPF rows are not interpreted as virus records,
genomes, or virus-host observations.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_table  # noqa: E402


BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE / "data"
RAW_DIR = PROJECT / "input_original" / "manual_downloads" / "VPF_Class"
FAMTAX = RAW_DIR / "2019_VPF_FamTax_REclassification_new.tsv"
GENTAX = RAW_DIR / "2019_VPF_GenTax_REclassification_new.tsv"
ICTV_REF = PROJECT / "intermediate" / "ictv_family_reference.csv"
VMR = PROJECT / "input_original" / "manual_downloads" / "ICTV_VMR" / "VMR_MSL41.v1.20260721.xlsx"
OUTPUT = BASE / "outputs" / "tools" / "VPF-Class.csv"

TOOL = "VPF-Class"
SOURCE_UNIT = "V"
FAMTAX_SOURCE = "input_original/manual_downloads/VPF_Class/2019_VPF_FamTax_REclassification_new.tsv"
GENTAX_SOURCE = "input_original/manual_downloads/VPF_Class/2019_VPF_GenTax_REclassification_new.tsv"

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


def read_vpf_tsv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", keep_default_na=False)
    expected = {"VPF", "classification", "percentage", "category"}
    missing = expected - set(df.columns)
    if missing:
        raise SystemExit(f"{path} lacks required columns: {sorted(missing)}")
    df["VPF"] = df["VPF"].astype(str)
    df["classification"] = df["classification"].astype(str).str.strip()
    return df


def join_unique(values: pd.Series) -> str:
    cleaned = sorted({str(v).strip() for v in values.dropna() if str(v).strip()})
    return "; ".join(cleaned)


def source_files_for_rows(values: pd.Series) -> str:
    levels = {str(v).strip() for v in values.dropna() if str(v).strip()}
    files = []
    if "family" in levels:
        files.append(FAMTAX_SOURCE)
    if "genus" in levels:
        files.append(GENTAX_SOURCE)
    return "; ".join(files)


def build_genus_to_family() -> dict[str, str]:
    vmr = pd.read_excel(VMR, sheet_name="VMR MSL41", usecols=["Family", "Genus"])
    vmr["Family"] = vmr["Family"].fillna("").astype(str).str.strip()
    vmr["Genus"] = vmr["Genus"].fillna("").astype(str).str.strip()
    vmr = vmr[(vmr["Family"] != "") & (vmr["Genus"] != "")]
    grouped = vmr.groupby("Genus")["Family"].agg(lambda s: sorted(set(s))).reset_index()
    unique = grouped[grouped["Family"].apply(len).eq(1)].copy()
    return dict(zip(unique["Genus"], unique["Family"].str[0]))


def main() -> None:
    for path in [FAMTAX, GENTAX, ICTV_REF, VMR]:
        if not path.exists():
            raise SystemExit(f"Missing required input: {path}")

    ictv = pd.read_csv(ICTV_REF)
    current_families = set(ictv["Current_ICTV_family"].dropna().astype(str))

    # Conservative direct successor mapping. Split historical families are not
    # forced into one current family.
    manual_family_map = {
        "Polydnaviridae": "Polydnaviriformidae",
    }

    fam = read_vpf_tsv(FAMTAX)
    fam["Current_ICTV_family"] = fam["classification"].map(
        lambda label: label if label in current_families else manual_family_map.get(label)
    )
    fam["Mapping_method"] = fam.apply(
        lambda row: (
            "exact_current_family_or_family_level_taxon"
            if row["classification"] in current_families
            else "manual_direct_successor_family_level_taxon"
            if row["classification"] in manual_family_map
            else "unresolved_or_split_historical_family"
        ),
        axis=1,
    )
    fam["Source_taxonomic_level"] = "family"

    genus_to_family = build_genus_to_family()
    gen = read_vpf_tsv(GENTAX)
    gen["Current_ICTV_family"] = gen["classification"].map(genus_to_family)
    gen["Mapping_method"] = gen["Current_ICTV_family"].map(
        lambda value: "exact_current_genus_unique_family" if isinstance(value, str) and value else "unresolved_genus_label_not_in_current_msl41_v1"
    )
    gen["Source_taxonomic_level"] = "genus"

    combined = pd.concat([fam, gen], ignore_index=True)
    combined = combined[
        combined["Current_ICTV_family"].notna()
        & combined["Current_ICTV_family"].astype(str).str.len().gt(0)
    ].copy()

    grouped = (
        combined.groupby("Current_ICTV_family", dropna=False)
        .agg(
            Source_record_count=("VPF", "nunique"),
            Source_file=("Source_taxonomic_level", source_files_for_rows),
            Source_label=("classification", join_unique),
            Mapping_method=("Mapping_method", join_unique),
        )
        .reset_index()
    )
    grouped.insert(0, "Tool", TOOL)
    grouped["Source_unit"] = SOURCE_UNIT
    grouped["Verification_status"] = "confirmed_profile_level_source_not_record_level"
    grouped["Notes"] = (
        "Family-level presence inferred from classified VPF profiles; "
        "percentages and categories remain in raw VPF-Class files; "
        "VPF rows are not viruses, genomes, or virus-host observations."
    )
    grouped = grouped[REQUIRED_COLUMNS].sort_values("Current_ICTV_family")

    write_table(grouped, OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(BASE)}: {grouped.shape[0]} current family-level taxa")


if __name__ == "__main__":
    main()
