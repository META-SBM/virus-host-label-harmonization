# -*- coding: utf-8 -*-
"""Table S4: every host label as its tool released it, before any harmonization.

    python3 make_before_harmonization_table.py

Writes table_S4_labels_as_released.csv and .md.
"""
import collections
import csv
import os

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
COUNTS = os.path.join(ROOT, "per_tool_counts_from_scratch_v2", "counts_per_tool_v2")
OUT_CSV = os.path.join(ROOT, "table_S4_labels_as_released.csv")
OUT_MD = os.path.join(ROOT, "table_S4_labels_as_released.md")

STATUS_WORDING = {
    "INCLUDE": "carried into the analysis",
    "EXCL": "excluded",
    "INCLUDE (documented, uncounted)": "documented, not counted",
}
COLUMNS = ["Tool", "Label as released", "Count", "Counting unit", "Label level",
           "Kind of statement", "Status", "Source file and field", "Note"]


def read(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_data() -> dict:
    """Every label with its curation, and where each tool's labels were read
    from -- taken from the recompute headers so the two cannot drift apart."""
    source_of = {}
    for fn in sorted(os.listdir(COUNTS)):
        if not fn.endswith("_counts.csv") or fn.startswith("00_"):
            continue
        tool = None
        with open(os.path.join(COUNTS, fn), newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row:
                    continue
                if row[0].startswith("# Tool"):
                    tool = row[1].strip()
                elif row[0].startswith("# Recomputed from"):
                    source_of[tool] = row[1].strip()
    return {
        "master": read(os.path.join(SC, "master_labels.csv")),
        "source_of": source_of,
        "categories": read(os.path.join(SC, "general_scheme_matrix.csv")),
    }


def process_data(data: dict) -> list:
    rows_out = [{
        "Tool": r["Tool"],
        "Label as released": r["Original_label"],
        "Count": r["Count"],
        "Counting unit": r["Counting_unit"],
        "Label level": r["Label_level"],
        "Kind of statement": r["Data_category"],
        "Status": STATUS_WORDING.get(r["Status"], r["Status"]),
        "Source file and field": data["source_of"].get(r["Tool"], ""),
        "Note": r["Notes"],
    } for r in data["master"]]
    rows_out.sort(key=lambda r: (r["Tool"], r["Label as released"]))

    missing_source = sorted({r["Tool"] for r in rows_out if not r["Source file and field"]})
    assert not missing_source, (
        f"no recompute header names a source file for {missing_source} -- a label cannot "
        "be published as released without saying what it was released in")
    return rows_out


def per_tool_totals(rows_out: list) -> dict:
    out = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in rows_out:
        e = out[r["Tool"]]
        e[0] += 1
        e[1] += r["Status"] == "excluded"
        try:
            e[2] += float(r["Count"])
        except (TypeError, ValueError):
            pass
    return out


def markdown(rows_out: list, n_after: int) -> str:
    per_tool = per_tool_totals(rows_out)
    lines = [
        "# Table S4. Host labels as released, before harmonization", "",
        f"`table_S4_labels_as_released.csv`, {len(rows_out):,} rows — one per tool and "
        "label, spelled as the released file spells it. Nothing in this table has been "
        "mapped, merged, renamed or resolved.", "",
        f"It is the input to everything else here. Those {len(rows_out):,} labels become "
        f"1,513 host entities in Table S2 and {n_after} categories on the figure, and "
        "reading the three in order shows every editorial act in between: `human`, "
        "`Human`, `Homo sapiens` and `Homo sapiens (taxid 9606, positive class)` are "
        "four rows in this table and one row in the next.", "",
        "**Status** says whether a label was carried into the analysis or excluded, and "
        "the note says why — non-eukaryotic classes, negative-class placeholders and "
        "labels that state no host are excluded, and each one says which it is. "
        "**Source file and field** names where the label was read, so any row can be "
        "checked against the release it came from.", "",
        "| Tool | Labels | of which excluded | Records |", "|---|---:|---:|---:|",
    ]
    for tool in sorted(per_tool):
        n, exc, rec = per_tool[tool]
        lines.append(f"| {tool} | {n:,} | {exc:,} | {round(rec):,} |")
    tot = [sum(x) for x in zip(*per_tool.values())]
    lines += [f"| **Total** | **{tot[0]:,}** | **{tot[1]:,}** | **{round(tot[2]):,}** |", ""]
    return "\n".join(lines)


def save(rows_out: list, n_after: int) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows_out)
    print("saved ->", OUT_CSV)

    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(markdown(rows_out, n_after))
    print("saved ->", OUT_MD,
          f"| {len(rows_out):,} labels from {len(per_tool_totals(rows_out))} tools")


if __name__ == "__main__":
    _data = load_data()
    save(process_data(_data), len({r["Row"] for r in _data["categories"]}))
