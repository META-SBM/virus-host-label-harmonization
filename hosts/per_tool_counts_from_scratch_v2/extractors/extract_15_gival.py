# -*- coding: utf-8 -*-
"""GIVAL: df_AIV_before_sample.csv, host column plus the host token in record_id.

The host column leaves 1,199 rows as "Mammal"; influenza strain names carry the
host in record_id, so those rows resolve further.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "GIVAL/df_AIV_before_sample.csv"
SOURCE_DESC = "df_AIV_before_sample.csv (121,753 sequences), host column"
# host_token (lowercased, underscores normalized to spaces) -> canonical label.
SYNONYMS = {
    "red fox": "Fox", "fox": "Fox", "ezo red fox": "Fox", "vulpes vulpes": "Fox",
    "mink": "Mink", "wild mink": "Mink",
    "canine": "Canine", "equine": "Equine", "feline": "Feline", "ferret": "Ferret",
    "tiger": "Tiger", "raccoon dog": "Raccoon dog", "skunk": "Skunk", "striped skunk": "Skunk",
    "donkey": "Donkey", "polecat": "Polecat", "mustela putorius": "Polecat", "lion": "Lion",
    "virginia opossum": "Virginia opossum", "owston's_civet": "Owston's civet", "owston's civet": "Owston's civet",
    "badger": "Badger", "bear": "Bear", "bobcat": "Bobcat", "otter": "Otter",
    "bottlenose dolphin": "Bottlenose dolphin", "raccoon": "Raccoon", "cat": "Feline",
}


def load_raw() -> pd.DataFrame:
    """The host column and the strain identifier."""
    return pd.read_csv(os.path.join(RS, SRC), usecols=["host", "record_id"])


def count_labels(gv: pd.DataFrame) -> tuple:
    """The four released classes, the three the article groups post hoc with no
    count, then the species parsed out of the mammal rows."""
    gv_vc = gv["host"].value_counts()
    mam = gv[gv["host"] == "Mammal"].copy()
    mam["host_token"] = mam["record_id"].str.split("/").str[1].str.strip()
    mam["species"] = (mam["host_token"].str.lower().str.replace("_", " ", regex=False)
                      .map(SYNONYMS).fillna(mam["host_token"]))
    rows = [
        ("Human", int(gv_vc.get("Human", 0)), "MATCH (53942)"),
        ("Avian", int(gv_vc.get("Avian", 0)), "MATCH (48905)"),
        ("Swine", int(gv_vc.get("Swine", 0)), "MATCH (17486)"),
        ("Unknown (EXCL)", int(gv_vc.get("Unknown", 0)), "MATCH (221)"),
        ("Primates (PRI) -- CoV post-hoc grouping", "nan", "not present in this file, no released count (as originally documented)"),
        ("Chiroptera (CHI) -- CoV post-hoc grouping", "nan", "not present in this file, no released count (as originally documented)"),
        ("Suiformes/Artiodactyla -- CoV post-hoc grouping", "nan", "not present in this file, no released count (as originally documented)"),
    ]
    rows += [(sp, int(n), "") for sp, n in mam["species"].value_counts().items()]
    return rows, int(gv_vc.get("Mammal", 0))


def run():
    rows, mammal_n = count_labels(load_raw())
    return write_csv(
        15, "GIVAL", SOURCE_DESC, rows,
        note=f"'Mammal (unspecified)' ({mammal_n} records) further resolved by parsing the "
             f"host token out of record_id (A/<host>/<location>/<strain>/<year>, standard "
             f"influenza strain naming) -- the df_AIV_before_sample.csv host column itself "
             f"has no finer resolution, but record_id does. Canine/Equine match the committed "
             f"counts_per_tool_v2 file exactly.")


if __name__ == "__main__":
    run()
