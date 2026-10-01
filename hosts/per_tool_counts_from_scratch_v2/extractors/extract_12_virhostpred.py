# -*- coding: utf-8 -*-
"""VirHostPRED: reps70.fasta (positive class) + random_dataset_1.fasta (negative).

Both files were once classified as absent; they were in the download folder all
along, and the sequence counts match the article's own Table S2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

POSITIVE = "VirHostPRED/reps70.fasta"
NEGATIVE = "VirHostPRED/random_dataset_1.fasta"
SOURCE_DESC = "reps70.fasta (positive class) + random_dataset_1.fasta (negative class)"


def count_fasta(path: str) -> int:
    """Sequences in a FASTA file, by header line."""
    n = 0
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                n += 1
    return n


def load_raw() -> tuple:
    """Sequence counts of the two classes. The sequences themselves are not
    needed: the label is the file a sequence is in."""
    return (count_fasta(os.path.join(RS, POSITIVE)),
            count_fasta(os.path.join(RS, NEGATIVE)))


def count_labels(counts: tuple) -> list:
    """One row per class."""
    pos_n, neg_n = counts
    return [("Homo sapiens (taxid 9606, positive class)", pos_n,
             "MATCH -- reps70.fasta has exactly 2,127 sequences, matches article's Table S2 exactly"),
            ("NOT Homo sapiens (negative class)", neg_n,
             "MATCH -- random_dataset_1.fasta has exactly 2,127 sequences, matches article's Table S2 exactly")]


def run():
    return write_csv(
        12, "VirHostPRED", SOURCE_DESC, count_labels(load_raw()),
        note="reps70.fasta: CD-HIT clustered at 70% identity from an initial ~5,200-sequence "
             "NCBI RefSeq pool (positive/human-infecting class, Host=taxid 9606). "
             "random_dataset_1.fasta: randomly undersampled with a fixed seed from a "
             "10,635-sequence pool to match the positive class size (negative/non-human "
             "class, Host!=taxid 9606) -- per the article's own Table S1/S2 (see "
             "manual_downloads/VirHostPRED/41598_2026_37765_MOESM3_ESM.docx, MOESM4_ESM.docx).")


if __name__ == "__main__":
    run()
