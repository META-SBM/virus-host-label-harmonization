# -*- coding: utf-8 -*-
"""DeePaC-vir. VHDB_1_folds_{human,all_nhuman}.rds (Zenodo 10.5281/zenodo.4312525).
"""
import os
import subprocess
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

import pandas as pd

# RENV first, then whatever is on PATH.
R_CANDIDATES = tuple(
    p for p in (os.path.join(os.environ["RENV"], "bin", "Rscript")
                if os.environ.get("RENV") else None,
                "Rscript") if p)

R_SCRIPT = """
h <- readRDS(file.path(%(dir)r, "VHDB_1_folds_human.rds"))
n <- readRDS(file.path(%(dir)r, "VHDB_1_folds_all_nhuman.rds"))
both <- rbind(h, n)
write.csv(both[, c("host.name", "host.lineage", "virus.lineage", "fold1")],
          %(out)r, row.names = FALSE, na = "")
"""


def rscript() -> str:
    for cand in R_CANDIDATES:
        from shutil import which
        path = which(cand) if os.sep not in cand else (cand if os.path.exists(cand) else None)
        if path:
            return path
    raise SystemExit("Rscript not found; DeePaC-vir's released labels are .rds files. "
                     "See environment-R.yml.")


def load_raw() -> pd.DataFrame:
    """The two .rds tables, dumped to CSV by R and read back."""
    src = f"{RS}/DeePaC_vir"
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "vhdb.csv")
        script = os.path.join(tmp, "dump.R")
        with open(script, "w") as fh:
            fh.write(R_SCRIPT % {"dir": src, "out": out})
        subprocess.run([rscript(), script], check=True, capture_output=True)
        return pd.read_csv(out, dtype=str, keep_default_na=False)


def count_labels(df: pd.DataFrame) -> list:
    """One row per host name. The record count is asserted here: a changed
    input must fail loudly rather than produce different numbers."""
    if len(df) != 9496:
        raise SystemExit(f"expected the 9,496 viruses the study reports, read {len(df)}")
    counts = df["host.name"].value_counts()
    # Sorted by count, then by name: value_counts leaves ties in an order
    # that depends on the pandas version, which the byte-for-byte check
    # against the committed file would otherwise inherit.
    order = sorted(counts.items(), key=lambda kv: (-int(kv[1]), str(kv[0])))
    return [(host, int(n), "") for host, n in order]


def run():
    rows = count_labels(load_raw())
    return write_csv(
        16, "DeePaC-vir",
        "VHDB_1_folds_human.rds + VHDB_1_folds_all_nhuman.rds (Zenodo 10.5281/zenodo.4312525), "
        "host.name column, 9,496 Virus-Host DB records (1,309 human, 8,187 non-human)",
        rows,
        note=("Species-level host names released under a binary human/non-human model, as "
              "HostClassifier also does. The nested eukarya/metazoa/chordata negative sets in the "
              "same deposit are subsets of all_nhuman and are not read, to avoid counting the same "
              "virus more than once. The study's own train/val/test split (fold1) is combined, as "
              "for every other tool with a released split. Not matched against "
              "original_reported_labels.xlsx: this tool entered the review through citation "
              "searching, after that workbook was curated."))


if __name__ == "__main__":
    run()
