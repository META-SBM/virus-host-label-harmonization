# -*- coding: utf-8 -*-
"""ViralHostPredictor: BabayanEtAl_VirusData.csv, Reservoir + Vector columns."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

SRC = "ViralHostPredictor/BabayanEtAl_VirusData.csv"
SOURCE_DESC = "BabayanEtAl_VirusData.csv (536 rows), Reservoir + Vector columns"
RESERVOIR_LABELS = ["Rodent", "Primate", "Pterobat", "Vespbat", "Artiodactyl", "Carnivore", "Galloanserae", "Neoaves",
                     "Fish", "Insect", "Plant", "Reptile", "Lagomorph", "Perissodactyla", "Scandentia", "Diprotodontia",
                     "Cetacean", "Soricomorph", "Erinaceidae", "Macropod", "Orphan"]
VECTOR_LABELS = ["mosquito", "tick", "sandfly", "midge", "thrip", "leafhopper", "planthopper", "fruit fly",
                  "aphid", "louse", "cimicid", "lepidoptera", "unknown"]


def load_raw() -> pd.DataFrame:
    """The host and vector axes of the Babayan table."""
    return pd.read_csv(os.path.join(RS, SRC),
                       usecols=["Reservoir", "Vector-borne", "Vector"], low_memory=False)


def count_labels(bab: pd.DataFrame) -> list:
    """Reservoir labels, the unlabelled reservoir rows, then vector labels."""
    res = bab["Reservoir"].value_counts(dropna=False)
    vec = bab["Vector"].value_counts(dropna=False)
    rows = [(f"{label} (reservoir)", int(res.get(label, 0)), "MATCH")
            for label in RESERVOIR_LABELS]
    rows.append(("NA (reservoir, EXCL)", int(bab["Reservoir"].isna().sum()), "MATCH (2)"))
    rows += [(f"{label} (vector)", int(vec.get(label, 0)), "MATCH") for label in VECTOR_LABELS]
    return rows


def run():
    return write_csv(9, "ViralHostPredictor", SOURCE_DESC, count_labels(load_raw()))


if __name__ == "__main__":
    run()
