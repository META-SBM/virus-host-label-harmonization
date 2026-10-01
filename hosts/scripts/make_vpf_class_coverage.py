# -*- coding: utf-8 -*-
"""Table S3: what VPF-Class covers, counted in profiles because that is its unit.

    python3 make_vpf_class_coverage.py

Writes table_S3_vpf_class_profile_coverage.csv and .md.
"""
import collections
import csv
import os
import sys

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
RS = os.path.join(ROOT, "raw_sources", "VPF_Class")
OUT_CSV = os.path.join(ROOT, "table_S3_vpf_class_profile_coverage.csv")
OUT_MD = os.path.join(ROOT, "table_S3_vpf_class_profile_coverage.md")

THRESHOLDS = [30, 50, 100]
RANKS = (("genus", "GenHost"), ("family", "FamHost"))

# Which host taxa are eukaryotic comes from the NCBI lineage in Host Taxon
# Predictor's dump. It does not cover everything; the rest are declared below,
# and the script fails if a taxon appears that neither route resolves.
DOMAIN_OVERRIDE = {
    # eukaryotic algae, absent from the lineage file
    "Aureococcus": "Eukaryota", "Ectocarpus": "Eukaryota", "Ostreococcus": "Eukaryota",
    "Ectocarpaceae": "Eukaryota", "Bathycoccaceae": "Eukaryota",
    # cyanobacteria and other bacteria
    "Synechococcus": "Bacteria", "Sphingomonas": "Bacteria", "Arthrobacter": "Bacteria",
    "Brevibacillus": "Bacteria", "Oenococcus": "Bacteria", "Salinivibrio": "Bacteria",
    "Agrobacterium": "Bacteria", "Caulobacter": "Bacteria", "Nitrincola": "Bacteria",
    "Sulfitobacter": "Bacteria", "Polaribacter": "Bacteria", "Rhodovulum": "Bacteria",
    "Serratia": "Bacteria", "Microcystis": "Bacteria", "Pediococcus": "Bacteria",
    "Anabaena": "Bacteria", "Phormidium": "Bacteria",
    "Synechococcaceae": "Bacteria", "Sphingomonadaceae": "Bacteria",
    "Oceanospirillaceae": "Bacteria", "Microcystaceae": "Bacteria",
    "Idiomarinaceae": "Bacteria", "Nostocaceae": "Bacteria",
    # archaea
    "Methanothermobacter": "Archaea", "Methanobacteriaceae": "Archaea",
}


def lineage_domains() -> dict:
    """Taxon -> domain, from the NCBI lineage in Host Taxon Predictor's dump."""
    sys.path.insert(0, os.path.join(ROOT, "per_tool_counts_from_scratch_v2", "extractors"))
    import extract_03_host_taxon_predictor as htp
    dump = os.path.join(htp.RS, "Host_Taxon_Predictor",
                        "all_viruses_with_desired_attributes.dump")
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


def load_data() -> dict:
    """The two released host-classification tables, and the domain of every
    taxon in them."""
    data = {"domain": lineage_domains()}
    for rank, table in RANKS:
        path = os.path.join(RS, f"2019_VPF_{table}_REclassification_new.tsv")
        with open(path, newline="", encoding="utf-8") as fh:
            data[rank] = list(csv.DictReader(fh, delimiter="\t"))
    return data


def process_data(data: dict) -> tuple:
    """Profiles per eukaryotic host taxon at each membership cut, plus the
    per-rank totals the front matter quotes."""
    rows_out, summary = [], {}
    for rank, _table in RANKS:
        rows = data[rank]
        taxa = {r["classification"] for r in rows if float(r["percentage"]) >= min(THRESHOLDS)}
        unresolved = [t for t in taxa if t not in data["domain"] and t not in DOMAIN_OVERRIDE]
        assert not unresolved, (
            f"no domain for {len(unresolved)} {rank} taxa -- add them to DOMAIN_OVERRIDE "
            f"with the domain each belongs to: {sorted(unresolved)}")

        def domain_of(t, domain=data["domain"]):
            return DOMAIN_OVERRIDE.get(t) or domain[t]

        counts = collections.defaultdict(dict)
        for thr in THRESHOLDS:
            kept = [r for r in rows if float(r["percentage"]) >= thr]
            # Above half a profile can satisfy only one class;
            per_profile = collections.Counter(r["VPF"] for r in kept)
            summary[(rank, thr)] = {
                "profiles": len(per_profile),
                "max_per_profile": max(per_profile.values()) if per_profile else 0,
                "eukaryotic_profiles": len({r["VPF"] for r in kept
                                            if domain_of(r["classification"]) == "Eukaryota"}),
            }
            for r in kept:
                if domain_of(r["classification"]) == "Eukaryota":
                    counts[r["classification"]][thr] = counts[r["classification"]].get(thr, 0) + 1

        for taxon in sorted(counts, key=lambda t: -counts[t].get(THRESHOLDS[0], 0)):
            rows_out.append({
                "Rank": rank,
                "Host taxon": taxon,
                **{f"Profiles at >={t}%": counts[taxon].get(t, 0) for t in THRESHOLDS},
            })
    return rows_out, summary


def markdown(rows_out: list, summary: dict) -> str:
    lines = [
        "# Table S3. VPF-Class coverage, counted in protein-family profiles", "",
        "VPF-Class carries no column in the host matrix: its released tables classify "
        "viral protein families rather than viruses, so no record count exists (see "
        "`DECISIONS.md`, entry 11). What it does state can still be reported, in its "
        "own unit. **Every number below is a count of profiles and is not comparable "
        "with a record count anywhere else in this review.**", "",
        "A profile carries a distribution over candidate hosts, so the membership "
        "ratio decides what a count means. Three cuts are given: **>=30%**, the "
        "operating point the article itself uses for host prediction at genus level; "
        "**>=50%**, above which a profile can satisfy only one class, so the "
        "assignment is unique; and **=100%**, wholly homogeneous profiles.", "",
    ]
    for rank, _table in RANKS:
        s30, s50 = summary[(rank, 30)], summary[(rank, 50)]
        lines += [
            f"## Host {rank}", "",
            f"Of {s30['profiles']:,} profiles reaching 30% at {rank} level, "
            f"{s30['eukaryotic_profiles']:,} name a eukaryotic host; at 50% it is "
            f"{s50['eukaryotic_profiles']:,} of {s50['profiles']:,}. At most "
            f"{s30['max_per_profile']} {rank} names per profile at 30%, "
            f"{s50['max_per_profile']} at 50%.", "",
            "| Host " + rank + " | " + " | ".join(f"≥{t}%" for t in THRESHOLDS) + " |",
            "|---|" + "---:|" * len(THRESHOLDS),
        ]
        for r in rows_out:
            if r["Rank"] == rank:
                lines.append(f"| *{r['Host taxon']}* | "
                             + " | ".join(f"{r[f'Profiles at >={t}%']:,}" for t in THRESHOLDS) + " |")
        lines.append("")
    return "\n".join(lines)


def save(rows_out: list, summary: dict) -> None:
    cols = ["Rank", "Host taxon"] + [f"Profiles at >={t}%" for t in THRESHOLDS]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows_out)
    print("saved ->", OUT_CSV)

    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(markdown(rows_out, summary))
    print("saved ->", OUT_MD)
    for rank, _table in RANKS:
        s = summary[(rank, 50)]
        print(f"  {rank}: {s['eukaryotic_profiles']:,} of {s['profiles']:,} profiles name a "
              f"eukaryotic host at >=50% (unique assignment: max {s['max_per_profile']} per profile)")


if __name__ == "__main__":
    save(*process_data(load_data()))
