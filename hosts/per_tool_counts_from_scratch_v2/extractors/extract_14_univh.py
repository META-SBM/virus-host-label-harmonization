# -*- coding: utf-8 -*-
"""UniVH: dataset.csv, deduplicated to a 525-species candidate pool.

The same file carries an unused train/val/test column (77,561/2,633/1,680); see
DATASET_SCOPE in categories.py for why no split filter is applied.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "UniVH/dataset.csv"
SOURCE_DESC = ("dataset.csv (81,874 accession-pair rows), deduped by host.species.name -> "
               "525-species candidate pool; host.order/host.class/host.kingdom columns")
NAMED_MAMMAL_ORDERS = ["Carnivora", "Primates", "Artiodactyla", "Chiroptera", "Rodentia"]
NAMED_CLASSES = ["Mammalia", "Insecta", "Aves", "Actinopteri", "Arachnida", "Lepidosauria"]


def load_raw() -> pd.DataFrame:
    """One row per species, not per accession pair."""
    return pd.read_csv(os.path.join(RS, SRC)).drop_duplicates(subset=["host.species.name"])


def count_labels(sp: pd.DataFrame) -> list:
    """Species counts at the ranks the tool itself reports."""
    mam = sp[sp["host.class"] == "Mammalia"]
    mam_order = mam["host.order"].value_counts()
    other_mam_orders = int(mam_order.sum()) - sum(int(mam_order.get(o, 0))
                                                  for o in NAMED_MAMMAL_ORDERS)
    cls = sp["host.class"].value_counts()
    other_animalia = int(cls.sum()) - sum(int(cls.get(c, 0)) for c in NAMED_CLASSES)
    kingdom = sp["host.kingdom"].value_counts()
    return [("Homo sapiens", 1, "MATCH"),
            ("Primates (excl. human)", int(mam_order.get("Primates", 0)) - 1, "MATCH (18)"),
            ("Chiroptera", int(mam_order.get("Chiroptera", 0)), "MATCH (17)"),
            ("Rodentia", int(mam_order.get("Rodentia", 0)), "MATCH (17)"),
            ("Artiodactyla/Cetartiodactyla", int(mam_order.get("Artiodactyla", 0)), "MATCH (18)"),
            ("Carnivora", int(mam_order.get("Carnivora", 0)), "MATCH (29)"),
            ("Mammalia (other orders)", other_mam_orders, "MATCH (14)"),
            ("Aves", int(cls.get("Aves", 0)), "MATCH (58)"),
            ("fish classes (Actinopteri etc.)", int(cls.get("Actinopteri", 0)), "MATCH (42)"),
            ("Lepidosauria", int(cls.get("Lepidosauria", 0)), "MATCH (2)"),
            ("Insecta", int(cls.get("Insecta", 0)), "MATCH (62)"),
            ("Arachnida", int(cls.get("Arachnida", 0)), "MATCH (14)"),
            ("Animalia (other, no class match)", other_animalia, "MATCH (20)"),
            ("Plantae", int(kingdom.get("Plantae", 0)), "MATCH (113)"),
            ("Fungi", int(kingdom.get("Fungi", 0)), "MATCH (100)")]


def run():
    return write_csv(
        14, "UniVH", SOURCE_DESC, count_labels(load_raw()),
        note="Counting_unit is species, not accession-pair rows -- do not sum this column "
             "expecting 81,874. The dataset.csv file also carries its own 'dataset' column "
             "(train=77,561/val=2,633/test=1,680, unused -- see DATASET_SCOPE).")


if __name__ == "__main__":
    run()
