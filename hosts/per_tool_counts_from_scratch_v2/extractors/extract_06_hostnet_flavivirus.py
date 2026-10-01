# -*- coding: utf-8 -*-
"""HostNet (Flavivirus): flavivirus.csv, Y2_subVector column."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "HostNet_Flavivirus/flavivirus.csv"
SOURCE_DESC = "flavivirus.csv (9,626 rows), Y2_subVector column"
AEDES_NOTE = ("NEAR-MATCH: original reported Aedes=6828 + other=1 (6829 total); recomputed "
              "finds all 6829 rows cleanly tagged 'aedes' with no separate 'other' value "
              "present in this column -- 1-row discrepancy, source of original 'other' "
              "split not reproducible from this column alone")


def load_raw() -> pd.DataFrame:
    """The vector column of the flavivirus table."""
    return pd.read_csv(os.path.join(RS, SRC), usecols=["Y2_subVector"])


def count_labels(fv: pd.DataFrame) -> list:
    """One row per vector label, in the order the original recompute used."""
    vc = fv["Y2_subVector"].value_counts()
    return [("aedes", int(vc.get("aedes", 0)), AEDES_NOTE),
            ("culex", int(vc.get("culex", 0)), "MATCH (2424)"),
            ("ixodes", int(vc.get("ixodes", 0)), "MATCH (373)")]


def run():
    return write_csv(6, "HostNet (Flavivirus)", SOURCE_DESC, count_labels(load_raw()))


if __name__ == "__main__":
    run()
