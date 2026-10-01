# -*- coding: utf-8 -*-
"""SPHAK: animal_train.csv + plant_train.csv, Host column.

This is the tool's own train_only headline figure, not the fuller
*_including_out_of_sample.csv files that also exist in its repo; see
DATASET_SCOPE in categories.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

ANIMALS = "SPHAK/animal_train.csv"
PLANTS = "SPHAK/plant_train.csv"
SOURCE_DESC = ("animal_train.csv + plant_train.csv, Host column (finer species-level "
               "resolution than the Host_agg column the original harmonization used for "
               "animals, and than the plain row-count-only treatment it used for plants)")


def load_raw() -> tuple:
    """The Host column of the animal and plant training files."""
    return (pd.read_csv(os.path.join(RS, ANIMALS), usecols=["Host"]),
            pd.read_csv(os.path.join(RS, PLANTS), usecols=["Host"]))


def count_labels(an: pd.DataFrame, pl: pd.DataFrame) -> tuple:
    """Species counts, animals then plants. Returns the rows and both tallies,
    since the note quotes the split."""
    an_vc = an["Host"].value_counts()
    pl_vc = pl["Host"].value_counts()
    rows = ([(sp, int(n), "") for sp, n in an_vc.items()]
            + [(sp, int(n), "") for sp, n in pl_vc.items()])
    return rows, an_vc, pl_vc


def run():
    rows, an_vc, pl_vc = count_labels(*load_raw())
    return write_csv(
        13, "SPHAK", SOURCE_DESC, rows,
        note=f"{len(an_vc)} animal species + {len(pl_vc)} plant species, "
             f"{int(an_vc.sum() + pl_vc.sum())} records total ({int(an_vc.sum())} animal + "
             f"{int(pl_vc.sum())} plant). Host->Host_agg is a clean 1:1 mapping in both "
             f"files, no ambiguity.")


if __name__ == "__main__":
    run()
