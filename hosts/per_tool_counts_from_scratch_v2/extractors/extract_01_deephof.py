# -*- coding: utf-8 -*-
"""DeepHoF: 41598_2021_96903_MOESM5_ESM.xlsx, train + test genome sheets.

The Host column is comma-separated multi-tag, so a record can be counted in
more than one class; see the note below and Potential_double_count in
label_categories.csv.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "DeepHoF/41598_2021_96903_MOESM5_ESM.xlsx"
SHEETS = ["train_genome_info", "test_genome_info"]
SOURCE_DESC = ("41598_2021_96903_MOESM5_ESM.xlsx (train_genome_info + test_genome_info "
               "sheets, Host column, 61,684 total genome records)")
NOTE = ("human/non-human vertebrate mutually exclusive (human wins); invertebrate/plant/germ "
        "each counted independently of every other tag (incl. human) -- up to 4 of 5 categories "
        "can include the same record, 5,256 of 61,684 records counted 2-3x. See "
        "Potential_double_count in label_categories.csv. germ is DeepHoF's residual microbial "
        "class (11,529 of 12,020 records are viruses of bacteria or archaea, 491 of fungi, "
        "protists and algae -- see scripts/resolve_germ.py) and is excluded as non-eukaryotic.")


def load_raw() -> pd.Series:
    """The Host column of both sheets, concatenated."""
    sheets = [pd.read_excel(os.path.join(RS, SRC), sheet_name=s, header=1) for s in SHEETS]
    return pd.concat(sheets, ignore_index=True)["Host"].astype(str)


def has_tag(host: pd.Series, tag: str) -> pd.Series:
    """Whether a comma-separated Host field carries this tag exactly."""
    return host.str.split(",").apply(lambda parts: tag in parts)


def count_labels(host: pd.Series) -> list:
    """The five released classes, plus the records carrying no tag at all."""
    return [("human", int(has_tag(host, "human").sum()), "MATCH (32464)"),
            ("non-human vertebrate",
             int((has_tag(host, "vertebrates") & ~has_tag(host, "human")).sum()),
             "MATCH (10245)"),
            ("invertebrate", int(has_tag(host, "invertebrates").sum()), "MATCH (7424)"),
            ("plant", int((has_tag(host, "plant") | has_tag(host, "plants")).sum()),
             "MATCH (4787)"),
            ("germ (microbial hosts, EXCL)", int(has_tag(host, "germ").sum()), "MATCH (12020)"),
            ("- (untagged)", int(host.str.strip().isin(["-", "nan", ""]).sum()),
             "MATCH (9) -- Unknown host, previously silently dropped")]


def run():
    return write_csv(1, "DeepHoF", SOURCE_DESC, count_labels(load_raw()), note=NOTE)


if __name__ == "__main__":
    run()
