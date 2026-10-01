# -*- coding: utf-8 -*-
"""VPF-Class, 2019_VPF_GenHost_REclassification_new.tsv (bioinfo.uib.es/~recerca/VPF-Class/).
"""
import collections
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RS, write_csv

MIN_RATIO = 50.0
SRC = "VPF_Class/2019_VPF_GenHost_REclassification_new.tsv"

# Domain per host genus.
OVERRIDE = {
    "Aureococcus": "Eukaryota", "Ectocarpus": "Eukaryota", "Ostreococcus": "Eukaryota",
    "Synechococcus": "Bacteria", "Sphingomonas": "Bacteria", "Arthrobacter": "Bacteria",
    "Brevibacillus": "Bacteria", "Oenococcus": "Bacteria", "Salinivibrio": "Bacteria",
    "Agrobacterium": "Bacteria", "Caulobacter": "Bacteria", "Nitrincola": "Bacteria",
    "Sulfitobacter": "Bacteria", "Polaribacter": "Bacteria", "Rhodovulum": "Bacteria",
    "Serratia": "Bacteria", "Microcystis": "Bacteria", "Pediococcus": "Bacteria",
    "Anabaena": "Bacteria", "Phormidium": "Bacteria",
    "Methanothermobacter": "Archaea",
}


def domains_from_lineage():
    import extract_03_host_taxon_predictor as htp
    dump = os.path.join(RS, "Host_Taxon_Predictor", "all_viruses_with_desired_attributes.dump")
    with open(dump, "rb") as fh:
        seqs = htp.SafeUnpickler(fh, encoding="latin1").load().seqs
    out = {}
    for s in seqs:
        lineage = s.host_lineage or []
        domain = next((d for d in ("Bacteria", "Archaea", "Eukaryota") if d in lineage), None)
        if domain:
            for taxon in lineage:
                out.setdefault(taxon, domain)
    return out


def load_raw() -> list:
    """Genus-level rows at or above the membership ratio that makes the
    assignment unique."""
    with open(os.path.join(RS, SRC), newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t")
                if float(r["percentage"]) >= MIN_RATIO]


def count_labels(rows: list) -> list:
    """Eukaryotic host genera one row each, everything else in one excluded
    row. The uniqueness and the total are asserted here."""
    per_profile = collections.Counter(r["VPF"] for r in rows)
    if max(per_profile.values()) != 1:
        raise SystemExit(f"a profile has {max(per_profile.values())} genera at >={MIN_RATIO}%; "
                         "the assignment is no longer unique and this column is not valid")

    domain = domains_from_lineage()
    counts = collections.Counter(r["classification"] for r in rows)
    unresolved = [g for g in counts if g not in domain and g not in OVERRIDE]
    if unresolved:
        raise SystemExit(f"no domain for {sorted(unresolved)} -- add them to OVERRIDE")

    euk, prok = [], 0
    for genus, n in counts.most_common():
        if (OVERRIDE.get(genus) or domain[genus]) == "Eukaryota":
            euk.append((genus, n, ""))
        else:
            prok += n

    euk.append((f"Prokaryote/Archaea host genus (negative, EXCL)", prok,
                "non-eukaryotic, outside the review's scope"))
    total = sum(n for _, n, _ in euk)
    if total != len(per_profile):
        raise SystemExit(f"{total} counted against {len(per_profile)} profiles -- a profile was "
                         "dropped or double counted")
    return euk, len(per_profile)


def run():
    euk, n_profiles = count_labels(load_raw())
    return write_csv(
        18, "VPF-Class",
        f"{SRC}, genus-level host reclassification filtered to membership ratio >={MIN_RATIO:.0f}% "
        f"(the cut above which a profile can satisfy only one genus, so each of the "
        f"{n_profiles:,} profiles is counted once)",
        euk,
        note=("COUNTING UNIT IS A PROTEIN-FAMILY PROFILE, NOT A VIRUS. The release classifies "
              "viral protein families, not viruses; a profile spans many viruses and a virus "
              "contributes many profiles, so these counts are not comparable with any "
              "record count elsewhere in this review. The tool entered the review through "
              "citation searching and has no rows in original_reported_labels.xlsx to match "
              "against. See scripts/assess_vpf_class.py and DECISIONS.md entry 11."))


if __name__ == "__main__":
    run()
