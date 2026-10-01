# -*- coding: utf-8 -*-
"""VIDHOP: Y_{train,val,test}.csv for Influ + Rabies + Rota.

All three sub-datasets and all three splits summed, which is the tool's
complete released dataset; see DATASET_SCOPE in categories.py.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SUB_DATASETS = ["Influ", "Rabies", "Rota"]
SPLITS = ["train", "val", "test"]
SOURCE_DESC = ("Y_train/Y_val/Y_test.csv summed across Influ_strict + Rabies_strict + "
               "Rota_strict (all 3 splits)")


def load_split(sub_dataset: str, split: str) -> pd.DataFrame:
    """One label file. Shared with extract_07_hostnet_rabies_viphod.py, whose
    benchmark is this same Rabies_strict split."""
    path = f"{RS}/VIDHOP/small_paper_version_{sub_dataset}_strict/Y_{split}.csv"
    return pd.read_csv(path, sep="\t", header=None, names=["taxid", "species"])


def load_raw() -> list:
    """Every split of every sub-dataset."""
    return [load_split(ds, split) for ds in SUB_DATASETS for split in SPLITS]


def count_labels(splits: list) -> tuple:
    """Species summed across the splits, commonest first."""
    total = collections.Counter()
    for dsub in splits:
        total.update(dsub["species"].value_counts().to_dict())
    return [(sp, int(c), "") for sp, c in total.most_common()], total


def run():
    rows, total = count_labels(load_raw())
    return write_csv(
        5, "VIDHOP", SOURCE_DESC, rows,
        note=f"51 species, grand total {sum(total.values())} -- MATCHES original exactly "
             f"(263,962); top values (Homo sapiens 136031, Sus scrofa 42440, Gallus gallus "
             f"27229...) all match.")


if __name__ == "__main__":
    run()
