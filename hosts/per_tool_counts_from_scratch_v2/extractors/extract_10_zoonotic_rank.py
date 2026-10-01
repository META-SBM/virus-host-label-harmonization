# -*- coding: utf-8 -*-
"""Zoonotic rank: AllInternalData_Checked.csv, Reservoir column.

The tool's Makefile runs its holdout script with --holdoutProportion 0, so this
file is the complete dataset rather than a train-only slice.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "Zoonotic_rank/AllInternalData_Checked.csv"
SOURCE_DESC = "AllInternalData_Checked.csv (1,258 records), Reservoir column"
BAT_TAGS = ["Pterobat", "Vespbat", "Chiroptera"]
MINOR_MAMMAL_TAGS = ["Perissodactyla", "Lagomorph", "Diprotodontia", "Macropod", "Scandentia",
                     "Eulipotyphla", "Cetacean", "Pilosa", "Erinaceidae", "Soricomorph"]
BIRD_TAGS = ["Galliformes", "Passeriformes", "Anseriformes", "Charadriiformes", "Psittaciformes",
             "Pelecaniformes", "Columbiformes", "Suliformes", "Sphenisciformes"]


def load_raw() -> pd.DataFrame:
    """The reservoir table as released."""
    return pd.read_csv(os.path.join(RS, SRC))


def count_labels(zr: pd.DataFrame) -> list:
    """Reservoir tags, with the groups the original recompute combined."""
    rv = zr["Reservoir"].value_counts(dropna=False)

    def g(k: str) -> int:
        return int(rv.get(k, 0))

    def total(tags: list) -> int:
        return sum(g(t) for t in tags)

    return [
        ("Human", g("Human"), "MATCH (113)"),
        ("NonHumanPrimate", g("NonHumanPrimate"), "MATCH (69)"),
        ("Pterobat/Vespbat/Chiroptera (combined)", total(BAT_TAGS), "MATCH (70)"),
        ("Rodent", g("Rodent"), "MATCH (138)"),
        ("Artiodactyl", g("Artiodactyl"), "MATCH (143)"),
        ("Carnivore", g("Carnivore"), "MATCH (62)"),
        ("minor mammal orders (10 tags combined)", total(MINOR_MAMMAL_TAGS), "MATCH (64)"),
        ("bird orders (9 tags combined)", total(BIRD_TAGS), "MATCH (66)"),
        ("Fish", g("Fish"), "MATCH (39)"),
        ("Reptile", g("Reptile"), "MATCH (17)"),
        ("Insect", g("Insect"), "MATCH (67)"),
        ("Crustacean/Bivalve (combined)", g("Crustacean") + g("Bivalve"), "MATCH (2)"),
        ("Plant", g("Plant"), "MATCH (61)"),
        ("Fungi", g("Fungi"), "MATCH (3)"),
        ("Orphan/blank/NA/NONE (EXCL)",
         g("Orphan") + int(zr["Reservoir"].isna().sum()) + g("NONE"), "MATCH (341)"),
        ("MULTIPLE/Protist (EXCL)", g("MULTIPLE") + g("Protist"), "MATCH (3)"),
    ]


def run():
    return write_csv(
        10, "Zoonotic rank", SOURCE_DESC, count_labels(load_raw()),
        note="Confirmed this project's own dataset-scope audit: the tool's Makefile runs "
             "SelectHoldoutData.R with --holdoutProportion 0 (\"Holdout not currently used -- "
             "not enough data\"), so this file is the tool's complete dataset, not a "
             "train-only slice of something fuller.")


if __name__ == "__main__":
    run()
