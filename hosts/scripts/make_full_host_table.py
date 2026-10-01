# -*- coding: utf-8 -*-
"""Supplementary Table S2: every host entity, at its own resolution, no threshold.

    python3 make_full_host_table.py

Writes table_S2_full_host_table.csv and .md.
"""
import csv
import os
from collections import defaultdict

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
OUT_CSV = os.path.join(ROOT, "table_S2_full_host_table.csv")
OUT_MD = os.path.join(ROOT, "table_S2_full_host_table.md")

# Why an entity is where it is.
FATE_WORDING = {
    "standalone_species": "Named by >=6 instances; drawn as its own row",
    "vector_or_crustacea_rollup": "Vector or crustacean taxon; own row by explicit mapping",
    "vector_genus_fallback": "Vector taxon; own row by genus-level fallback",
    "taxon_promoted": "Grouped under the conventional taxon of its harmonized category",
    "detailed_scheme_direct": "Grouped under its harmonized category as it stands",
}
# Read the way the figure is read: lineage, then category, then largest first.
LINEAGE_ORDER = ["Mammals", "Non-mammalian vertebrates", "Invertebrates",
                 "Plants", "Fungi", "Unknown/Excluded"]


def read(name: str) -> list:
    with open(os.path.join(SC, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_data() -> dict:
    return {
        "rows": read("species_matrix_wide.csv"),
        "fate": {r["Row"]: r for r in read("general_scheme_row_fate.csv")},
        # An entity carrying vector-axis records in any instance is marked, the
        # same way the figure marks the cell it lands in.
        "vector_rows": {r["Row"] for r in read("species_matrix_vector_fallback.csv")},
        "categories": {r["Row"] for r in read("general_scheme_matrix.csv")},
    }


def check_one_row_per_entity(rows: list) -> None:
    seen = defaultdict(list)
    for r in rows:
        seen[r["Row"]].append((r["Rank"], r["Group"]))
    split = {k: v for k, v in seen.items() if len(v) > 1}
    assert not split, (
        "host entities occupying more than one row -- Rank/Group disagree between "
        f"the paths that reach them: {split}")


def check_routing(rows: list, fate: dict, categories: set) -> None:
    missing = [r["Row"] for r in rows if r["Row"] not in fate]
    assert not missing, f"no routing recorded for {len(missing)} entities: {missing[:5]}"
    stray = {f["Final_category"] for f in fate.values()} - categories
    assert not stray, f"routed to categories the figure does not draw: {sorted(stray)}"


def process_data(data: dict) -> tuple:
    rows, fate = data["rows"], data["fate"]
    instances = [c for c in rows[0] if c not in ("Row", "Rank", "Group")]
    check_one_row_per_entity(rows)
    check_routing(rows, fate, data["categories"])

    out = []
    for r in rows:
        counts = {i: int(float(r[i])) for i in instances}
        out.append({
            "Host entity": r["Row"],
            "Rank": r["Rank"],
            "Lineage": r["Group"],
            "Figure category": fate[r["Row"]]["Final_category"],
            "Why": FATE_WORDING.get(fate[r["Row"]]["Fate"], fate[r["Row"]]["Fate"]),
            "Vector axis": "Yes" if r["Row"] in data["vector_rows"] else "",
            "Dataset instances": sum(1 for v in counts.values() if v),
            "Records": sum(counts.values()),
            **counts,
        })
    out.sort(key=lambda r: (LINEAGE_ORDER.index(r["Lineage"]) if r["Lineage"] in LINEAGE_ORDER
                            else len(LINEAGE_ORDER),
                            r["Figure category"], -r["Records"], r["Host entity"]))
    return out, instances


def markdown(out: list, instances: list, categories: set) -> str:
    """A short front matter for the supplement: the table itself is far too long
    to render, so this states what it is and summarises the collapse."""
    total = sum(r["Records"] for r in out)
    per_cat = defaultdict(lambda: [0, 0])
    for r in out:
        per_cat[r["Figure category"]][0] += 1
        per_cat[r["Figure category"]][1] += r["Records"]

    lines = [
        "# Table S2. Full host table — every entity, no retention threshold", "",
        f"`table_S2_full_host_table.csv`, {len(out):,} rows, one per host entity, "
        f"{total:,} records across {len(instances)} dataset instances.", "",
        "The figure draws " + str(len(categories)) + " categories because a species must be "
        "named by at least 6 of the 17 dataset instances to hold a row of its own. "
        "This table removes that threshold: every host entity appears at the "
        "resolution its own source published it at, with the category the figure "
        "placed it in and the rule that put it there. It is the audit trail for the "
        "collapse, and the answer to what any one row of the figure is made of.", "",
        "Columns: identity and rank; lineage; the figure category and why; whether the "
        "entity carries vector-axis records; how many dataset instances name it; total "
        "records; then one column per dataset instance. HostNet's two instances are "
        "kept apart here, where the figure sums them.", "",
        "The **Why** column distinguishes the four routes into a category. The first "
        "three keep an entity as a row of its own — the retention threshold, or the "
        "explicit vector mapping, or its genus-level fallback. The fourth and "
        "commonest, *grouped under the conventional taxon*, covers every entity that "
        "did not clear the bar, whether it is a species or a term that names no "
        "species; those are the rows the figure compresses.", "",
        "## What each figure category is made of", "",
        "| Figure category | Entities | Records |", "|---|---:|---:|",
    ]
    for cat in sorted(per_cat, key=lambda c: -per_cat[c][1]):
        n, rec = per_cat[cat]
        lines.append(f"| {cat} | {n:,} | {rec:,} |")
    lines += ["", f"| **Total** | **{len(out):,}** | **{total:,}** |", ""]
    return "\n".join(lines)


def save(out: list, instances: list, categories: set) -> None:
    columns = (["Host entity", "Rank", "Lineage", "Figure category", "Why", "Vector axis",
                "Dataset instances", "Records"] + instances)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(out)

    total = sum(r["Records"] for r in out)
    kept = sum(1 for r in out if r["Figure category"] == r["Host entity"])
    print(f"saved -> {OUT_CSV}")
    print(f"{len(out)} host entities, {total:,} records, {len(categories)} figure categories; "
          f"{kept} entities are a figure row in their own right")

    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(markdown(out, instances, categories))
    print("saved ->", OUT_MD)


if __name__ == "__main__":
    _data = load_data()
    _out, _instances = process_data(_data)
    save(_out, _instances, _data["categories"])
