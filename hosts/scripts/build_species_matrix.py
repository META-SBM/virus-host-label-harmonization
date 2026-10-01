# -*- coding: utf-8 -*-
"""Species-resolved host matrix: one heatmap row per genuine, unambiguous
taxonomic identity (species where resolvable, else the existing harmonized
category), tagged with its taxonomic rank. Answers "which tools share the
same host species", a question the 27-category heatmap can't show since it
stops at order/class level for most categories.
"""
import os
import re
import pandas as pd

SC = os.path.dirname(os.path.abspath(__file__))
master = pd.read_csv(os.path.join(SC, "master_labels.csv"))
# Status=EXCL rows are placeholders, and every other script reading
# master_labels.csv drops them.
host = master[master["Data_category"].isin(["host", "unclear", "host/vector unresolved"])
              & (~master["Status"].astype(str).str.startswith("EXCL"))].copy()
host["Count"] = pd.to_numeric(host["Count"], errors="coerce").fillna(0)

# VirHostPRED's "NOT Homo sapiens (negative class)" (2127 records) is a
# synthetic, size-matched negative sample for a binary human/non-human
# classifier, not a real biologic

from categories import CATS, DETAILED_SCHEME_REMAP
CAT_GROUP = dict(CATS)
host["Detailed_scheme"] = host["Detailed_scheme"].replace(DETAILED_SCHEME_REMAP)

# Unambiguous common-name -> canonical species/subspecies.
RESOLVE = {
    "Human": "Homo sapiens", "human": "Homo sapiens", "human (-> Homo sapiens)": "Homo sapiens",
    # VPF-Class names hosts at genus level, and genus Homo has one extant
    # species.
    "Homo": "Homo sapiens",
    "Human (train, x4 families)": "Homo sapiens",
    "Homo sapiens (taxid 9606, positive class)": "Homo sapiens",
    "Pig": "Sus scrofa", "Wild Boar": "Sus scrofa", "Swine": "Sus scrofa",
    "Swine (train, x4 families)": "Sus scrofa",
    "Cattle": "Bos taurus",
    "Horse": "Equus caballus",
    "Goat": "Capra hircus",
    "Sheep": "Ovis aries",
    "Chimpanzee": "Pan troglodytes",
    "Raccoon": "Procyon lotor",
    "Cat (all variants combined)": "Felis catus",
    "Dog": "Canis lupus familiaris (dog)",
    "Canis lupus familiaris": "Canis lupus familiaris (dog)",  # HostClassifier's standardized_host omits the "(dog)" suffix used elsewhere
    # Host Taxon Predictor's raw "host" field uses lowercase common names
    # (cleaned of demographic annotations/parenthetical notes, see
    # hostclassifier_standa
    "tomato": "Solanum lycopersicum", "chicken": "Gallus gallus",
    "wheat": "Triticum aestivum", "dog": "Canis lupus familiaris (dog)",
    "swine": "Sus scrofa", "cattle": "Bos taurus", "pig": "Sus scrofa",
    "Cougar": "Puma concolor",
    "Panda": "Ailuropoda melanoleuca",
    "Koala": "Phascolarctos cinereus",
    "Tiger": "Panthera tigris",
    "Ferret": "Mustela putorius furo",
    "Wolverine": "Gulo gulo",
    "Yak": "Bos grunniens",
    "Mouse": "Mus musculus",
    "Rat": "Rattus norvegicus",
    "Rabbit": "Oryctolagus cuniculus",
    "Mink": "Neovison vison",
    "Badger": "Meles meles",
    # GIVAL's record_id-parsed mammal tokens (see
    # hostclassifier_standardized_host_rebuild.md memory note, same "richer info
    # hiding in the raw file" pattern
    "Canine": "Canis lupus familiaris (dog)", "Equine": "Equus caballus",
    "Fox": "Vulpes vulpes", "Feline": "Felis catus",
    "Raccoon dog": "Nyctereutes procyonoides", "Skunk": "Mephitis mephitis",
    "Donkey": "Equus asinus", "Lion": "Panthera leo",
    "Virginia opossum": "Didelphis virginiana", "Polecat": "Mustela putorius",
    "Bobcat": "Lynx rufus",
}


# Tier 2: named higher-rank taxa.
HIGHER = {
    ("Amphibia", "order"): "Amphibia", ("Amphibian", "class"): "Amphibia",
    ("Arachnida", "order"): "Arachnida", ("Arachnida", "class"): "Arachnida",
    ("Chiroptera", "order"): "Chiroptera",
    ("Pterobat (reservoir)", "suborder"): "Chiroptera", ("Vespbat (reservoir)", "suborder"): "Chiroptera",
    ("Pterobat/Vespbat/Chiroptera (combined)", "order"): "Chiroptera",
    ("Bat", "informal biological group"): "Chiroptera",  # unambiguous common name -- all bats are Chiroptera
    ("Aves", "order"): "Aves", ("Aves", "class"): "Aves", ("Avian", "class"): "Aves",
    ("Avian (train, x4 families)", "aggregate group"): "Aves",
    ("Galloanserae (reservoir)", "clade"): "Galloanserae (bird clade)",
    ("Neoaves (reservoir)", "clade"): "Neoaves (bird clade)",
    ("Carnivora", "order"): "Carnivora", ("Carnivore", "order"): "Carnivora", ("Carnivore (reservoir)", "order"): "Carnivora",
    ("Canidae", "informal biological group"): "Canidae",
    ("Feliformia", "informal biological group"): "Feliformia",
    ("Wild Cat", "informal biological group"): "Felis (genus)",
    ("Civet", "informal biological group"): "Viverridae", ("Civets", "informal biological group"): "Viverridae",
    ("Mongoose", "informal biological group"): "Herpestidae",
    ("Seal", "informal biological group"): "Pinnipedia",
    ("Dolphin", "informal biological group"): "Delphinidae",
    ("Bottlenose dolphin", "informal biological group"): "Delphinidae",
    ("Owston's civet", "informal biological group"): "Viverridae",
    ("Bear", "informal biological group"): "Ursidae",
    ("Otter", "informal biological group"): "Lutrinae",
    ("Whale", "informal biological group"): "Cetacea",
    ("Sea Cow", "informal biological group"): "Sirenia",
    ("Hedgehog", "informal biological group"): "Erinaceidae",
    ("Shrew", "informal biological group"): "Soricidae",
    ("Pangolin", "informal biological group"): "Manis (genus)",
    ("Mule", "informal biological group"): "Equus (hybrid: mule)",
    ("Bovids", "informal biological group"): "Bovidae",
    ("Buffalo", "informal biological group"): "Bovidae (buffalo)",
    ("Camel", "informal biological group"): "Camelus (genus)",
    ("Deer", "informal biological group"): "Cervidae",
    ("Ape", "informal biological group"): "Hominoidea",
    ("Lemur", "informal biological group"): "Lemuriformes",
    ("Macaque", "informal biological group"): "Macaca (genus)",
    ("Monkey", "informal biological group"): "Simiiformes (monkey, family unresolved)",
    ("Hamsters", "informal biological group"): "Cricetinae",
    ("Porcupine", "informal biological group"): "Hystricognathi",
    ("Vole", "informal biological group"): "Arvicolinae",
    ("tick", "informal biological group"): "Ixodida",
    ("Mosquito", "informal biological group"): "Culicidae",
    ("Prawn", "informal biological group"): "Caridea",
    ("Penguins", "informal biological group"): "Sphenisciformes",
    ("Fungi", "order"): "Fungi", ("Fungi", "kingdom"): "Fungi",
    ("Insecta", "order"): "Insecta", ("Insecta", "class"): "Insecta", ("Insect", "class"): "Insecta", ("Insect (reservoir)", "class"): "Insecta",
    ("Insects", "informal biological group"): "Insecta",
    ("Reptilia", "order"): "Reptilia", ("Reptile", "class"): "Reptilia", ("Reptile (reservoir)", "class"): "Reptilia",
    ("Lepidosauria", "class"): "Lepidosauria (reptile clade, excl. turtles/crocodiles)",
    ("Rodentia", "order"): "Rodentia", ("Rodent", "order"): "Rodentia", ("Rodent (reservoir)", "order"): "Rodentia",
    ("Rodent", "informal biological group"): "Rodentia",
    ("Artiodactyla", "order"): "Artiodactyla", ("Artiodactyl", "order"): "Artiodactyla", ("Artiodactyl (reservoir)", "order"): "Artiodactyla",
    ("Artiodactyla/Cetartiodactyla", "order"): "Artiodactyla",
    ("Viridiplantae", "order"): "Plantae", ("Plantae", "kingdom"): "Plantae", ("Plant", "kingdom"): "Plantae",
    ("Plant (reservoir)", "kingdom"): "Plantae", ("plant", "kingdom"): "Plantae",
    ("Crustacean", "class"): "Crustacea",
    # HostClassifier's standardized_host column (added when its rows were
    # rebuilt from that column instead of the coarser host_category) reports
    # some taxa a
    ("Aedes", "genus"): "Culicidae", ("Culex", "genus"): "Culicidae",
    ("Simia", "genus"): "Simiiformes (monkey, family unresolved)",
    ("Macaca", "genus"): "Macaca (genus)",
    ("Cervidae", "family"): "Cervidae",
    ("Ixodida", "order"): "Ixodida",
    # Host Taxon Predictor's host field (cleaned common names)
    ("mosquito", "family"): "Culicidae",
    # Same host, same field, same tool, but NCBI returns "unclassified
    # sequences" for these two spellings, so nothing resolved them and they sat
    # in "Unresol
    ("Mosquito-Unknown", "family"): "Culicidae",
    ("unidentified mosquitos", "family"): "Culicidae",
    ("Ornithodoros", "genus"): "Ixodida",
    # SPHAK's raw Host column (self-mapped: large enough family-level bird
    # groups to deserve their own species_matrix row)
    ("Anatidae", "family"): "Anatidae", ("Columbidae", "family"): "Columbidae",
    ("whitetail deer", "informal biological group"): "Cervidae",
    ("masked palm civet", "informal biological group"): "Viverridae",
    ("freshwater atyid shrimp", "infraorder"): "Caridea",
    # RNAVirHost's y|host name (added when its 15 order-level rows were rebuilt
    # from that column: see hostclassifier_standardized_host_rebuild.md).
    ("Culicidae", "family"): "Culicidae",
    # MosViR classifies by host range, not host taxon: a mosquito-specific virus
    # replicates only in mosquito cells, so the mosquito is its host.
    ("mosquito-specific virus", "host-range class"): "Culicidae",
    ("Felidae", "family"): "Feliformia",
    ("Chlorocebus", "genus"): "Chlorocebus (genus)",
    ("Manidae", "family"): "Manis (genus)",
}


# Infraspecific names collapse onto their binomial before counting, so that a
# species is not split across rows by how each study spelled it.
_HYBRID_RE = re.compile(r"\s[xX]\s")
_INFRASPECIFIC_STOP = ("cf.", "aff.")
BINOMIAL_SYNONYM = {
    "Canis familiaris": "Canis lupus",          # domestic dog, older binomial
    # These two are trinomials whose own binomial is NOT the name the species is
    # filed under here, so the generic rule would send them to the wrong row
    # (Cap
    "Capra aegagrus hircus": "Capra hircus",
    "Equus ferus caballus": "Equus caballus",
    "Litopenaeus vannamei": "Penaeus vannamei",   # whiteleg shrimp, older genus
}


# A three-word capitalised name is normally an infraspecific taxon, which is
# what the collapse below is for.
_VIRUS_TAIL = re.compile(r"\b(virus(es)?|viridae|virinae|phage|viroid|satellite)\b", re.I)


def collapse_to_binomial(name):
    if not isinstance(name, str) or not name:
        return name
    if _VIRUS_TAIL.search(name):
        return name
    if name in BINOMIAL_SYNONYM:
        return BINOMIAL_SYNONYM[name]
    if _HYBRID_RE.search(name):
        return name
    parts = re.sub(r"\s*\(.*?\)", "", name).split()
    if len(parts) < 3 or not parts[0][:1].isupper():
        return name
    if any(p in _INFRASPECIFIC_STOP for p in parts):
        return name
    return f"{parts[0]} {parts[1]}"


def resolve_species(row):
    label = row["Original_label"]
    if row["Label_level"] == "species":
        resolved = label if label not in RESOLVE else RESOLVE[label]
    else:
        resolved = RESOLVE.get(label)
    return collapse_to_binomial(resolved)


def resolve_higher(row):
    return HIGHER.get((row["Original_label"], row["Label_level"]))


host["Resolved_species"] = host.apply(resolve_species, axis=1)
host["Resolved_higher"] = host.apply(resolve_higher, axis=1)

RANK_OF = {
    "Amphibia": "class", "Arachnida": "class", "Chiroptera": "order", "Aves": "class",
    "Galloanserae (bird clade)": "clade", "Neoaves (bird clade)": "clade", "Carnivora": "order",
    "Canidae": "family", "Feliformia": "suborder", "Felis (genus)": "genus", "Viverridae": "family",
    "Ursidae": "family", "Lutrinae": "subfamily",
    "Herpestidae": "family", "Pinnipedia": "suborder", "Delphinidae": "family", "Cetacea": "infraorder",
    "Sirenia": "order", "Erinaceidae": "family", "Soricidae": "family", "Manis (genus)": "genus",
    "Equus (hybrid: mule)": "hybrid", "Bovidae": "family", "Bovidae (buffalo)": "family",
    "Camelus (genus)": "genus", "Cervidae": "family", "Hominoidea": "superfamily", "Lemuriformes": "infraorder",
    "Macaca (genus)": "genus", "Simiiformes (monkey, family unresolved)": "infraorder", "Cricetinae": "subfamily",
    "Chlorocebus (genus)": "genus", "Anatidae": "family", "Columbidae": "family",
    "Hystricognathi": "infraorder", "Arvicolinae": "subfamily", "Ixodida": "order", "Culicidae": "family",
    "Caridea": "infraorder", "Sphenisciformes": "order", "Fungi": "kingdom", "Insecta": "class",
    "Reptilia": "class", "Lepidosauria (reptile clade, excl. turtles/crocodiles)": "clade", "Rodentia": "order",
    "Artiodactyla": "order", "Plantae": "kingdom", "Crustacea": "subphylum",
}

# Materiality bar: a resolved species only gets its own row if shared by >=2
# tools or has >=100 records in at least one tool.
sp_rows = host[host["Resolved_species"].notna()].copy()
tool_counts = sp_rows.groupby("Resolved_species")["Tool"].nunique()
max_count = sp_rows.groupby("Resolved_species")["Count"].max()
material = set(tool_counts[tool_counts >= 2].index) | set(max_count[max_count >= 100].index)

# A species that fails the materiality bar normally falls back to its raw
# category's generic residual ("Insects (not resolved to species)"), but a few s
LOW_MATERIALITY_FALLBACK = {
    "Aedes albopictus": ("Culicidae", "family"),
}

sp_rows["Row"] = sp_rows["Resolved_species"]
sp_rows["Rank"] = "species"
fails_bar = ~sp_rows["Row"].isin(material)
override = sp_rows["Row"].map(LOW_MATERIALITY_FALLBACK)
has_override = fails_bar & override.notna()
sp_rows.loc[has_override, "Rank"] = override[has_override].map(lambda t: t[1])
sp_rows.loc[has_override, "Row"] = override[has_override].map(lambda t: t[0])
sp_rows.loc[fails_bar & ~has_override, "Row"] = None  # will fall back to category residual below

higher_rows = host[host["Resolved_species"].isna() & host["Resolved_higher"].notna()].copy()
higher_rows["Row"] = higher_rows["Resolved_higher"]
higher_rows["Rank"] = higher_rows["Row"].map(RANK_OF)

resolved_idx = set(sp_rows.index[sp_rows["Row"].notna()]) | set(higher_rows.index)
fallback_mask = ~host.index.isin(resolved_idx)
residual = host[fallback_mask].copy()
residual["Row"] = residual["Detailed_scheme"] + "  (not resolved to species)"
# One residual row per category regardless of which order/class/aggregate labels
# feed it, that mix is exactly what "not resolved to species" means;
residual["Rank"] = "not species-resolved"

species_final = sp_rows[sp_rows["Row"].notna()]

combined = pd.concat([species_final, higher_rows, residual], ignore_index=True)
combined["Group"] = combined["Detailed_scheme"].map(lambda c: CAT_GROUP.get(c, "Unknown/Excluded"))
# species/higher-rank rows: use the row's own harmonized category's group (not
# "Unknown/Excluded", which is only the fallback for the Row string itself not
# matching a categ
combined.loc[combined["Rank"] != "not species-resolved", "Group"] = \
    combined.loc[combined["Rank"] != "not species-resolved", "Detailed_scheme"].map(lambda c: CAT_GROUP.get(c, "Unknown/Excluded"))
combined["Row_source"] = "host_data"

long = combined.groupby(["Row", "Rank", "Group", "Tool"], as_index=False)["Count"].sum()
long = long[long["Count"] > 0]

# Vector-axis fallback, targeting the named vector categories rather than a
# generic Insects/Arachnids bucket.
VECTOR_FALLBACK_TARGET_OVERRIDE = {
    "aedes": "Culicidae", "culex": "Culicidae", "mosquito (vector)": "Culicidae",
    "ixodes": "Ixodida", "tick (vector)": "Ixodida",
}
vector = master[master["Data_category"] == "vector"].copy()
vector["Row"] = vector["Original_label"].map(lambda l: VECTOR_FALLBACK_TARGET_OVERRIDE.get(l, "Insecta"))
vector["Rank"] = vector["Row"].map(RANK_OF)
vector["Group"] = "Invertebrates"

already_populated = set(zip(long["Row"], long["Tool"]))
vector_agg = vector.groupby(["Row", "Rank", "Group", "Tool"], as_index=False)["Count"].sum()
vector_agg["Wholly_vector"] = vector_agg.apply(
    lambda r: "No" if (r["Row"], r["Tool"]) in already_populated else "Yes", axis=1)
vector_agg["Row_source"] = vector_agg["Wholly_vector"].map(
    {"Yes": "vector_fallback_used", "No": "vector_fallback_merged"})

long = pd.concat([long, vector_agg.drop(columns=["Row_source", "Wholly_vector"])],
                 ignore_index=True)
# A mixed cell now appears twice, once from host data, once from vector -- so
# re-aggregate.
long = long.groupby(["Row", "Rank", "Group", "Tool"], as_index=False)["Count"].sum()

vector_agg[["Row", "Tool", "Count", "Wholly_vector"]].to_csv(
    os.path.join(SC, "species_matrix_vector_fallback.csv"), index=False)
_whole = (vector_agg["Wholly_vector"] == "Yes").sum()
print(f"vector fallback: {len(vector_agg)} cell(s) carry vector records "
      f"({_whole} wholly vector, {len(vector_agg) - _whole} mixed with host data) "
      f"-> species_matrix_vector_fallback.csv")

# Per-original-label trace (before the final host groupby collapses labels into
# shared Rows), one row per (Tool, Original_label), host AND vector, with
vector["Row_source"] = vector.apply(
    lambda r: "vector_fallback_blocked" if (r["Row"], r["Tool"]) in already_populated else "vector_fallback_used",
    axis=1)
trace_cols = ["Tool", "Original_label", "Count", "Detailed_scheme", "Row", "Rank", "Group", "Row_source"]
trace = pd.concat([
    combined.assign(**{c: combined.get(c) for c in ["Resolved_species", "Resolved_higher"]})[
        trace_cols + ["Resolved_species", "Resolved_higher"]],
    vector.assign(Resolved_species=None, Resolved_higher=None)[trace_cols + ["Resolved_species", "Resolved_higher"]],
], ignore_index=True)
trace.to_csv(os.path.join(SC, "species_matrix_label_trace.csv"), index=False)

def save(long: pd.DataFrame) -> None:
    """The species matrix, long and wide."""
    long_out = os.path.join(SC, "species_matrix.csv")
    long.to_csv(long_out, index=False)
    wide = long.pivot_table(index=["Row", "Rank", "Group"], columns="Tool",
                            values="Count", fill_value=0)
    wide_out = os.path.join(SC, "species_matrix_wide.csv")
    wide.to_csv(wide_out)
    print(f"Total rows in species-resolved matrix: {len(wide)}")
    print(f"  of which species-level: {(wide.index.get_level_values('Rank')=='species').sum()}")
    print(f"  of which residual/unresolved: {(wide.index.get_level_values('Rank')!='species').sum()}")
    print("\nsaved ->", long_out)
    print("saved ->", wide_out)


save(long)
