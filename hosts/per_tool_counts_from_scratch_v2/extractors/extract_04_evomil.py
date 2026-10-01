# -*- coding: utf-8 -*-
"""EvoMIL: Supplementary Table S2.

The released file uses strict-OOXML conformance, which openpyxl cannot read;
raw_sources/EvoMIL/ holds a LibreOffice-converted copy, and the original is not
kept anywhere in this project.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "EvoMIL/journal.pcbi.1012597.s002_converted.xlsx"
SHEET = "Table_S2"
SOURCE_DESC = (f"journal.pcbi.1012597.s002_converted.xlsx, sheet {SHEET} (36 host rows, "
               "Number of viruses column)")
ANIMALS = ["Homo sapiens", "Chlorocebus aethiops", "Macaca mulatta", "Pan troglodytes", "Mus musculus",
           "Rattus norvegicus", "Mesocricetus auratus", "Sus scrofa", "Bos taurus", "Ovis aries", "Capra hircus",
           "Canis lupus", "Felis catus", "Equus caballus", "Gallus gallus", "Anas platyrhynchos", "Aedes albopictus"]


def load_raw() -> pd.DataFrame:
    """Table S2 as published."""
    return pd.read_excel(os.path.join(RS, SRC), sheet_name=SHEET, header=0)


def count_labels(s2: pd.DataFrame) -> list:
    """The named animals one row each, every remaining host pooled as plants."""
    rows = []
    for a in ANIMALS:
        v = s2.loc[s2["Host name"] == a, "Number of viruses"]
        rows.append((a, int(v.iloc[0]) if len(v) else 0, "MATCH"))
    plant_mask = ~s2["Host name"].isin(ANIMALS)
    rows.append(("19 plant species (pooled)",
                 int(s2.loc[plant_mask, "Number of viruses"].sum()), "MATCH (1187)"))
    return rows


def run():
    return write_csv(
        4, "EvoMIL", SOURCE_DESC, count_labels(load_raw()),
        note="File uses strict-OOXML conformance which openpyxl/pandas can't read directly; "
             "the version in raw_sources/EvoMIL/ was already converted via LibreOffice headless.")


if __name__ == "__main__":
    run()
