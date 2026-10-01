#!/usr/bin/env python3
"""Re-derive every number the manuscript quotes for the host analysis.

    python3 verify_reported_numbers.py

Exits non-zero if any stated value no longer matches the committed tables.
"""
from __future__ import annotations

import csv
import re
import sys

from categories import excluded_instances, is_excluded
from collections import Counter
from pathlib import Path

SC = Path(__file__).resolve().parent

# Values as the manuscript states them. Changing the text means changing these.
# Re-baselined on 2026-09-25, when HostClassifier was flagged
# include_in_analysis = no in tool_metadata.csv and the standalone-species
# bar returned to 5 of 17 instances. Every value below was recomputed from
# the committed tables by this script, not edited by hand.
CLAIMED = {
    "mapping records": 6838,
    "included mapping records": 6270,
    "high confidence records": 5843,
    "medium confidence records": 421,
    "low confidence records": 6,
    "high confidence share": "93.5%",
    "medium confidence share": "6.1%",
    "low confidence share": "0.4%",
    "excluded source labels": 568,
    "host entities": 1315,
    "display categories": 50,
    "observations": 545898,
    "populated cells": 304,
    "matrix cells": 800,
    "dataset instances": 17,
    "tools": 16,
    # "reported source labels" (278) and "articles enumerating labels" (16) were
    # dropped on 2026-09-09: the claim they backed was withdrawn as unsupported,
    # only 38 of the 278 carry a pointer into a paper, and no live manuscript
    # file states either number any more.
    # The Results argue from these three that a six-instance threshold is
    # unreachable outside mammals.
    "plant species": 443,
    "algal species": 3,
    "fungal species": 101,
    "instances naming a plant species": 4,
    # The Results open by contrasting the unthresholded scheme with the drawn
    # one.
    "categories with no threshold": 1278,
    # Quoted in the Discussion, where the gap between the two is the argument.
    "DeePaC-vir categories populated": 48,
    "VIDHOP categories populated": 22,
    # The Discussion contrasts how many label strings a release carries with how
    # many categories they resolve to; the Limitations quote the curation counts.
    "RNAVirHost labels carried": 2496,
    "RNAVirHost categories populated": 41,
    "HostClassifier labels carried": 1238,
    "sequence-counting instances": 10,
    "taxon-counting instances": 5,
    # Added by the methods audit of 2026-09-08. Each was recomputed from the
    # committed tables before being written here; see
    # HOST_METHODS_CLARIFICATIONS.md for the derivation of every one.
    "excluded observations": 27199,
    "non-eukaryotic excluded labels": 563,
    "VirHostPRED flagged positive-class records": 235,
    "VirHostPRED Staphylococcus phage 6ec records": 141,
    "VirHostPRED IAS virus records": 94,
    "retained species": 26,
    "explicit vector mappings": 14,
    "genus-rule vector mappings": 59,
    "entities mapped to a higher rank": 779,
    "entities used unchanged": 437,
    "display headers": 8,
    "drawn rows": 58,
    # The two neighbouring thresholds, quoted in the Methods to justify 6. At 5
    # the two species counts differ: four species clear the bar and are still
    # pooled, because the vector/crustacean mapping outranks the threshold.
    "categories at threshold 5": 50,
    "species clearing the bar at threshold 5": 26,
    "standalone species at threshold 5": 26,
    "categories at threshold 7": 32,
    "standalone species at threshold 7": 8,
    # The Methods lead with the unweighted shares, because observation counts
    # are not on a common scale; the weighted figure above is kept because the
    # text still quotes it, with VIDHOP's dominance of it stated alongside.
    "high confidence share, unweighted": "93.2%",
    "medium confidence share, unweighted": "6.7%",
    "low confidence share, unweighted": "0.1%",
    "VIDHOP share of observations": "48.4%",
    # The materiality bar, surfaced by the 2026-09-08 provenance table: a name can
    # be resolved to a binomial and still be displayed inside a residual row.
    "species names recovered": 2799,
    "species drawn as their own entity": 1265,
    "species pooled by the materiality bar": 1534,
    "residual rows absorbing them": 18,
    "plant species names recovered": 1022,
    "fungal species names recovered": 189,
    # Results section, rebuilt 2026-09-08 on unit-free statistics: counts of
    # instances, presence/absence, and shares within one instance only.
    "categories named by 11 instances": 0,
    "median instances per category": 6,
    "categories named by one instance": 2,
    "narrowest category breadth": 2,
    "widest category breadth": 48,
    "instances with any carnivore records": 11,
    "instances where the dog is the largest carnivore row": 4,
    "largest within-instance dog share of carnivores": "67.6%",
    "wild-species cells": 45,
    "wild-species cells at 1% or less of their instance": 35,
    "largest within-instance wild-species share": "4.5%",
    "instances naming amphibians": 3,
    "instances naming reptiles": 6,
    # SPHAK's released training file duplicates 773 rows exactly. Kept, because
    # the study's own reported total counts them; reported as a finding instead.
    "SPHAK duplicated accessions": 773,
    "SPHAK redundant rows": 773,
    "SPHAK observations": 13570,
    "SPHAK observations if deduplicated": 12797,
    "SPHAK duplicate share": "5.7%",
    "authority checks performed": 33,
    "entities carrying a taxid": 30,
    "matrix occupancy": "38.0%",
    # 51 comes from reported_labels.csv, and every one of its 51 rows is
    # reproduced by our own recompute from the released files, so the two are
    # cross-checked against each other here rather than trusted separately.
    "VIDHOP reported labels": 51,
    "VIDHOP labels in the recompute": 51,
    "Host Taxon Predictor reported labels": 6,
    "Host Taxon Predictor categories populated": 48,
    "instances naming Homo sapiens": 14,
    "instances naming Canis lupus": 8,
    "Canis lupus spellings": 5,
    "wild species clearing the threshold": 9,
    "instances at 40% human or more": 6,
    "instances at 12% human or less": 6,
    "instances with no human records": 3,
    "widest lineage coverage": 8,
    "narrowest lineage coverage": 1,
    "instances naming a fungal species": 3,
    "instances naming a mammal species": 14,
    # Shares of the record-weighted total by counting unit, which is why that
    # total is a processing checksum and not a corpus size.
    "sequence-counted observations": 531286,
    "taxon-counted observations": 11881,
    "deduplicated-pool observations": 736,
    "profile-counted observations": 1995,
    # Added 2026-09-09 after a coverage check of the prose against this table
    # found them stated and never recomputed. Every one held; they are here so
    # that stays true. Each is a share of one instance's own records, which is
    # the only way a percentage in this work can be read.
    "HostClassifier human share": "54.3%",
    "DeepHoF human share": "59.1%",
    "RNAVirHost plant share": "32.3%",
    "DeePaC-vir plant share": "27.9%",
    "HostNet invertebrate share": "45.2%",
    # The Results argue that the dog is invisible until synonyms are merged, and
    # the argument rests on no single spelling clearing the six-instance bar.
    "instances writing Canis lupus": 4,
    "instances writing Canis lupus familiaris": 4,
    "instances writing Canis familiaris": 2,
    # Provenance, stated in the Methods and held only by the manifest.
    "raw source files": 34,
    "raw files with a resolvable URL": 34,
    "raw files with no retrieval date": 24,
    "raw files whose published copy was re-fetched": 19,
    # The low-confidence examples the Methods names and Supplementary S2 lists
    # in full. Added 2026-09-09 with those examples.
    "HostClassifier unrecorded-host records": 635,
    "HostClassifier cell-culture records": 63,
    "VirHostPRED negative-class records": 2127,
    "GIVAL post-hoc groupings carrying no count": 3,
    # "Where the host was hardest to determine", added 2026-09-10. Each names a
    # situation in which a release yields no host in the sense the others mean.
    "record-type phrasings across the releases": 12,
    "records naming no host": 15,
    "instances naming no host": 3,
    "HostClassifier records naming no host": 1133,
    "records giving a class but no species": 0,
    "vector-annotation records": 9766,
    "wholly vector-annotation records": 9721,
    "RNAVirHost multi-host records": 17063,
    "DeepHoF multi-host records": 12211,
    # VPF-Class, the instance whose unit is not a virus. The structural grounds
    # (82 genera per profile, the 219 of 1,064, the median hit share) are
    # recomputed from the raw tables by assess_vpf_class.py, which the audit
    # runs as its own stage. These four come from the committed tables.
    "VPF-Class profiles in the genus table": 19056,
    "VPF-Class profiles clearing the 50% cut": 12253,
    "VPF-Class profiles with a eukaryotic host genus": 1995,
    "VPF-Class profiles with a prokaryotic host genus": 10258,
}


# Every row the matrix places under Carnivora, header included, so the dog's
# share of the carnivore rows is taken over the same set the figure draws.
CARNIVORE_ROWS = ("Carnivora", "Canis lupus", "Vulpes vulpes", "Procyon lotor", "Felis catus",
                  "Mephitis mephitis", "Mustela putorius", "Nyctereutes procyonoides")
# The bats, rodents and non-human primates the Results single out.
WILD_SPECIES = {"Desmodus rotundus", "Eptesicus fuscus", "Tadarida brasiliensis",
                "Mus musculus", "Rattus norvegicus", "Mesocricetus auratus",
                "Pan troglodytes", "Macaca mulatta", "Chlorocebus aethiops"}


def num(x: str) -> float:
    try:
        return float(x)
    except ValueError:
        return 0.0


def read(name: str) -> list[dict]:
    with (SC / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_data() -> dict:
    data = {name: read(f"{name}.csv") for name in
            ("master_labels", "species_matrix", "general_scheme_matrix", "reported_labels",
             "threshold_sweep", "tool_metadata", "general_scheme_row_fate",
             "comparison_metrics", "species_matrix_label_trace")}
    data["label_trace"] = data.pop("species_matrix_label_trace")
    data["virhostpred_flagged"] = read("virhostpred_flagged_records.csv")
    data["harmonization_provenance"] = read("host_harmonization_provenance.csv")
    data["authority_checks"] = read("host_name_authority_checks.csv")
    data["sphak_duplicates"] = read("sphak_duplicate_records.csv")
    data["row_meta"] = read("r_general_scheme/row_meta.csv")
    data["manifest"] = read("../sources/MANIFEST.csv")
    return data


def flagged_records(flagged: list, comparison_metrics: list) -> dict:
    """The records in VirHostPRED's human-infecting class whose source organism
    is not a human-infecting virus, counted per organism from the per-accession
    evidence table, and cross-checked against the adjusted human-dominance
    fraction so the two cannot drift apart."""
    out = Counter(r["organism_label_in_release"] for r in flagged)
    out["total"] = len(flagged)
    row = next(r for r in comparison_metrics if r["Tool"] == "VirHostPRED")
    n = int(row["Dataset_size"])
    from_metrics = (round(float(row["Human_dominance_fraction"]) * n)
                    - round(float(row["Human_dominance_fraction_adjusted"]) * n))
    if from_metrics != out["total"]:
        raise SystemExit(f"virhostpred_flagged_records.csv holds {out['total']} records but "
                         f"comparison_metrics.csv implies {from_metrics} -- the two disagree")
    return out


def recompute(data: dict) -> dict:
    """Each stated value, derived from the tables rather than from the text."""
    master, species = data["master_labels"], data["species_matrix"]
    scheme, reported = data["general_scheme_matrix"], data["reported_labels"]

    included = [r for r in master if r["Status"].startswith("INCLUDE")]
    excluded = [r for r in master if r["Status"] == "EXCL"]

    # Confidence is reported over the mapping records the analysis actually
    # uses.
    conf = Counter(r["Mapping_confidence"] for r in included)
    weight = Counter()
    for r in included:
        weight[r["Mapping_confidence"]] += num(r["Count"])
    total_weight = sum(weight.values())

    instances = {r["Tool"] for r in scheme}
    tools = {t.split(" (")[0] for t in instances}

    sweep = {int(r["Threshold"]): int(r["Categories"]) for r in data["threshold_sweep"]}
    sweep_species = {int(r["Threshold"]): int(r["Species drawn as their own row"])
                     for r in data["threshold_sweep"]}
    sweep_clearing = {int(r["Threshold"]): int(r["Species clearing the bar"])
                      for r in data["threshold_sweep"]}
    populated = Counter(r["Tool"] for r in scheme if num(r["Count"]) > 0)
    carried = Counter(r["Tool"] for r in included)
    units = Counter(r["counting_unit"] for r in data["tool_metadata"])

    # How each entity reached its display category, and how many observations
    # each counting unit contributes to the record-weighted total.
    fate_counts = Counter(r["Fate"] for r in data["general_scheme_row_fate"])
    unit_of = {r["tool"]: r["counting_unit"] for r in data["tool_metadata"]}
    per_unit = Counter()
    for r in included:
        per_unit[unit_of[r["Tool"].split(" (")[0]]] += num(r["Count"])
    # An article that enumerates its host labels has rows in reported_labels;
    # instances are folded back to their tool so HostNet is not counted twice.
    with_list = {r["Tool"].split(" (")[0] for r in reported}
    header_rows = [r for r in data["row_meta"] if r["is_header"] == "1"]
    vidhop = sum(num(r["Count"]) for r in included if r["Tool"] == "VIDHOP")
    flagged = flagged_records(data["virhostpred_flagged"], data["comparison_metrics"])
    sphak_total = sum(num(r["Count"]) for r in scheme if r["Tool"] == "SPHAK")
    # Every duplicate must be an exact one, or the finding is a different finding.
    partial = [r for r in data["sphak_duplicates"] if r["identical_in_every_field"] != "yes"]
    if partial:
        raise SystemExit(f"{len(partial)} SPHAK duplicates are not identical in every field, "
                         f"e.g. {partial[0]['accession']} -- these would be multi-host records, "
                         "not redundant rows, and the Methods wording would be wrong")

    # Row and column aggregates of the drawn matrix, for the Results section.
    n_categories = len({r["Row"] for r in scheme})
    reported_per_tool = Counter(r["Tool"].split(" (")[0] for r in reported)
    # Distinct labels our own extractors found, straight from the counts files.
    recomputed_labels = Counter(r["Tool"].split(" (")[0] for r in master)
    row_total, row_instances = Counter(), {}
    col_total, human, lineages = Counter(), Counter(), {}
    for r in scheme:
        v = num(r["Count"])
        row_total[r["Row"]] += v
        row_instances.setdefault(r["Row"], set()).add(r["Tool"])
        col_total[r["Tool"]] += v
        lineages.setdefault(r["Tool"], set()).add(r["Group"])
        if r["Row"] == "Homo sapiens":
            human[r["Tool"]] += v
    human_share = {t: human[t] / col_total[t] for t in col_total}

    # A share of one instance's own records. HostNet is two instances drawn in
    # one column, and the Results quote the column, so its two are summed here
    # and nowhere else.
    lineage = Counter()
    for r in scheme:
        lineage[(r["Tool"], r["Group"])] += num(r["Count"])

    def lineage_share(tool: str, group: str) -> str:
        cols = [t for t in col_total if t.split(" (")[0] == tool]
        got = sum(lineage[(t, group)] for t in cols)
        return f"{100 * got / sum(col_total[t] for t in cols):.1f}%"

    # Every spelling under which one species reaches the matrix, and how many
    # instances write it that way.
    dog_spellings = {}
    for r in data["label_trace"]:
        if r["Row"] == "Canis lupus":
            dog_spellings.setdefault(r["Original_label"], set()).add(r["Tool"])

    # The low-confidence labels, which Supplementary S2 lists one by one.
    low = [r for r in master if r["Mapping_confidence"] == "low" and r["Status"] != "EXCL"]

    def low_records(tool: str, *labels: str) -> int:
        return round(sum(num(r["Count"]) for r in low
                         if r["Tool"] == tool and r["Original_label"] in labels))

    # Where the host was hardest to determine. "No host" is the label resolving
    # to Unknown host, which is not the same as a label giving a class and no
    # species: the second still places the record, only coarsely.
    no_host = [r for r in included if r["Terminal_category"] == "Unknown host"]
    class_only = [r for r in included if "species not recorded" in r["Original_label"]]
    multi_host = Counter()
    for r in included:
        if r["Potential_double_count"] == "Yes":
            multi_host[r["Tool"]] += num(r["Count"])
    vector_fallback = read("species_matrix_vector_fallback.csv")

    # VPF-Class counts profiles. Its eukaryotic profiles are what the figure
    # draws, its prokaryotic ones are the label excluded as out of scope, and
    # the two together are the profiles clearing the 50% membership cut.
    vpf_euk = sum(num(r["Count"]) for r in included if r["Tool"] == "VPF-Class")
    vpf_prok = sum(num(r["Count"]) for r in master
                   if r["Tool"] == "VPF-Class" and r["Status"] == "EXCL")

    def filled(column: str) -> int:
        return sum(1 for r in data["manifest"]
                   if (r[column] or "").strip().upper() not in ("", "MISSING", "NA", "N/A"))
    carnivore_total = sum(row_total[c] for c in CARNIVORE_ROWS)
    standalone = [r["Row"] for r in data["general_scheme_row_fate"]
                  if r["Fate"] == "standalone_species"]
    group_of = {r["Row"]: r["Group"] for r in species}
    # Unit-free statistics: which instances name a category, and how much of one
    # instance's own records a cell is. Nothing here crosses a counting unit.
    category_instances, breadth_per_instance = {}, Counter()
    for r in scheme:
        if num(r["Count"]) > 0:
            category_instances.setdefault(r["Row"], set()).add(r["Tool"])
            breadth_per_instance[r["Tool"]] += 1
    carnivore_cells = {}
    for r in scheme:
        if r["Row"] in CARNIVORE_ROWS and num(r["Count"]) > 0:
            carnivore_cells.setdefault(r["Tool"], {})[r["Row"]] = num(r["Count"])
    carnivore_share = {t: d.get("Canis lupus", 0) / sum(d.values()) for t, d in carnivore_cells.items()}
    dog_largest = sum(1 for d in carnivore_cells.values() if max(d, key=d.get) == "Canis lupus")
    wild_cells = [100 * num(r["Count"]) / col_total[r["Tool"]] for r in scheme
                  if r["Row"] in WILD_SPECIES and num(r["Count"]) > 0]
    displayed_species = {r["Row"] for r in species if r["Rank"] == "species"}
    pooled_species = {r["original_entity"] for r in data["harmonization_provenance"]
                      if r["mapping_method"] == "below_materiality_bar"}

    # Algae live in the Plants LINEAGE but are their own category, so a lineage
    # test would quietly fold them into the plant count.
    fate = {r["Row"]: r["Final_category"] for r in data["general_scheme_row_fate"]}

    def kingdom_species(group: str) -> set:
        return {r["Row"] for r in species
                if r["Group"] == group and r["Rank"] == "species"
                and fate.get(r["Row"]) != "Algae"}

    def algal_species() -> set:
        return {r["Row"] for r in species
                if r["Rank"] == "species" and fate.get(r["Row"]) == "Algae"}

    return {
        "mapping records": len(master),
        "included mapping records": len(included),
        "high confidence records": conf["high"],
        "medium confidence records": conf["medium"],
        "low confidence records": conf["low"],
        "high confidence share": f"{100 * weight['high'] / total_weight:.1f}%",
        "medium confidence share": f"{100 * weight['medium'] / total_weight:.1f}%",
        "low confidence share": f"{100 * weight['low'] / total_weight:.1f}%",
        "excluded source labels": len(excluded),
        "host entities": len({r["Row"] for r in species}),
        "display categories": len({r["Row"] for r in scheme}),
        "observations": round(sum(num(r["Count"]) for r in included)),
        "populated cells": sum(1 for r in scheme if num(r["Count"]) > 0),
        "matrix cells": len({r["Row"] for r in scheme}) * len(tools),
        "dataset instances": len(instances),
        "tools": len(tools),
        "plant species": len(kingdom_species("Plants")),
        "algal species": len(algal_species()),
        "fungal species": len(kingdom_species("Fungi")),
        "instances naming a plant species": len(
            {r["Tool"] for r in species
             if r["Group"] == "Plants" and r["Rank"] == "species" and num(r["Count"]) > 0}),
        "categories with no threshold": sweep[1],
        "DeePaC-vir categories populated": populated["DeePaC-vir"],
        "RNAVirHost labels carried": carried["RNAVirHost"],
        "RNAVirHost categories populated": populated["RNAVirHost"],
        **({} if is_excluded("HostClassifier") else {"HostClassifier labels carried": carried["HostClassifier"]}),
        "VIDHOP categories populated": populated["VIDHOP"],
        "sequence-counting instances": units["seq"],
        "taxon-counting instances": units["taxon"],
        "high confidence share, unweighted": f"{100 * conf['high'] / len(included):.1f}%",
        "medium confidence share, unweighted": f"{100 * conf['medium'] / len(included):.1f}%",
        "low confidence share, unweighted": f"{100 * conf['low'] / len(included):.1f}%",
        "VIDHOP share of observations": f"{100 * vidhop / total_weight:.1f}%",
        "species names recovered": len(displayed_species | pooled_species),
        "species drawn as their own entity": len(displayed_species),
        "species pooled by the materiality bar": len(pooled_species),
        "residual rows absorbing them": len({r["harmonized_entity"] for r in data["harmonization_provenance"]
                                             if r["mapping_method"] == "below_materiality_bar"}),
        "plant species names recovered": len(kingdom_species("Plants")) + len(
            {r["original_entity"] for r in data["harmonization_provenance"]
             if r["mapping_method"] == "below_materiality_bar"
             and r["harmonized_entity"].startswith("Plants ")}),
        "fungal species names recovered": len(kingdom_species("Fungi")) + len(
            {r["original_entity"] for r in data["harmonization_provenance"]
             if r["mapping_method"] == "below_materiality_bar"
             and r["harmonized_entity"].startswith("Fungi ")}),
        "categories named by 11 instances": sum(1 for v in category_instances.values() if len(v) == 11),
        "median instances per category": sorted(len(v) for v in category_instances.values())[
            len(category_instances) // 2],
        "categories named by one instance": sum(1 for v in category_instances.values() if len(v) == 1),
        "narrowest category breadth": min(breadth_per_instance.values()),
        "widest category breadth": max(breadth_per_instance.values()),
        "instances with any carnivore records": len(carnivore_share),
        "instances where the dog is the largest carnivore row": dog_largest,
        "largest within-instance dog share of carnivores": f"{100 * max(carnivore_share.values()):.1f}%",
        "wild-species cells": len(wild_cells),
        "wild-species cells at 1% or less of their instance": sum(1 for v in wild_cells if v <= 1.0),
        "largest within-instance wild-species share": f"{max(wild_cells):.1f}%",
        "instances naming amphibians": len(category_instances.get("Amphibia", ())),
        "instances naming reptiles": len(category_instances.get("Reptilia", ())),
        "SPHAK duplicated accessions": len(data["sphak_duplicates"]),
        "SPHAK redundant rows": sum(int(r["extra_rows"]) for r in data["sphak_duplicates"]),
        "SPHAK observations": round(sphak_total),
        "SPHAK observations if deduplicated":
            round(sphak_total) - sum(int(r["extra_rows"]) for r in data["sphak_duplicates"]),
        "SPHAK duplicate share":
            f"{100 * sum(int(r['extra_rows']) for r in data['sphak_duplicates']) / sphak_total:.1f}%",
        "authority checks performed": len(data["authority_checks"]),
        "entities carrying a taxid": len({r["harmonized_entity"] for r in data["harmonization_provenance"]
                                          if r["taxid"] != "MISSING"}),
        "matrix occupancy": f"{100 * len(scheme) / (n_categories * len(tools)):.1f}%",
        "VIDHOP reported labels": reported_per_tool["VIDHOP"],
        "VIDHOP labels in the recompute": recomputed_labels["VIDHOP"],
        "Host Taxon Predictor reported labels": reported_per_tool["Host Taxon Predictor"],
        "Host Taxon Predictor categories populated": populated["Host Taxon Predictor"],
        "instances naming Homo sapiens": len(row_instances["Homo sapiens"]),
        "instances naming Canis lupus": len(row_instances["Canis lupus"]),
        "Canis lupus spellings": len({r["Original_label"] for r in data["label_trace"]
                                      if r["Row"] == "Canis lupus"}),
        "wild species clearing the threshold": len(WILD_SPECIES & set(standalone)),
        "instances at 40% human or more": sum(1 for s_ in human_share.values() if s_ >= 0.40),
        "instances at 12% human or less": sum(1 for s_ in human_share.values() if s_ <= 0.12),
        "instances with no human records": sum(1 for s_ in human_share.values() if s_ == 0),
        "widest lineage coverage": max(len(v) for v in lineages.values()),
        "narrowest lineage coverage": min(len(v) for v in lineages.values()),
        "instances naming a fungal species": len(
            {r["Tool"] for r in species if r["Row"] in kingdom_species("Fungi") and num(r["Count"]) > 0}),
        "instances naming a mammal species": len(
            {r["Tool"] for r in species if r["Group"] == "Mammals" and r["Rank"] == "species"
             and num(r["Count"]) > 0}),
        "excluded observations": round(sum(num(r["Count"]) for r in excluded)),
        "non-eukaryotic excluded labels": sum(
            1 for r in excluded if r["Detailed_scheme"] == "Excluded (non-eukaryotic)"),
        "VirHostPRED flagged positive-class records": flagged["total"],
        "VirHostPRED Staphylococcus phage 6ec records": flagged["Staphylococcus phage 6ec"],
        "VirHostPRED IAS virus records": flagged["IAS virus"],
        "retained species": fate_counts["standalone_species"],
        "explicit vector mappings": fate_counts["vector_or_crustacea_rollup"],
        "genus-rule vector mappings": fate_counts["vector_genus_fallback"],
        "entities mapped to a higher rank": fate_counts["taxon_promoted"],
        "entities used unchanged": fate_counts["detailed_scheme_direct"],
        "display headers": len(header_rows),
        "drawn rows": len(data["row_meta"]),
        "categories at threshold 5": sweep[5],
        "species clearing the bar at threshold 5": sweep_clearing[5],
        "standalone species at threshold 5": sweep_species[5],
        "categories at threshold 7": sweep[7],
        "standalone species at threshold 7": sweep_species[7],
        "sequence-counted observations": round(per_unit["seq"]),
        "taxon-counted observations": round(per_unit["taxon"]),
        "deduplicated-pool observations": round(per_unit["dedup"]),
        "profile-counted observations": round(per_unit["profile"]),
        **({} if is_excluded("HostClassifier") else
           {"HostClassifier human share": f"{100 * human_share['HostClassifier']:.1f}%"}),
        "DeepHoF human share": f"{100 * human_share['DeepHoF']:.1f}%",
        "RNAVirHost plant share": lineage_share("RNAVirHost", "Plants"),
        "DeePaC-vir plant share": lineage_share("DeePaC-vir", "Plants"),
        "HostNet invertebrate share": lineage_share("HostNet", "Invertebrates"),
        "instances writing Canis lupus": len(dog_spellings["Canis lupus"]),
        "instances writing Canis lupus familiaris": len(dog_spellings["Canis lupus familiaris"]),
        "instances writing Canis familiaris": len(dog_spellings["Canis familiaris"]),
        "raw source files": len(data["manifest"]),
        "raw files with a resolvable URL": filled("source_url"),
        "raw files with no retrieval date": len(data["manifest"]) - filled("retrieved"),
        "raw files whose published copy was re-fetched": filled("url_verified"),
        **({} if is_excluded("HostClassifier") else
           {"HostClassifier unrecorded-host records":
            low_records("HostClassifier", "Other (species not recorded)")}),
        **({} if is_excluded("HostClassifier") else
           {"HostClassifier cell-culture records":
            low_records("HostClassifier", "cell culture", "Cell Culture", "Cell culture")}),
        "VirHostPRED negative-class records":
            low_records("VirHostPRED", "NOT Homo sapiens (negative class)"),
        "GIVAL post-hoc groupings carrying no count":
            sum(1 for r in low if r["Tool"] == "GIVAL" and not r["Count"].strip()),
        "record-type phrasings across the releases":
            len({r["dataset_size_unit"] for r in data["tool_metadata"]}),
        "records naming no host": round(sum(num(r["Count"]) for r in no_host)),
        "instances naming no host": len({r["Tool"] for r in no_host}),
        **({} if is_excluded("HostClassifier") else
           {"HostClassifier records naming no host":
            round(sum(num(r["Count"]) for r in no_host if r["Tool"] == "HostClassifier"))}),
        "records giving a class but no species":
            round(sum(num(r["Count"]) for r in class_only)),
        "vector-annotation records":
            round(sum(num(r["Count"]) for r in vector_fallback)),
        "wholly vector-annotation records":
            round(sum(num(r["Count"]) for r in vector_fallback if r["Wholly_vector"] == "Yes")),
        "RNAVirHost multi-host records": round(multi_host["RNAVirHost"]),
        "DeepHoF multi-host records": round(multi_host["DeepHoF"]),
        "VPF-Class profiles in the genus table":
            round(num(next(r["dataset_size"] for r in data["tool_metadata"]
                           if r["tool"] == "VPF-Class"))),
        "VPF-Class profiles clearing the 50% cut": round(vpf_euk + vpf_prok),
        "VPF-Class profiles with a eukaryotic host genus": round(vpf_euk),
        "VPF-Class profiles with a prokaryotic host genus": round(vpf_prok),
    }


def report_values(found: dict) -> list:
    width = max(len(k) for k in CLAIMED)
    bad = []
    for key, claim in CLAIMED.items():
        if key not in found and any(t in key for t in excluded_instances()):
            print(f"SKIP  {key:<{width}}  instance excluded from the analysis")
            continue
        got = found[key]
        ok = got == claim
        print(f"{'OK ' if ok else 'BAD'}  {key:<{width}}  stated {str(claim):>9}   "
              f"recomputed {str(got):>9}")
        if not ok:
            bad.append(key)
    return bad


def report_instance_overlap(scheme: list) -> list:
    """The occupancy denominator is tools, not dataset instances, which only
    holds while a tool's instances populate disjoint categories."""
    per_instance: dict[str, set] = {}
    for r in scheme:
        if num(r["Count"]) > 0:
            per_instance.setdefault(r["Tool"], set()).add(r["Row"])

    bad = []
    for tool in sorted({t.split(" (")[0] for t in per_instance}):
        parts = [rows for inst, rows in per_instance.items()
                 if inst.split(" (")[0] == tool]
        if len(parts) > 1:
            overlap = set.intersection(*parts)
            state = "disjoint" if not overlap else f"OVERLAP {sorted(overlap)}"
            print(f"\n{tool} spans {len(parts)} dataset instances; their categories are {state}.")
            if overlap:
                bad.append(f"{tool} instance overlap")
                print("  Combining its columns would change the populated-cell count, so "
                      "the stated occupancy cannot use a per-tool denominator.")
    return bad


# Manuscript-facing prose the numbers must agree with. Files carrying an
# explicit superseded or not-re-verified banner are deliberately absent: they are
# marked in their own first lines and are not cited from.
MANUSCRIPT_FILES = ("manuscript_host_general_scheme.md",
                    "methods_3_3_host_label_harmonization.md", "results_section.md",
                    "supplementary_methods_host_harmonization.md",
                    "figure_captions.md")
# Values from earlier builds. Any of these reappearing in manuscript prose means
# a file has drifted back, or a new file was written from an old draft.
STALE_TOKENS = {
    r"\b14 tools\b": "14 tools (the build had 17)",
    r"\b15 tools\b": "15 tools (the build had 17)",
    r"\b15 datasets\b|fifteen datasets": "15 datasets (there are 18 instances)",
    r"\b15 dataset instances\b": "15 dataset instances (there are 18)",
    r"580,438": "580,438 observations (the total is 603,953)",
    r"292 of 700|\b292\b of \b700\b": "292 of 700 cells (it is 349 of 850)",
    r"41\.7\s?%": "41.7% occupancy (it is 41.1%)",
    r"13 of the 1[45]": "13 of the 14/15 tools",
    r"\b1,085 rows\b": "1,085 species-matrix rows (there are 1,513)",
    r"\b34 categories\b": "34 display categories (there are 50)",
    r"\b5,777\b": "5,777 label records (there are 8,076)",
    r"\b56 rows\b": "56 drawn rows (there are 58)",
    r"\b562 (of them )?non-eukaryotic": "562 non-eukaryotic labels (there are 563)",
    # This work carries one figure. A reference to any other letter is a leftover
    # from the ten that are now legacy, and points the reader at nothing.
    r"Figure (?!Y\b)[A-Z]\b": "a reference to a figure that is not Figure Y",
}


def check_provenance_coverage(data: dict) -> list:
    """The two provenance tables are written by their own scripts and are not
    part of run_all.py, so nothing else would notice them going stale."""
    bad = []
    entities = {r["Row"] for r in data["species_matrix"]}
    covered = {r["harmonized_entity"] for r in data["harmonization_provenance"]}
    if entities - covered:
        n = len(entities - covered)
        print(f"BAD  host_harmonization_provenance.csv misses {n} host entities -- rerun "
              f"build_host_harmonization_provenance.py")
        bad.append("taxonomy provenance stale")
    unclassified = [r for r in data["harmonization_provenance"] if r["mapping_status"] == "unclassified"]
    if unclassified:
        print(f"BAD  host_harmonization_provenance.csv leaves {len(unclassified)} pairs unattributed "
              f"to any curation rule, e.g. {unclassified[0]['original_entity']!r}")
        bad.append("unattributed harmonization")
    if not bad:
        print(f"OK   provenance tables cover all {len(entities)} host entities and "
              f"{len(data['virhostpred_flagged'])} flagged records")
    return bad


def check_manuscript_prose() -> list:
    """A number can rot in prose without any table changing, which is how the
    confidence shares in methods_results_general_scheme_R.md went stale unseen.
    This scans the manuscript-facing files for values from earlier builds."""
    root = SC.parent
    bad = []
    for name in MANUSCRIPT_FILES:
        path = root / name
        if not path.exists():
            print(f"BAD  manuscript file missing: {name}")
            bad.append(f"{name} missing")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, description in STALE_TOKENS.items():
            for m in re.finditer(pattern, text):
                line = text.count("\n", 0, m.start()) + 1
                print(f"BAD  {name}:{line} carries a stale value -- {description}")
                bad.append(f"{name}:{line}")
    if not bad:
        print(f"OK   no stale value from an earlier build in "
              f"{len(MANUSCRIPT_FILES)} manuscript files")
    return bad


def main() -> int:
    data = load_data()
    bad = report_values(recompute(data))
    bad += report_instance_overlap(data["general_scheme_matrix"])
    print()
    bad += check_provenance_coverage(data)
    bad += check_manuscript_prose()

    print()
    if bad:
        print(f"FAIL: {len(bad)} stated value(s) disagree with the data: {bad}")
        return 1
    print(f"PASS: all {len(CLAIMED)} stated values reproduce from the committed tables.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
