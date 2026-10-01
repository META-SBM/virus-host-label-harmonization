# -*- coding: utf-8 -*-
"""MosViR, mosquito_500.fasta.xz + arboviruses_500bp.fasta.xz (Zenodo 10.5281/zenodo.10975789).
"""
import lzma
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

FRAGMENT_SUFFIX = re.compile(r"_\d+$")

CLASSES = [
    ("mosquito-specific virus", "mosquito_500.fasta.xz"),
    ("arbovirus", "arboviruses_500bp.fasta.xz"),
]


def source_sequences(path: str) -> int:
    """Fragments collapsed back to the sequences they were cut from."""
    seen = set()
    with lzma.open(path, "rt", errors="replace") as fh:
        for line in fh:
            if line.startswith(">"):
                seen.add(FRAGMENT_SUFFIX.sub("", line.strip().lstrip(">")))
    return len(seen)


def load_raw() -> dict:
    """Source-sequence counts per released class. The sequences themselves are
    not needed: the label is the file a sequence is in."""
    return {label: source_sequences(f"{RS}/MosViR/{fname}") for label, fname in CLASSES}


def count_labels(counts: dict) -> list:
    """One row per class, in the released order. The totals are asserted here:
    a changed input must fail loudly rather than produce different numbers."""
    if counts != {"mosquito-specific virus": 2391, "arbovirus": 24611}:
        raise SystemExit(f"source-sequence counts moved: {counts}")
    return [(label, counts[label], "") for label, _ in CLASSES]


def run():
    rows = count_labels(load_raw())
    return write_csv(
        17, "MosViR",
        "mosquito_500.fasta.xz + arboviruses_500bp.fasta.xz (Zenodo 10.5281/zenodo.10975789), "
        "500 bp fragments collapsed to 27,002 source sequences",
        rows,
        note=("Host-range classes, not host taxa: a mosquito-specific virus replicates only in "
              "mosquito cells, an arbovirus in the mosquito vector and a vertebrate host. The 500 bp "
              "set is used because a short sequence appears in no longer fragment set, and fragments "
              "are collapsed to their source sequence. The third released class, `other viruses` "
              "(620,553 source sequences), is the not-mosquito-associated background for the first "
              "classification step; it is not counted, because it asserts no host and its accessions "
              "cannot be resolved to check it against the review's eukaryotic scope. Identifiers "
              "throughout the release are truncated accessions, so these records carry no resolvable "
              "viral taxonomy. Not matched against original_reported_labels.xlsx: this tool entered "
              "the review through citation searching, after that workbook was curated."))


if __name__ == "__main__":
    run()
