# -*- coding: utf-8 -*-
"""Provenance of every host-name harmonization act, one row per (released label,
resolved entity) pair.

    python3 build_host_harmonization_provenance.py

Writes scripts/host_harmonization_provenance.csv.

This table documents THIS PROJECT'S harmonization rules. It is deliberately not
called a taxonomy provenance table, because for most rows there is no external
taxonomic provenance to record: `accepted_name`, `taxid` and `evidence_url` are
MISSING wherever no authority was consulted, and MISSING is a finding rather
than a blank waiting to be guessed at. What the table records exactly is which
curation rule fired for each rewrite.

The names that HAVE been checked against an authority are carried in
`host_name_authority_checks.csv` (NCBI Taxonomy, accessed 2026-09-08) and their
taxids are joined in here, so the two files cannot disagree about a taxid.

The rule tables are read out of build_species_matrix.py with ast.literal_eval
rather than imported, so that this script cannot trigger a rebuild.
"""
import ast
import csv
import os

SC = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SC, "build_species_matrix.py")
OUT = os.path.join(SC, "host_harmonization_provenance.csv")
CHECKS = os.path.join(SC, "host_name_authority_checks.csv")

COLUMNS = ["original_entity", "harmonized_entity", "accepted_name", "taxid", "authority",
           "authority_version_or_access_date", "mapping_method", "mapping_status",
           "evidence_url", "notes"]

AUTHORITY = "manual curation in this repository"
UNRECORDED = "MISSING"

# What each rule is, in the order resolve_species/resolve_higher apply them.
METHOD_NOTE = {
    "identity": "label already names the entity; carried through unchanged",
    "synonym_table": "rewritten by the RESOLVE table in build_species_matrix.py",
    "higher_rank_table": "mapped to a higher taxon by the HIGHER table, keyed on (label, label level)",
    "binomial_synonym": "rewritten by BINOMIAL_SYNONYM, a four-entry table of older or infraspecific binomials",
    "infraspecific_collapse": "trinomial collapsed onto its binomial by collapse_to_binomial()",
    "vector_fallback_override": "vector-axis label routed by VECTOR_FALLBACK_TARGET_OVERRIDE",
    "low_materiality_fallback": "species below the materiality bar routed by LOW_MATERIALITY_FALLBACK",
    "category_residual": "label names no taxon; carried to its category's residual row",
    "below_materiality_bar": ("resolved to a species, but displayed inside its category's residual row: "
                              "build_species_matrix.py keeps a species only when at least 2 dataset "
                              "instances name it or one gives it 100 or more records"),
    "unclassified": "no rule in build_species_matrix.py accounts for this pair",
}


def rule_tables() -> dict:
    """The manual tables, read without executing the module."""
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                continue
    return out


def load_data() -> dict:
    with open(os.path.join(SC, "species_matrix_label_trace.csv"), newline="", encoding="utf-8") as fh:
        trace = list(csv.DictReader(fh))
    with open(os.path.join(SC, "species_matrix.csv"), newline="", encoding="utf-8") as fh:
        matrix = list(csv.DictReader(fh))
    with open(CHECKS, newline="", encoding="utf-8") as fh:
        checks = list(csv.DictReader(fh))
    return {"trace": trace, "matrix": matrix, "rules": rule_tables(), "checks": checks}


def classify(t: dict, rules: dict) -> str:
    """Which rule accounts for this rewrite. The trace records which of the two
    resolution paths fired, so the path is read off it rather than guessed; only
    the sub-rule inside the species path has to be re-derived."""
    original, harmonized = t["Original_label"], t["Row"]
    if t["Row_source"] == "vector_fallback_used":
        return "vector_fallback_override"
    if t["Resolved_higher"]:
        return "higher_rank_table"
    if not t["Resolved_species"]:
        return "category_residual"
    if original in rules["LOW_MATERIALITY_FALLBACK"]:
        return "low_materiality_fallback"
    if "(not resolved to species)" in harmonized:
        return "below_materiality_bar"
    if original == harmonized:
        return "identity"
    if original in rules["RESOLVE"]:
        return "synonym_table"
    if original in rules["BINOMIAL_SYNONYM"] or rules["RESOLVE"].get(original) in rules["BINOMIAL_SYNONYM"]:
        return "binomial_synonym"
    collapsed = " ".join(original.replace("(", " ").split()[:2])
    if collapsed == harmonized:
        return "infraspecific_collapse"
    return "unclassified"


def process_data(data: dict) -> list:
    rank = {r["Row"]: r["Rank"] for r in data["matrix"]}
    checked = {c["name_used_here"]: c for c in data["checks"] if c["verdict"] == "CONFIRMED"}
    seen, rows = set(), []
    for t in data["trace"]:
        key = (t["Original_label"], t["Row"])
        if key in seen:
            continue
        seen.add(key)
        method = classify(t, data["rules"])
        rows.append({
            "original_entity": t["Original_label"],
            "harmonized_entity": t["Row"],
            "accepted_name": checked.get(t["Row"], {}).get("accepted_name", UNRECORDED),
            "taxid": checked.get(t["Row"], {}).get("taxid", UNRECORDED),
            "authority": checked[t["Row"]]["authority"] if t["Row"] in checked else AUTHORITY,
            "authority_version_or_access_date":
                checked.get(t["Row"], {}).get("access_date", UNRECORDED),
            "mapping_method": method,
            "mapping_status": "identity" if method == "identity" else (
                "unclassified" if method == "unclassified" else "manual_curated"),
            "evidence_url": checked.get(t["Row"], {}).get("evidence_url", UNRECORDED),
            "notes": f"{METHOD_NOTE[method]}. Resolved entity rank: {rank.get(t['Row'], 'MISSING')}.",
        })
    rows.sort(key=lambda r: (r["harmonized_entity"], r["original_entity"]))
    return rows


def save(rows: list) -> None:
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    import collections
    by_method = collections.Counter(r["mapping_method"] for r in rows)
    print("saved ->", OUT, f"| {len(rows)} label-to-entity pairs, "
          f"{len({r['harmonized_entity'] for r in rows})} distinct entities")
    for m, n in by_method.most_common():
        print(f"   {m:<26}{n:>6}")
    entities = {r["harmonized_entity"] for r in rows}
    ent_taxid = {r["harmonized_entity"] for r in rows if r["taxid"] != UNRECORDED}
    print(f"   {'pairs with a taxid':<26}{sum(1 for r in rows if r['taxid'] != UNRECORDED):>6}")
    print(f"   {'entities with a taxid':<26}{len(ent_taxid):>6} of {len(entities)}")


if __name__ == "__main__":
    save(process_data(load_data()))
