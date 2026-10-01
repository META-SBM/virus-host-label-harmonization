# -*- coding: utf-8 -*-
"""MENB: msaf127_supplementary_data.pdf, Supplementary Figure 1A.

Train counts only, which is what the article headlines as its dataset. The
figure is a rendered table, not machine-parseable, so it is transcribed below
rather than read at run time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write_csv

HOSTS = ["Human", "Avian", "Swine"]
SOURCE_DESC = ("msaf127_supplementary_data.pdf, Supplementary Figure 1A (per-strain "
               "train/test table, transcribed from rendered PDF page 3) -- TRAIN counts "
               "only, this IS what the article itself headlines as its dataset")
CELL_NOTE = ("Per-strain composition table (Suppl. Fig. 1A) sums to exactly 300 train "
             "sequences per host per viral family x 4 families")

# Transcribed from raw_sources/MENB/msaf127_supplementary_data.pdf, page 3:
# (strain, train_n, test_n) per host per viral family.
FIG1A = dict(
    Corona=dict(
        Human=[('MERS-CoV', 115, 51), ('SARS-CoV2', 8, 10), ('HCoV-NL63', 34, 23), ('HCoV-OC43', 109, 48), ('HCoV-HKU1', 11, 8), ('HCoV-229E', 17, 7), ('PDCoV', 3, 1), ('CoV-EMC-2C', 1, 1), ('BCoV-EN1', 2, 0), ('HECoV-4408', 0, 1)],
        Avian=[('IBV', 279, 137), ('Avian CoV', 20, 11), ('Duck CoV', 1, 2)],
        Swine=[('PEDV', 217, 106), ('PDCoV', 59, 36), ('PHEV', 7, 3), ('SeCoV', 2, 0), ('TGEV', 13, 4), ('PRCV', 1, 0), ('PToV', 1, 1)],
    ),
    Flavi=dict(
        Human=[('DENV-1', 64, 40), ('DENV-2', 65, 24), ('DENV-3', 46, 27), ('DENV-4', 18, 10), ('HCV', 71, 32), ('YFV', 5, 3), ('ZIKV', 19, 9), ('HPgV', 7, 1), ('WESSV', 1, 0), ('AHFV', 1, 0), ('WNV', 3, 1), ('TBEV', 0, 2), ('POWV', 0, 1)],
        Avian=[('WNV', 40, 19), ('DEDSV', 9, 9), ('TMUV', 234, 103), ('DHV', 5, 7), ('ITV', 3, 0), ('Duck flavivirus TA', 2, 1), ('USUV', 1, 2), ('HPgV-1', 2, 1), ('BYDV', 1, 2), ('Flavivirus muscovy', 1, 2), ('MDRV', 1, 2), ('HPgV-2', 1, 2)],
        Swine=[('CSF', 147, 77), ('JEV', 63, 29), ('BDV', 3, 3), ('APPV', 68, 35), ('PPgV', 13, 4), ('BVDV-2', 2, 1), ('LindaV', 4, 1)],
    ),
    Picorna=dict(
        Human=[('EVs', 96, 48), ('Coxsackievirus', 72, 40), ('Human poliovirus', 18, 10), ('HRVs', 88, 37), ('ECHO', 14, 6), ('PeVs', 9, 3), ('AiV', 1, 3), ('Cosavirus', 2, 1), ('Cardiovirus', 0, 0), ('Saffold virus', 0, 1)],
        Avian=[('Avihepatovirus', 16, 12), ('Avisivirus', 3, 5), ('Megrivirus', 40, 20), ('DVH', 153, 74), ('Anativirus', 13, 4), ('TVH', 4, 2), ('Pigeon mesivirus', 3, 0), ('Pigeon picornavirus', 2, 0), ('AEV', 3, 2), ('Orivirus', 6, 0), ('ChPV', 11, 4), ('Sicinivirus', 33, 18), ('Goose picornavirus', 7, 4), ('Melegrivirus', 3, 0), ('Gallivirus', 3, 3), ('Duck picornavirus', 0, 2)],
        Swine=[('FMDV', 33, 11), ('EVs', 58, 28), ('PKoV', 55, 33), ('Porcine teschovirus', 13, 3), ('PSV', 36, 28), ('EMCV', 7, 6), ('SVV', 97, 40), ('Pasivirus', 1, 1), ('SVD', 0, 11)],
    ),
    Orthomyxo=dict(
        Human=[('1990-1999', 173, 66), ('1980-1989', 41, 28), ('1970-1979', 38, 39), ('1960-1969', 19, 9), ('1950-1959', 16, 5), ('1940-1949', 3, 1), ('1930-1939', 10, 2)],
        Avian=[('1990-1999', 116, 63), ('1980-1989', 98, 41), ('1970-1979', 67, 32), ('1960-1969', 5, 8), ('1950-1959', 10, 6), ('1940-1949', 0, 0), ('1930-1939', 4, 0)],
        Swine=[('1990-1999', 54, 23), ('1980-1989', 62, 40), ('1970-1979', 172, 81), ('1960-1969', 4, 4), ('1950-1959', 2, 0), ('1940-1949', 2, 0), ('1930-1939', 4, 2)],
    ),
)


def load_raw() -> dict:
    """The transcribed table. The PDF is not machine-parseable, so the
    transcription is the source and this returns it unchanged."""
    return FIG1A


def count_labels(fig1a: dict) -> list:
    """Train sequences per host, summed over strains and viral families."""
    return [(f"{host} (train, x4 families)",
             sum(sum(x[1] for x in fam[host]) for fam in fig1a.values()),
             CELL_NOTE)
            for host in HOSTS]


def run():
    return write_csv(
        8, "MENB", SOURCE_DESC, count_labels(load_raw()),
        note=("Re-derived from the article's OWN supplementary dataset-composition figure. "
              "Every host-family cell in Suppl. Fig. 1A sums to exactly 300 "
              "training sequences; x4 families = 1200 train sequences per host, identical "
              "for Human/Avian/Swine."))


if __name__ == "__main__":
    run()
