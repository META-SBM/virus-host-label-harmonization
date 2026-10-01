# -*- coding: utf-8 -*-
"""Supplementary provenance table: one row per tool column of the figure.

    python3 make_provenance_table.py

Writes table_S1_data_provenance.csv and .md. What the figure knows about its
own columns is imported from it, not restated here.
"""
import csv
import os

import make_general_scheme_heatmap as scheme
from categories import DATASET_SCOPE, MOLTYPE_LABEL

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
COUNTS = os.path.join(ROOT, "per_tool_counts_from_scratch_v2", "counts_per_tool_v2")
OUT_CSV = os.path.join(ROOT, "table_S1_data_provenance.csv")
OUT_MD = os.path.join(ROOT, "table_S1_data_provenance.md")

SCOPE_WORDING = {
    "full_dataset": "Complete labelled release",
    "train+test": "Complete labelled release (train + test)",
    "train+val+test": "Complete labelled release (train + val + test)",
    "train_only": "Training corpus (what the study itself reports)",
}
RECTYPE_WORDING = {
    "seq": "Sequence-level (one record per isolate)",
    "taxon": "Virus-taxon-level (one record per virus species)",
    "dedup": "Deduplicated species pool",
    # Spelled out, because this is the one unit in the table that does not count
    # viruses at all and so cannot be compared with the other three.
    "profile": "Protein-family profile (NOT a virus; not comparable with the counts above)",
}
# The two HostNet dataset instances are summed into one column for display.
INSTANCES = {"HostNet": ["HostNet (Rabies, VIPHOD)", "HostNet (Flavivirus)"]}


def instances_of(tool: str) -> list:
    return INSTANCES.get(tool, [tool])


def load_data() -> dict:
    """The figure's columns, and the recompute headers that say where each
    column's numbers were read from."""
    recomputed_from, extraction_note, label_records = {}, {}, {}
    for fn in sorted(os.listdir(COUNTS)):
        if not fn.endswith("_counts.csv") or fn.startswith("00_"):
            continue
        tool = None
        with open(os.path.join(COUNTS, fn), newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        n_labels = 0
        for row in rows:
            if not row:
                continue
            if row[0].startswith("# Tool"):
                tool = row[1].strip()
            elif row[0].startswith("# Recomputed from"):
                recomputed_from[tool] = row[1].strip()
            elif row[0].startswith("# Note"):
                extraction_note[tool] = row[1].strip()
            elif row[0] != "TOTAL" and len(row) > 1 and row[1].strip() and not row[0].startswith("Label"):
                n_labels += 1
        label_records[tool] = n_labels
    with open(os.path.join(SC, "general_scheme_matrix.csv"), newline="", encoding="utf-8") as fh:
        n_categories = len({r["Row"] for r in csv.DictReader(fh)})
    return {
        "figure": scheme.process_data(scheme.load_data()),
        "recomputed_from": recomputed_from,
        "extraction_note": extraction_note,
        "label_records": label_records,
        "n_categories": n_categories,
    }


def joined(tool: str, mapping: dict, sep: str = "; ") -> str:
    """One cell for a tool, naming each dataset instance when there are two."""
    inst = instances_of(tool)
    if len(inst) == 1:
        return mapping.get(inst[0], "")
    return sep.join(f"{i.split('(')[-1].rstrip(')')} — {mapping.get(i, '')}"
                    for i in inst if mapping.get(i))


def process_data(data: dict) -> tuple:
    """One row per tool. Every figure-derived number is read off the rendered
    matrix rather than recounted, so the table cannot drift from the figure."""
    fig = data["figure"]
    tools, annot = fig["TOOLS"], fig["annot"]
    # Counted from the scheme rather than written in: the total was 51 when this
    # table was written and is 49 now, and a literal in a column header is a caption
    # that goes quietl
    cats_col = f"Categories populated (of {data['n_categories']})"
    columns = [
        "Tool",
        "Prediction target",
        "Dataset scope",
        "Dataset size",
        "Source file and field extracted",
        "Counting unit",
        "Input molecule",
        "Distinct labels recomputed",
        "Host records on figure",
        cats_col,
        "Extraction notes",
    ]

    rows_out = []
    for j, tool in enumerate(tools):
        n, unit = fig["TOTAL_DATASET_SIZE"][tool]
        scope = joined(tool, {i: SCOPE_WORDING.get(DATASET_SCOPE[i][0], DATASET_SCOPE[i][0])
                              for i in instances_of(tool)})
        notes = [joined(tool, data["extraction_note"], sep="  ||  ")]
        if tool in fig["DOUBLE_COUNT_TOOLS"]:
            notes.append("One record can fall in more than one category; column marked * on the figure "
                         "and totals are not deduplicated.")
        if any(t.startswith(tool) for _, t in fig["VECTOR_FALLBACK_CELLS"]):
            notes.append("Carries vector-axis records; the cells concerned are marked V.")
        col_total = sum(int(annot[i, j].replace(",", ""))
                        for i in range(len(fig["CATS"])) if annot[i, j])
        rows_out.append({
            "Tool": tool,
            "Prediction target": f"{fig['ENDPOINT_CATEGORY'][tool]} — "
                                 f"{fig['ENDPOINT_LABEL'][fig['ENDPOINT_CATEGORY'][tool]]}",
            "Dataset scope": scope,
            "Dataset size": f"{n:,} {unit}",
            "Source file and field extracted": joined(tool, data["recomputed_from"], sep="  ||  "),
            "Counting unit": RECTYPE_WORDING[fig["record_type"][tool]],
            "Input molecule": MOLTYPE_LABEL[fig["MOLECULE_TYPE"][tool][0]],
            "Distinct labels recomputed": sum(data["label_records"].get(i, 0) for i in instances_of(tool)),
            "Host records on figure": f"{col_total:,}",
            cats_col: int(fig["breadth_per_tool"][j]),
            "Extraction notes": "  ".join(x for x in notes if x),
        })
    return rows_out, columns, cats_col


def md_cell(v) -> str:
    """Markdown reads a bare | as a column break, and HostNet's scope cell has one."""
    return str(v).replace("|", "/")


def markdown(rows_out: list, cats_col: str, n_categories: int) -> str:
    """The long provenance strings go under the table as footnotes, so the grid
    stays readable on a page."""
    short = ["Tool", "Prediction target", "Dataset scope", "Dataset size", "Counting unit",
             "Input molecule", "Distinct labels recomputed",
             "Host records on figure", cats_col]
    head = {"Distinct labels recomputed": "Labels recomputed",
            "Host records on figure": "Records on figure",
            cats_col: f"Categories (of {n_categories})"}

    lines = ["# Table S1. Data provenance and extraction, by tool", "",
             "One row per column of the host-scheme figure. Where a tool contributes two "
             "dataset instances they are named inside the cell; the figure sums them for "
             "display only.", "",
             "**Distinct labels recomputed** is the number of distinct host labels "
             "found in the tool's released files, and **Categories** how many "
             "harmonized categories those labels resolve to. A column giving the "
             "label count each article states was withdrawn: of its 278 entries only "
             "38 could be pointed to a passage in a paper, 174 were the release's own "
             "labels reproduced by the recompute, and 48 matched only on count. It "
             "did not measure what its name said. The per-label evidence is kept in "
             "reported_labels_provenance.csv for anyone who wants it.", ""]
    lines.append("| " + " | ".join(head.get(c, c) for c in short) + " |")
    lines.append("|" + "|".join(["---"] * len(short)) + "|")
    for r in rows_out:
        lines.append("| " + " | ".join(md_cell(r[c]) for c in short) + " |")

    lines += ["", "## Source file and field extracted", ""]
    for r in rows_out:
        lines.append(f"**{r['Tool']}.** {r['Source file and field extracted']}")
        if r["Extraction notes"].strip():
            lines.append(f"  *Notes:* {r['Extraction notes']}")
        lines.append("")
    return "\n".join(lines)


def save(rows_out: list, columns: list, cats_col: str, n_categories: int) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(rows_out)
    print("saved ->", OUT_CSV)

    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(markdown(rows_out, cats_col, n_categories))
    print("saved ->", OUT_MD, f"| {len(rows_out)} tools")


if __name__ == "__main__":
    _data = load_data()
    _rows, _columns, _cats_col = process_data(_data)
    save(_rows, _columns, _cats_col, _data["n_categories"])
