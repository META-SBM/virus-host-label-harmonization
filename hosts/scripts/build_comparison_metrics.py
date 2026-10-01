# -*- coding: utf-8 -*-
"""Cross-tool host-comparison metrics, computed on top of master_labels.csv.

    python3 build_comparison_metrics.py
"""
import math
import os

import numpy as np
import pandas as pd

from categories import CATS, DETAILED_SCHEME_REMAP, dataset_instances, dataset_sizes

SC = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(SC, "master_labels.csv")
OUT = os.path.join(SC, "comparison_metrics.csv")

TOOLS = dataset_instances()
TOTAL_DATASET_SIZE = {t: n for t, (n, _u) in dataset_sizes().items()}
CAT_LABELS = [c[0] for c in CATS]

NA_REASON = {
    "ViralHostPredictor": "Humans merged into 'Primates' (order-level)",
    "HostNet (Flavivirus)": "Vector-only tool -- no host axis",
}

# Companion metric: Primate-dominance fraction = (Humans + Non-human primates +
# any tool's own combined "Humans + non-human primates" bucket) / total.
PRIMATE_CATS = ["Humans", "Non-human primates", "Humans + non-human primates"]
PRIMATE_NA_REASON = {
    "HostNet (Flavivirus)": "Vector-only tool -- no host axis",
}

# Source-verified correction: re-auditing VirHostPRED's raw source files
# (random_dataset_1.fasta / reps70.fasta) plus its supplementary tables
# (MOESM3/MOESM4) confirmed the
CONTAMINATION_ADJUSTMENTS = {
    "VirHostPRED": dict(
        adjusted_human_count=2127 - 235,
        reason="excludes 235 bacteriophage records (141 Staphylococcus phage 6ec + 94 IAS virus/Crassvirales) confirmed via raw FASTA headers + NCBI taxonomy; not caught by the source paper's own QC",
    ),
}



def load_data() -> pd.DataFrame:
    """master_labels.csv with the display remap already applied."""
    master = pd.read_csv(MASTER)
    master["Detailed_scheme"] = master["Detailed_scheme"].replace(DETAILED_SCHEME_REMAP)
    return master


def host_axis(master: pd.DataFrame) -> pd.DataFrame:
    """The host-axis rows. 'unclear' counts too: those records are plotted."""
    rows = master[master["Data_category"].isin(["host", "unclear"])
                  & (~master["Status"].astype(str).str.startswith("EXCL"))].copy()
    rows["Count"] = pd.to_numeric(rows["Count"], errors="coerce")
    return rows


def category_breadth(master: pd.DataFrame) -> np.ndarray:
    """Categories each instance populates, by the same state matrix
    make_heatmap.py builds."""
    state = np.zeros((len(CAT_LABELS), len(TOOLS)))
    for j, tool in enumerate(TOOLS):
        for i, cat in enumerate(CAT_LABELS):
            rows = master[(master["Tool"] == tool) & (master["Detailed_scheme"] == cat)]
            if rows.empty:
                continue
            counts = pd.to_numeric(rows["Count"], errors="coerce")
            has_excl_only = (rows["Status"].astype(str).str.startswith("EXCL")).all()
            state[i, j] = 2 if (counts.notna().any() and not has_excl_only) else 1
    return (state > 0).sum(axis=0).astype(int)


def process_data(master: pd.DataFrame) -> pd.DataFrame:
    """One row of metrics per dataset instance."""
    host_rows = host_axis(master)
    breadth = category_breadth(master)
    rows_out = []
    for j, tool in enumerate(TOOLS):
        sub = host_rows[host_rows["Tool"] == tool]
        total = sub["Count"].sum()
        has_human_row = (sub["Detailed_scheme"] == "Humans").any()
        human = sub.loc[sub["Detailed_scheme"] == "Humans", "Count"].sum()
        # Grouped by category, not by raw label: several tools have more than
        # one label collapsing into the same category.
        by_cat = sub.groupby("Detailed_scheme")["Count"].sum()
        has_primate_data = any(c in by_cat.index for c in PRIMATE_CATS)
        primate_count = sum(by_cat.get(c, 0) for c in PRIMATE_CATS)

        if total and total > 0 and len(by_cat):
            human_frac = (human / total) if has_human_row else None
            primate_frac = (primate_count / total) if has_primate_data else None
            top_category = by_cat.idxmax()
            concentration = by_cat.max() / total
        else:
            human_frac, primate_frac, concentration, top_category = None, None, None, None

        adj = CONTAMINATION_ADJUSTMENTS.get(tool)
        adjusted_frac = (adj["adjusted_human_count"] / total) if (adj and total) else None

        rows_out.append(dict(
            Tool=tool,
            Human_dominance_fraction=round(human_frac, 4) if human_frac is not None else "N/A (no standalone Humans category at this tool's resolution)",
            Human_dominance_NA_reason=NA_REASON.get(tool, "") if human_frac is None else "",
            Human_dominance_fraction_adjusted=round(adjusted_frac, 4) if adjusted_frac is not None else "",
            Human_dominance_adjustment_note=adj["reason"] if adj else "",
            Primate_dominance_fraction=round(primate_frac, 4) if primate_frac is not None else "N/A",
            Primate_dominance_NA_reason=PRIMATE_NA_REASON.get(tool, "") if primate_frac is None else "",
            Dataset_size=TOTAL_DATASET_SIZE[tool],
            Log10_dataset_size=round(math.log10(TOTAL_DATASET_SIZE[tool]), 3),
            Breadth_of_27=int(breadth[j]),
            Concentration_index=round(concentration, 4) if concentration is not None else "N/A",
            Top_category=top_category if top_category is not None else "N/A",
            Total_host_records_used=int(total) if total and not pd.isna(total) else 0,
        ))
    return pd.DataFrame(rows_out)


def save(out: pd.DataFrame) -> None:
    """Write comparison_metrics.csv."""
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print("\nsaved ->", OUT)


if __name__ == "__main__":
    save(process_data(load_data()))
