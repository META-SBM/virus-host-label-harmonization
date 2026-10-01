# -*- coding: utf-8 -*-
"""Shared registry: the category vocabulary, the palettes and the dataset scope.

Data only. It imports nothing from this project, so every script can import it
without pulling a figure or a builder in behind it.
"""
import csv
import os

# Row order on the heatmaps, and the list of valid Detailed_scheme values that
# build_master_labels.py validates against.
CATS = [
    ("Humans", "Mammals"), ("Non-human primates", "Mammals"),
    ("Humans + non-human primates", "Mammals"),
    ("Bats", "Mammals"),
    ("Rodents", "Mammals"), ("Ungulates", "Mammals"),
    ("Swine (pig)", "Mammals"),
    ("Carnivores", "Mammals"),
    ("Other mammals", "Mammals"), ("Other/unresolved mammals", "Mammals"),
    ("Non-human (undifferentiated)", "Mammals"),
    ("Birds", "Non-mammalian vertebrates"),
    ("Fish", "Non-mammalian vertebrates"), ("Reptiles", "Non-mammalian vertebrates"),
    ("Amphibians", "Non-mammalian vertebrates"), ("Unresolved vertebrates", "Non-mammalian vertebrates"),
    ("Insects", "Invertebrates"), ("Arachnids", "Invertebrates"),
    ("Other invertebrates", "Invertebrates"), ("Unresolved invertebrates", "Invertebrates"),
    ("Unresolved arthropods", "Invertebrates"),
    ("Plants", "Plants"),
    # Neither plants, fungi nor animals, and not unknown either: most are named
    # to species.
    ("Algae", "Algae"),
    ("Protists & oomycetes", "Protists & oomycetes"),
    ("Fungi", "Fungi"),
    ("Unresolved eukaryote", "Unknown/Excluded"),
    ("Multiple / protist", "Unknown/Excluded"),
    ("Unknown host", "Unknown/Excluded"),
]
cat_labels = [c[0] for c in CATS]
cat_groups = [c[1] for c in CATS]

# Renames only.
DETAILED_SCHEME_REMAP = {
    "Unresolved (non-human, undifferentiated)": "Non-human (undifferentiated)",  # VirHostPRED's synthetic negative class
    "Unresolved (multiple/protist)": "Multiple / protist",                        # Zoonotic rank's MULTIPLE/Protist
    "Humans + Non-human primates (combined)": "Humans + non-human primates",      # shortened for display
    "Swine (pig, epidemiological aggregate)": "Swine (pig)",                      # shortened for display
    # A Detailed_scheme string matching no CATS key is dropped outright rather
    # than folded anywhere, so these two need the mapping.
    "Other mammals (Perissodactyla)": "Other mammals",          # EvoMIL/Equus caballus, 54 records -- order annotation, same category as every other "Other mammals" row
    "Other/unresolved invertebrates": "Unresolved invertebrates",  # UniVH's "Animalia (other, no class match)", 231 records -- "no class match" means genuinely unidentified, same character as DeepHoF's blanket "invertebrate", not the specific-but-uncategorized "Other invertebrates" bucket
    # Excluded rows need a valid category too: the main heatmap draws them as
    # "present, no count" rather than dropping them.
    "Unknown vector": "Unknown host",       # ViralHostPredictor's "unknown (vector)" (EXCL, 19 records) -- unidentified pool on the vector axis, same character as "Unknown host" on the host axis
    "Unresolved (other)": "Unknown host",   # HostClassifier's "Other (EXCL)" (999 records) -- generic unresolved/excluded catch-all, closest existing bucket
}

# Lineage colours, and nothing else: the record-type and molecule-type swatches
# are separate, so a lineage can be recoloured without touching them.
GROUP_COLOR = {
    "Mammals": "#1e88e5",
    "Non-mammalian vertebrates": "#f4511e",
    "Invertebrates": "#8e0000",
    "Plants": "#00bfa5",
    "Algae": "#64dd17",                   # 115 from its nearest neighbour
    "Protists & oomycetes": "#7b1fa2",    # 96 from Fungi, its nearest lineage
    "Fungi": "#d81b8c",
    "Unknown/Excluded": "#78909c",        # not a real taxon, neutral
}

# Counting units and the swatch each gets on the per-tool track.
RECTYPE_COLOR = {
    "seq": "#1baf7a",       # CAT_AQUA
    "taxon": "#eda100",     # CAT_YELLOW
    "dedup": "#4a3aa7",     # CAT_VIOLET
    # Measured against every swatch and lineage colour already on the figures:
    # nearest neighbour 95 units, wider than several pairs already in use.
    "profile": "#8a5a2b",
}
RECTYPE_LABEL = {
    "seq": "Sequence-level (per isolate)",
    "taxon": "Virus-taxon-level (per species)",
    "dedup": "Deduped species pool",
    # Named as bluntly as it can be: this one does not count viruses.
    "profile": "Protein-family profile (not a virus)",
}

# What a tool reads, the second swatch under every column.
MOLTYPE_COLOR = {
    "nt": "#2a78d6",      # CAT_BLUE
    "aa": "#e34948",      # CAT_RED
    "mixed": "#e87ba4",   # CAT_MAGENTA
    "meta": "#c3c2b7",    # BASELINE
}
MOLTYPE_LABEL = {
    "nt": "Nucleotide sequence",
    "aa": "Protein sequence",
    "mixed": "Mixed nt + protein",
    "meta": "Accession metadata only",
}

# Tools whose article states no fixed list of host labels, so the "labels
# reported by the study" bar has nothing to draw and is left empty rather than i
NO_REPORTED_LABEL_LIST = {"VPF-Class"}

# Cross-tool comparability caveat, shown on every heatmap-style figure
# (make_heatmap.py, make_species_heatmap.py, make_general_scheme_heatmap.py).
COMPARABILITY_FOOTNOTE = (
    "14 tools shown as 15 columns -- HostNet trains separately on\n"
    "Rabies/VIPHOD data and on Flavivirus data (2 dataset instances,\n"
    "1 tool). Read across a row for breadth (which tools cover this\n"
    "host) and within a column for composition, not raw counts\n"
    "between columns -- each tool counts records at its own\n"
    "resolution (e.g. sequence, species, or strain), and the scope of\n"
    "data each tool reports (training data only, training+test, or\n"
    "training+validation+test) also varies by tool -- see the\n"
    "accompanying supplementary tables for the full per-tool breakdown."
)

# Per-tool dataset scope, read off each tool's own source files.
DATASET_SCOPE = {
    "DeepHoF": ("train+test", "train_genome_info + test_genome_info sheets summed; no val sheet in the source file. This is the entirety of what the tool released -- no fuller pool exists to compare it against"),
    "RNAVirHost": ("full_dataset", "virus_label(1).csv -- one labeled pool. CORRECTED 2026-09-09: an earlier note here said the tool's public GitHub repo was empty. It is not. github.com/GreyGuoweiChen/VirHost holds 281 files, and rnavirhost/virus/virus_label.csv is byte-identical to the file used here. What the earlier note got right stands: that repository carries no train/val/test structure for this pool, only per-order data_label.csv files under rnavirhost/model/, so there is still no split to apply"),
    "Host Taxon Predictor": ("full_dataset", "all_viruses_with_desired_attributes.dump (5,282 records) -- the complete labeled pool. A separate learn/test split does exist in the tool's own supplementary materials (attributes_learn.dump/attributes_test.dump, plus an ids_test.dump/ids_test list of 488 held-out accession IDs), but is not used here -- see policy note above"),
    "EvoMIL": ("full_dataset", "published Table_S2 / virushostdb_latest.tsv -- one summary table. The tool's GitHub repo ships 5-fold CV example dataloaders for only 2 demonstration species (Mus musculus, Bacillus cereus), not a dataset-wide split -- no train-only extraction is possible even in principle, let alone available"),
    "VIDHOP": ("train+val+test", "Y_train/Y_val/Y_test.csv summed across all 3 splits and all 3 sub-datasets (Influ/Rabies/Rota) -- matches the tool's own reported grand total (263,962) exactly. The tool's GitHub repo root also has a small X.txt/Y.txt (11,685 records) -- checked and it is a CLI usage demo for the 'make_dataset' command, not a fuller pool (11,685 << 263,962; the real training data is hosted on OSF, which is exactly what train_data.zip already provides)"),
    "HostNet (Flavivirus)": ("full_dataset", "flavivirus.csv (9,626 records) -- the complete labeled pool. A genuine train/val/test split does exist for this exact data in the tool's own repo (X/Y_train.csv 9,562 + X/Y_val.csv 32 + X/Y_test.csv 32, summing exactly to 9,626), but is not used here -- see policy note above"),
    "HostNet (Rabies, VIPHOD)": ("train+test", "Y_train.csv + Y_test.csv only -- val split exists in the source but is deliberately excluded (verified: including it breaks the tool's own reported total). train+test together is the complete labeled pool the tool released for this dataset, so this is consistent with the full_dataset tools' policy, not an exception to it"),
    "DeePaC-vir": ("train+val+test", "VHDB_1_folds_human.rds + VHDB_1_folds_all_nhuman.rds (Zenodo 10.5281/zenodo.4312525) -- the two Virus-Host DB tables the study's read sets were drawn from, 9,496 records matching its reported total. fold1 carries the study's own train/val/test split, combined here as for every other tool with a released split. The same deposit's nested eukarya/metazoa/chordata non-human tables are SUBSETS of all_nhuman, used to vary the negative class between training settings, and are deliberately not read -- counting them would count the same virus several times. The multi-gigabyte simulated read FASTAs in the deposit carry no host annotation and are not the label source"),
    "MosViR": ("full_dataset", "mosquito_500.fasta.xz + arboviruses_500bp.fasta.xz (Zenodo 10.5281/zenodo.10975789), 500 bp fragments collapsed to 27,002 source sequences. The 500 bp set is the superset because a short sequence appears in no longer fragment set. The third released class, `other viruses` (620,553 source sequences), is NOT read: it is the not-mosquito-associated background for the first classification step, asserts no host, and its truncated accessions cannot be resolved to check it against the review's eukaryotic scope. Identifiers throughout the release are truncated accessions, so MosViR's records carry no resolvable viral taxonomy and cannot enter the ICTV taxonomic-breadth analysis"),
    "MENB": ("train_only", "article's own Supplementary Figure 1A, explicitly train counts only -- this is the entirety of what the article released for this dataset"),
    "ViralHostPredictor": ("full_dataset", "BabayanEtAl_VirusData.csv -- one labeled pool. The tool's GitHub repo confirms no persisted train/test split file was ever released, only R scripts that cross-validate in memory at runtime with no saved split output"),
    "Zoonotic rank": ("full_dataset", "AllInternalData_Checked.csv (1,258 records) -- one labeled pool. The tool's own repo defines a holdout-selection script (SelectHoldoutData.R), but its Makefile invokes it with --holdoutProportion 0 and an explicit code comment ('Holdout not currently used -- not enough data') -- the published analysis itself never held out a test set, so there is no train-only subset to use even in principle"),
    "HostClassifier": ("full_dataset", "virus-host-datasets_v4.5.0.csv (58,058 records) -- the complete labeled database dump. A separate HuggingFace-style train.parquet (51,934 records, 89%) exists with the same standardized_host column, but is not used here -- see policy note above"),
    "VirHostPRED": ("full_dataset", "reps70.fasta (2,127 sequences, human-infecting/positive class -- CD-HIT clustered at 70% identity from an initial ~5,200 NCBI RefSeq pool) + random_dataset_1.fasta (2,127 sequences, non-human/negative class -- randomly undersampled with a fixed seed from a 10,635-sequence pool to match the positive class size, per the article's own Table S2). Corrected from an earlier, wrong 'no_dataset_file' classification -- these 2 FASTA files were sitting in manual_downloads/VirHostPRED/ all along and directly verified by counting sequences (grep -c '^>'), not merely inferred from article text. The counts (2,127/2,127) were already correct either way -- this only fixes the provenance, not the numbers. Both classes are already explicitly balanced/undersampled by the tool's own published method (Table S2), not a train/test split -- there is no fuller pool to fall back to for the negative class beyond this 2,127-sequence random sample, so full_dataset here means exactly what VirHostPRED itself released"),
    "SPHAK": ("train_only", "animal_train.csv + plant_train.csv (13,570 rows). Per the tool's own README, 'train' is what builds SPHAK's deployed reference k-mer database, while 'test' and 'out_of_sample' are held out to evaluate it. out_of_sample is a temporal holdout (31 Dec 2024 to 31 May 2025) and is NOT excluded here in any meaningful sense: the article states it was integrated back into the reference database once evaluation was complete, and 77 of its 100 records are already present in the released train files we count. Appending the file would double-count those 77 to gain 23 records and one new host name, Melia dubia, which does not clear the materiality bar. SPHAK released no validation split: 93 files in its repository, none matching val/valid/holdout/dev, and the article uses 'validation' only for the out-of-sample holdout and for general corroboration. CORRECTED 2026-09-09 after reading the article (10.1038/s41598-026-52373-2, open access via PMC13365375): an earlier note here claimed 13,570 'matches the tool's own reported total exactly'. It does not. The string 13,570 does not occur in the article, and tool_metadata's value for it traces to original_reported_labels.xlsx, the workbook this project already documents as unverified. What the article does state: the curated animal dataset was 10,965 protein sequences (exactly animal_data_excluding_out_of_sample.csv), and after filtering the animal dataset was 10,207 sequences, 8,165 train and 2,042 test, while the plant dataset was 4,346, 3,476 train and 870 test. plant_train.csv matches its 3,476 exactly. animal_train.csv does NOT match its 8,165: the released file holds 10,094 rows and 9,321 distinct accessions. The article explains the direction of the gap -- out-of-sample data were integrated into the reference database after evaluation was complete -- and 74 of the 90 out_of_sample accessions are indeed present in the released animal_train.csv, so that file appears to be the post-integration state rather than the one the reported evaluation used. The released files are used as released, and this mismatch is reported rather than reconciled by substituting a different file. See Supplementary Methods S5b"),
    "UniVH": ("full_dataset", "dataset.csv (81,874 records) -- the complete labeled pool. The same file carries its own dataset column (train=77,561/val=2,633/test=1,680), but no split filter is applied -- see policy note above"),
    "GIVAL": ("full_dataset", "df_AIV_before_sample.csv (121,753 records) -- the complete pre-split labeled pool, covering 12 host categories (Human/Avian/Swine/Canine/Equine/Fox/Mink/Feline/Ferret/Tiger/Raccoon dog/...). The tool's own published train/test split (its vBERT sampling pipeline, confirmed by direct inspection of the archive hosted on Zenodo) collapses host labels down to Human/Avian only, discarding the other 10 categories -- an independent reason, beyond the uniform-scope policy, to use the complete pool instead"),
    # The first tool in the review with no column at all.
    "VPF-Class": ("full_dataset", "2019_VPF_GenHost_REclassification_new.tsv (bioinfo.uib.es/~recerca/VPF-Class/) -- the complete released genus-level host reclassification, filtered to membership ratio >=50%. The filter is not a subset of a fuller pool in the sense the other entries mean: a profile's shares sum to 100, so above half only one genus can qualify and each profile is counted exactly once. At the article's own operating point for host prediction (ratio 0.3) a profile carries up to three genera and would be counted three times. The counting unit is a protein-family PROFILE, not a virus, and the column carries its own record-type swatch saying so. The five other released tables (domain and family host, three virus-taxonomy tables) are not used: the ranks are reclassified independently and do not nest, so they cannot be combined -- see scripts/assess_vpf_class.py"),
}


# The ordered list of dataset instances every per-tool figure draws as columns.
_LEGACY_COLUMN_ORDER = [
    "RNAVirHost", "Zoonotic rank", "UniVH", "SPHAK", "ViralHostPredictor", "EvoMIL",
    "HostClassifier", "VIDHOP", "HostNet (Rabies, VIPHOD)", "HostNet (Flavivirus)",
    "MENB", "GIVAL", "DeepHoF", "Host Taxon Predictor", "VirHostPRED",
]


def _read(path: str, default: str) -> list:
    """A registry lookup reads only these two committed tables, never a figure
    script: this module must stay importable by anything."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(path or os.path.join(here, default), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))



def excluded_instances(tool_metadata_csv=None) -> set:
    """Tools kept in this tree for provenance but left out of the analysis.

    A tool is excluded by setting include_in_analysis to "no" in
    tool_metadata.csv; its raw files, counts and curation rows stay where they
    are, and every builder drops its rows through this one function.
    """
    return {r["tool"] for r in _read(tool_metadata_csv, "tool_metadata.csv")
            if (r.get("include_in_analysis") or "yes").strip().lower() == "no"}


def is_excluded(instance: str, tool_metadata_csv=None) -> bool:
    """True for an excluded tool and for its dataset instances, e.g. 'X (Y)'."""
    return any(instance == t or instance.startswith(t + " (")
               for t in excluded_instances(tool_metadata_csv))


def dataset_instances(master_labels_csv=None, tool_metadata_csv=None) -> list:
    """Instance names in display order, checked against the harmonized records."""
    dropped = excluded_instances(tool_metadata_csv)
    by_order = [r["tool"] for r in sorted(_read(tool_metadata_csv, "tool_metadata.csv"),
                                          key=lambda r: int(r["order"]))
                if r["tool"] not in dropped]
    present = list(dict.fromkeys(r["Tool"] for r in _read(master_labels_csv, "master_labels.csv")))

    covered = set()
    for tool in by_order:
        kids = [p for p in present if p == tool or p.startswith(tool + " (")]
        if not kids:
            raise SystemExit(f"{tool} is in tool_metadata.csv but has no harmonized records")
        covered.update(kids)
    orphans = [p for p in present if p not in covered]
    if orphans:
        raise SystemExit(f"harmonized records for tools missing from tool_metadata.csv: {orphans}")

    out = [t for t in _LEGACY_COLUMN_ORDER if t in covered]
    stale = [t for t in _LEGACY_COLUMN_ORDER
             if t not in covered and not is_excluded(t, tool_metadata_csv)]
    if stale:
        raise SystemExit(f"display order names instances that no longer exist: {stale}")
    for tool in by_order:
        for kid in [p for p in present if p == tool or p.startswith(tool + " (")]:
            if kid not in out:
                out.append(kid)
    return out


# Dataset size and unit per DATASET INSTANCE, for the figures whose columns are
# instances rather than tools.
INSTANCE_DATASET_SIZE_SPLIT = {
    "HostNet": {"HostNet (Flavivirus)": 9626, "HostNet (Rabies, VIPHOD)": 11685},
}


def dataset_sizes(tool_metadata_csv=None) -> dict:
    """Instance name -> (size, unit), as each study states it."""
    out = {}
    for r in _read(tool_metadata_csv, "tool_metadata.csv"):
        total, unit = int(r["dataset_size"]), r["dataset_size_unit"]
        split = INSTANCE_DATASET_SIZE_SPLIT.get(r["tool"])
        if split is None:
            out[r["tool"]] = (total, unit)
            continue
        if sum(split.values()) != total:
            raise SystemExit(
                f"{r['tool']}: instance sizes {split} do not sum to the {total} "
                "stated in tool_metadata.csv")
        for inst, n in split.items():
            out[inst] = (n, unit)
    return out


def instance_metadata(tool_metadata_csv=None) -> dict:
    """Instance name -> dict of the article-stated facts figures annotate columns with.

    Same source as dataset_sizes(); a tool that released more than one dataset
    gives each of its instances the same counting unit and molecule type, since
    those are properties of how the study works, not of a particular file.
    """
    out = {}
    for r in _read(tool_metadata_csv, "tool_metadata.csv"):
        names = list(INSTANCE_DATASET_SIZE_SPLIT.get(r["tool"], {r["tool"]: None}))
        for name in names:
            out[name] = {"counting_unit": r["counting_unit"],
                         "molecule_type": r["molecule_type"],
                         "molecule_detail": r["molecule_detail"],
                         "endpoint_id": r["endpoint_id"],
                         "endpoint_label": r["endpoint_label"]}
    return out
