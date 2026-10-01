# -*- coding: utf-8 -*-
"""
Orchestrator: runs all 15 per-tool extraction scripts in extractors/ (each one
reads its own raw_sources/<Tool>/ files and writes its own
counts_per_tool_v2/<NN>_<Tool>_counts.csv -- see extractors/common.py and
sources/00_README.md), then assembles 00_manifest.csv from their results.

Each extractor is also independently runnable for debugging a single tool,
e.g. `python3 extractors/extract_11_hostclassifier.py`.

History: this used to be one 476-line script with all 15 tools' logic inline
and dead, session-specific absolute paths -- split into one file per tool
(this session, per explicit request) so each tool's extraction can be run,
read, and tested on its own. Verify the whole thing reproduces the
already-committed counts_per_tool_v2/*.csv exactly with:
    cp -r counts_per_tool_v2 counts_per_tool_v2_BACKUP
    python3 recompute_all.py
    python3 verify_against_committed.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTORS = os.path.join(HERE, "extractors")
OUT = os.path.join(HERE, "counts_per_tool_v2")
sys.path.insert(0, EXTRACTORS)

from extract_01_deephof import run as run_01
from extract_02_rnavirhost import run as run_02
from extract_03_host_taxon_predictor import run as run_03
from extract_04_evomil import run as run_04
from extract_05_vidhop import run as run_05
from extract_06_hostnet_flavivirus import run as run_06
from extract_07_hostnet_rabies_viphod import run as run_07
from extract_08_menb import run as run_08
from extract_09_viralhostpredictor import run as run_09
from extract_10_zoonotic_rank import run as run_10
from extract_11_hostclassifier import run as run_11
from extract_12_virhostpred import run as run_12
from extract_13_sphak import run as run_13
from extract_14_univh import run as run_14
from extract_15_gival import run as run_15
from extract_16_deepacvir import run as run_16
from extract_17_mosvir import run as run_17
from extract_18_vpf_class import run as run_18

EXTRACTORS_IN_ORDER = [run_01, run_02, run_03, run_04, run_05, run_06, run_07,
                        run_08, run_09, run_10, run_11, run_12, run_13, run_14, run_15, run_16, run_17, run_18]


def main():
    manifest = [extractor() for extractor in EXTRACTORS_IN_ORDER]
    with open(os.path.join(OUT, "00_manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "Tool", "File", "Recomputed from", "N labels", "Sum of numeric counts"])
        w.writerows(manifest)
    print("\nDONE ->", OUT)


if __name__ == "__main__":
    main()
