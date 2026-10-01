# -*- coding: utf-8 -*-
"""RNAVirHost: virus_label(1).csv, y|host name.

The column is a stringified Python list per record, so a multi-host virus
becomes one row per host. That makes the unit a virus-host association, not a
record; see the note below.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "RNAVirHost/virus_label(1).csv"
SOURCE_DESC = ("virus_label(1).csv (14,500 rows), y|host name column (finer species-level "
               "resolution than the y|L1/y|L2/y|host class columns the original "
               "harmonization used)")


def load_raw() -> pd.DataFrame:
    """The label table as released."""
    return pd.read_csv(os.path.join(RS, SRC))


def count_labels(df: pd.DataFrame) -> tuple:
    """Host species with multi-host records expanded, then the bacterial
    records as one unexpanded excluded row."""
    bacteria_n = int((df["y|L1"] == "Bacteria").sum())
    euk = df[df["y|L1"] != "Bacteria"].copy()
    euk["host_list"] = euk["y|host name"].apply(ast.literal_eval)
    exploded = euk.explode("host_list")
    rows = [(sp, int(n), "") for sp, n in exploded["host_list"].value_counts().items()]
    rows.append(("Bacteria (EXCL)", bacteria_n,
                 "MATCH (44) -- kept as its own unexploded row, unchanged"))
    return rows, len(exploded), len(euk)


def run():
    rows, n_mentions, n_records = count_labels(load_raw())
    return write_csv(
        2, "RNAVirHost", SOURCE_DESC, rows,
        note=f"y|host name lists ALL reported host species per virus record -- ~940/14,500 "
             f"records (6.5%) name more than one host, so this table has {n_mentions} species "
             f"mentions from {n_records} eukaryotic-host records. Counting_unit is "
             f"\"virus-host species association\" (same unit EvoMIL already uses), not "
             f"\"sequence/isolate record\" -- do not sum this column expecting 14,500. "
             f"Bacteria (EXCL, 44 records) kept as its own unexploded row, unchanged.")


if __name__ == "__main__":
    run()
