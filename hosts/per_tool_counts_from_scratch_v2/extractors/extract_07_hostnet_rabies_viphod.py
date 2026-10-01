# -*- coding: utf-8 -*-
"""HostNet (Rabies, VIPHOD): the same source as VIDHOP's Rabies_strict split.

train + test only. Including val breaks the tool's own reported total, which is
checked in the note below.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write_csv
from extract_05_vidhop import load_split

SPLITS = ["train", "test"]
SOURCE_DESC = ("VIDHOP/small_paper_version_Rabies_strict Y_train.csv + Y_test.csv ONLY "
               "(val split excluded -- matches original exactly only when val is excluded; "
               "same underlying source as VIDHOP's own Rabies_strict split)")


def load_raw() -> list:
    """The two splits HostNet reports."""
    return [load_split("Rabies", split) for split in SPLITS]


def count_labels(splits: list) -> tuple:
    """Species summed across train and test, commonest first."""
    c = collections.Counter()
    for dsub in splits:
        c.update(dsub["species"].value_counts().to_dict())
    return [(sp, int(cnt), "") for sp, cnt in c.most_common()], c


def run():
    rows, c = count_labels(load_raw())
    return write_csv(
        7, "HostNet (Rabies, VIPHOD)", SOURCE_DESC, rows,
        note=f"17 species, total {sum(c.values())} -- MATCHES original exactly (11,685) when "
             f"only train+test are summed (adding val gives 12,025, +20 per species, which "
             f"does NOT match -- val is genuinely excluded from HostNet's own reported counts).")


if __name__ == "__main__":
    run()
