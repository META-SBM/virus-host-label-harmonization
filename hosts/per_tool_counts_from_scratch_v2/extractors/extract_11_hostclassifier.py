# -*- coding: utf-8 -*-
"""HostClassifier: virus-host-datasets_v4.5.0.csv, standardized_host column.

standardized_host resolves 1,230 species where host_category has 11 buckets.
The coarser column is still used for the 972 rows whose standardized_host is
null, and 166 more rows are null in both.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "HostClassifier/virus-host-datasets_v4.5.0.csv"
SOURCE_DESC = ("virus-host-datasets_v4.5.0.csv (58,055 rows), standardized_host column "
               "(finer species-level resolution than the host_category column the original "
               "harmonization used)")


def load_raw() -> pd.DataFrame:
    """The two host columns, whitespace stripped from the finer one."""
    df = pd.read_csv(os.path.join(RS, SRC), usecols=["standardized_host", "host_category"])
    df["standardized_host"] = df["standardized_host"].str.strip()
    return df


def count_labels(hc_df: pd.DataFrame) -> list:
    """Species first, then the coarse buckets standing in for the rows that
    have no species."""
    rows = [(sp, int(n), "") for sp, n in hc_df["standardized_host"].value_counts().items()]
    fallback = hc_df.loc[hc_df["standardized_host"].isna(), "host_category"]
    for cat, n in fallback.value_counts(dropna=False).items():
        if pd.isna(cat):
            rows.append(("blank (host not recorded)", int(n), "MATCH (166)"))
        else:
            rows.append((f"{cat} (species not recorded)", int(n), ""))
    return rows


def run():
    return write_csv(
        11, "HostClassifier", SOURCE_DESC, count_labels(load_raw()),
        note="host_category is still used to bucket the 972 rows where standardized_host "
             "itself is null, and to set each species's default Detailed_scheme -- see "
             "build_master_labels.py curated tables.")


if __name__ == "__main__":
    run()
