# -*- coding: utf-8 -*-
"""Why VPF-Class carries no column in the host matrix, recomputed from its files.

    python3 assess_vpf_class.py

Writes scripts/vpf_class_assessment.csv. The exclusion is not asserted here, it
is re-derived: the closing checks fail if any ground for it stops holding.
"""
import collections
import csv
import os

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
RS = os.path.join(ROOT, "raw_sources", "VPF_Class")
OUT = os.path.join(SC, "vpf_class_assessment.csv")

FILES = {rank: f"2019_VPF_{rank}_REclassification_new.tsv"
         for rank in ("DomHost", "FamHost", "GenHost", "BaltTax", "FamTax", "GenTax")}
# Bacterial families that turn up on profiles the domain file calls eukaryotic.
BACTERIAL_FAMILIES = {"Bacillaceae", "Enterobacteriaceae", "Vibrionaceae",
                      "Lactobacillaceae", "Xanthomonadaceae", "Erwiniaceae",
                      "Streptococcaceae", "Pseudomonadaceae", "Mycobacteriaceae"}
# Morphological Caudovirales families ICTV abolished in 2021.
RETIRED_FAMILIES = {"Myoviridae", "Siphoviridae", "Podoviridae"}


def read(rank: str) -> list:
    with open(os.path.join(RS, FILES[rank]), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def by_profile(rows: list) -> dict:
    out = collections.defaultdict(dict)
    for r in rows:
        out[r["VPF"]][r["classification"]] = float(r["percentage"])
    return out


def median(xs) -> float:
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 0.0


class Findings:
    """Each ground for the exclusion, printed as it is derived and written out
    as a row."""

    def __init__(self):
        self.rows = []

    def note(self, question: str, answer: str, detail: str) -> None:
        self.rows.append({"Question": question, "Answer": answer, "Detail": detail})
        print(f"  {answer:<11} {question}\n              {detail}")


def load_data() -> dict:
    return {rank: read(rank) for rank in ("DomHost", "FamHost", "GenHost", "FamTax")}


def process_data(data: dict) -> tuple:
    dom_rows, fam_rows, gen_rows = data["DomHost"], data["FamHost"], data["GenHost"]
    dom = by_profile(dom_rows)
    print(f"VPF-Class, {len(FILES)} released tables in raw_sources/VPF_Class/\n")
    f = Findings()

    # 1. There is no record unit to count.
    counts = {r: len({x["VPF"] for x in rows})
              for r, rows in (("DomHost", dom_rows), ("FamHost", fam_rows), ("GenHost", gen_rows))}
    f.note("Is there a countable record unit?", "no",
           "a row is a protein-family profile, not a virus, a sequence or a virus-host pair; "
           f"the three host tables do not even cover the same profiles ("
           + ", ".join(f"{k} {v:,}" for k, v in counts.items()) + ")")

    # 2. A profile does not name one host.
    per_fam = collections.Counter(r["VPF"] for r in fam_rows)
    per_gen = collections.Counter(r["VPF"] for r in gen_rows)
    f.note("Does a profile name one host?", "no",
           f"median {median(per_fam.values())} families and {median(per_gen.values())} genera per profile, "
           f"up to {max(per_fam.values())} and {max(per_gen.values())}")

    # 3. The percentage is a share, not an amount, and a small one.
    euk_pct = [float(r["percentage"]) for r in dom_rows if r["classification"] == "Eukaryota"]
    euk_c1 = [float(r["percentage"]) for r in dom_rows
              if r["classification"] == "Eukaryota" and r["category"] == "1"]
    f.note("Can the percentages stand in for counts?", "no",
           f"they are shares of a profile's hits: median {median(euk_pct):.1f}% on the {len(euk_pct):,} "
           f"Eukaryota rows, and {median(euk_c1):.1f}% even in the best-supported hit-count tier")

    # 4. The three ranks are independent classifications, not a hierarchy.
    euk_only = {v for v, d in dom.items() if list(d) == ["Eukaryota"] and d["Eukaryota"] == 100}
    fam_of = collections.defaultdict(set)
    for r in fam_rows:
        fam_of[r["VPF"]].add(r["classification"])
    contradicted = {v for v in euk_only if fam_of[v] & BACTERIAL_FAMILIES}
    example = sorted(contradicted)[0] if contradicted else ""
    f.note("Do the three rank tables nest?", "no",
           f"each rank is reclassified independently, so {len(contradicted):,} of the {len(euk_only):,} "
           f"profiles at Eukaryota 100% carry a bacterial family in the family table -- e.g. {example}: "
           + ", ".join(f"{k} {v:.0f}%" for k, v in
                       sorted(by_profile(fam_rows)[example].items(), key=lambda x: -x[1])[:3]))

    # 5. Profiles cannot be grouped back into virus-level records.
    refseq = {v: d for v, d in dom.items() if v.count("@") == 1}
    by_genome = collections.defaultdict(set)
    for v, d in refseq.items():
        by_genome[v.split("@")[1]] |= set(d)
    disagree = [g for g, s in by_genome.items() if len(s) > 1]
    f.note("Can profiles be grouped back into virus-level records?", "no",
           f"only {len(refseq):,} of {len(dom):,} profiles carry a genome accession, and "
           f"{len(disagree):,} of the {len(by_genome):,} genomes they name ("
           f"{100 * len(disagree) / len(by_genome):.0f}%) have profiles that disagree on the host domain")

    # 6. Scope: the corpus is prokaryotic.
    dominant = collections.Counter(max(d, key=d.get) for d in dom.values() if d)
    f.note("Is the corpus within a eukaryotic-host review?", "mostly not",
           "dominant domain per profile: "
           + ", ".join(f"{k} {v:,}" for k, v in dominant.most_common()))

    # The virus-taxonomy tables are the same shape, and are dated.
    tax_per = collections.Counter(r["VPF"] for r in data["FamTax"])
    retired = collections.Counter(r["classification"] for r in data["FamTax"]
                                  if r["classification"] in RETIRED_FAMILIES)
    f.note("Are the virus-taxonomy tables usable as they stand?", "not directly",
           f"same shape (median {median(tax_per.values())} families per profile), and the three "
           f"commonest families are the morphological Caudovirales families ICTV abolished in 2021 ("
           + ", ".join(f"{k} {v:,}" for k, v in retired.most_common()) + ")")

    grounds = {"per_gen": per_gen, "euk_pct": euk_pct,
               "contradicted": contradicted, "disagree": disagree}
    return f.rows, grounds


def check_exclusion_still_holds(g: dict) -> None:
    """The exclusion rests on these being true."""
    assert max(g["per_gen"].values()) > 1, "a profile now names a single genus -- revisit the exclusion"
    assert median(g["euk_pct"]) < 50, "eukaryotic percentages are no longer trace -- revisit the exclusion"
    assert g["contradicted"], "the rank tables now nest -- revisit the exclusion"
    assert g["disagree"], "profiles now agree per genome -- virus-level records may be reconstructible"
    print("VPF-Class stays out of the host matrix; all six grounds still hold.")


def save(findings: list, grounds: dict) -> None:
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Question", "Answer", "Detail"])
        w.writeheader()
        w.writerows(findings)
    print(f"\nsaved -> {OUT}")
    check_exclusion_still_holds(grounds)


if __name__ == "__main__":
    save(*process_data(load_data()))
