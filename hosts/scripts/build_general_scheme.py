# -*- coding: utf-8 -*-
"""Build the compact host scheme from the species-resolved matrix.
"""
import os
import pandas as pd

SC = os.path.dirname(os.path.abspath(__file__))
long = pd.read_csv(os.path.join(SC, "species_matrix.csv"))
trace = pd.read_csv(os.path.join(SC, "species_matrix_label_trace.csv"))
# Taken before any remapping: needed for the row-fate table and for the total
# check at the end.
ORIGINAL_ROWS = long["Row"].unique()
ORIGINAL_TOTAL = long["Count"].sum()

from categories import CATS
CAT_GROUP = dict(CATS)

# Tools can disagree about a row's category, so take a majority vote.
ROW_DETAILED_SCHEME = (
    trace.groupby(["Row", "Tool"])["Detailed_scheme"].first()
    .groupby("Row").agg(lambda s: s.value_counts().idxmax())
)

# Carve-out 1: a species named by at least this many dataset instances keeps a
# row of its own rather than folding into its order.
# 5 of the 17 dataset instances now in the analysis. The bar is a count, so
# it tightens when the corpus shrinks: it was 5 of 15 instances, 6 of 18, and
# returns to 5 at 17. At 6 of 17 the nine wildlife reservoirs the bar exists
# to keep would all fall out; at 5 the category set is unchanged.
SPECIES_STANDALONE_THRESHOLD = int(os.environ.get("SPECIES_STANDALONE_THRESHOLD", 5))
OUT_PREFIX = os.environ.get("GENERAL_SCHEME_PREFIX", "general_scheme")
_species_n_tools = long[long["Rank"] == "species"].groupby("Row")["Tool"].nunique()
SPECIES_KEEP_STANDALONE = set(_species_n_tools[_species_n_tools >= SPECIES_STANDALONE_THRESHOLD].index)

# Carve-out 2: species routed to a finer category than their own Detailed_scheme
# gives them.
VECTOR_ROLLUP = {
    "Aedes aegypti": ("Culicidae", "family", "Invertebrates"),
    "Amblyomma americanum": ("Ixodida", "order", "Invertebrates"),
    "Penaeus vannamei": ("Crustacea", "subphylum", "Invertebrates"),
    "Penaeus monodon": ("Crustacea", "subphylum", "Invertebrates"),
    "Caridea": ("Crustacea", "subphylum", "Invertebrates"),
    # These carry Detailed_scheme="Other invertebrates" and would not reach
    # Crustacea otherwise.
    "Callinectes sapidus": ("Crustacea", "subphylum", "Invertebrates"),
    "Eriocheir sinensis": ("Crustacea", "subphylum", "Invertebrates"),
    "Macrobrachium rosenbergii": ("Crustacea", "subphylum", "Invertebrates"),
    "Fenneropenaeus chinensis": ("Crustacea", "subphylum", "Invertebrates"),
    "Cherax quadricarinatus": ("Crustacea", "subphylum", "Invertebrates"),
    "Scylla serrata": ("Crustacea", "subphylum", "Invertebrates"),
    "Gammarus pulex": ("Crustacea", "subphylum", "Invertebrates"),
    "Gammarus chevreuxi": ("Crustacea", "subphylum", "Invertebrates"),
    "Crangon crangon": ("Crustacea", "subphylum", "Invertebrates"),
    "Charybdis japonica": ("Crustacea", "subphylum", "Invertebrates"),
    "Capitulum mitella": ("Crustacea", "subphylum", "Invertebrates"),
    # A mite, not an insect.
    "Varroa destructor": ("Arachnida", "class (rolled up)", "Invertebrates"),
    # "Culicidae"/"Ixodida" also occur as species_matrix Rows IN THEIR OWN
    # RIGHT, build_species_matrix.py's HIGHER dict resolves several tools' raw
    # labels (
    "Culicidae": ("Culicidae", "family", "Invertebrates"),
    "Ixodida": ("Ixodida", "order", "Invertebrates"),
}
# Genus-level fallback for species not yet individually enumerated above -- a
# future rebuild that resolves a new tick/mosquito species to species-level
MOSQUITO_GENERA = ("Aedes ", "Culex ", "Anopheles ", "Mansonia ", "Culiseta ")
TICK_GENERA = ("Ixodes ", "Amblyomma ", "Rhipicephalus ", "Dermacentor ",
               "Haemaphysalis ", "Ornithodoros ", "Argas ", "Hyalomma ")
_VECTOR_ISH_DETAILED_SCHEMES = ("Arachnids", "Insects", "Unresolved arthropods", "Unresolved invertebrates")


def _vector_genus_fallback(orig_row, ds):
    if ds not in _VECTOR_ISH_DETAILED_SCHEMES:
        return None
    if orig_row.startswith(MOSQUITO_GENERA):
        return "Culicidae", "family", "Invertebrates"
    if orig_row.startswith(TICK_GENERA):
        return "Ixodida", "order", "Invertebrates"
    return None


# Vector/crustacean identity is judged more important than a single species'
# cross-tool recurrence (see VECTOR_ROLLUP above), so a species that clears t
_vector_species = set(VECTOR_ROLLUP)
_promoted = SPECIES_KEEP_STANDALONE & _vector_species
if _promoted:
    SPECIES_KEEP_STANDALONE -= _vector_species
    print(f"  {len(_promoted)} vector/crustacean species cleared the "
          f">={SPECIES_STANDALONE_THRESHOLD}-instance threshold but stay pooled by rule: "
          + ", ".join(sorted(_promoted)))

# Promote a Detailed_scheme category one notch to its taxonomic order/class/
# kingdom where a natural one exists in this project's data (Bats/Rodents/ Un
DETAILED_SCHEME_TO_TAXON = {
    "Bats": "Chiroptera", "Rodents": "Rodentia", "Ungulates": "Artiodactyla",
    "Carnivores": "Carnivora", "Birds": "Aves",
    "Reptiles": "Reptilia", "Amphibians": "Amphibia", "Plants": "Plantae",
    # Arachnids get their own category rather than dissolving into the generic
    # invertebrate bucket: Ixodida (ticks) is already carved out as a vector
    # taxon, and leaving the rem
    "Arachnids": "Arachnida", "Unresolved arthropods": "Other invertebrates",
    "Unresolved invertebrates": "Other invertebrates",
    "Other/unresolved mammals": "Other mammals",
}
# NOTE: "Fish" is deliberately NOT in DETAILED_SCHEME_TO_TAXON, "Fish" is
# already a literal Detailed_scheme/CATS category (categories.py), not a generic
# one needing promoti
TAXON_RANK = {
    "Arachnida": "class (rolled up)",
    "Carnivora": "order (rolled up)", "Artiodactyla": "order (rolled up)",
    "Rodentia": "order (rolled up)", "Chiroptera": "order (rolled up)",
    "Aves": "class (rolled up)", "Reptilia": "class (rolled up)", "Amphibia": "class (rolled up)",
    "Plantae": "kingdom (rolled up)",
    "Other invertebrates": "mixed rank (rolled up)", "Other mammals": "mixed rank (rolled up)",
}
TAXON_GROUP = {
    "Arachnida": "Invertebrates",
    "Carnivora": "Mammals", "Artiodactyla": "Mammals", "Rodentia": "Mammals",
    "Chiroptera": "Mammals", "Other mammals": "Mammals",
    "Aves": "Non-mammalian vertebrates", "Reptilia": "Non-mammalian vertebrates",
    "Amphibia": "Non-mammalian vertebrates", "Plantae": "Plants",
    "Other invertebrates": "Invertebrates",
}


# Any two routing paths that land on the SAME final category must agree on Rank
# and Group, or groupby() splits that category into two same-named rows.
_rank_conflicts = [
    (row, rank, TAXON_RANK[row]) for row, rank, _grp in VECTOR_ROLLUP.values()
    if row in TAXON_RANK and rank != TAXON_RANK[row]
]
assert not _rank_conflicts, (
    "VECTOR_ROLLUP Rank disagrees with TAXON_RANK for the same category -- "
    f"would split it into duplicate rows: {_rank_conflicts}")


def _route(orig_row):
    if orig_row in SPECIES_KEEP_STANDALONE:
        ds = ROW_DETAILED_SCHEME.get(orig_row, orig_row)
        return orig_row, "species", CAT_GROUP.get(ds, "Unknown/Excluded"), "standalone_species"
    if orig_row in VECTOR_ROLLUP:
        row, rank, group = VECTOR_ROLLUP[orig_row]
        return row, rank, group, "vector_or_crustacea_rollup"
    ds = ROW_DETAILED_SCHEME.get(orig_row)
    if ds is None:
        # Should not happen: every species_matrix Row is built from raw labels
        # that already carry a Detailed_scheme (build_species_matrix.py never
        # drops that column before this poi
        raise ValueError(f"no Detailed_scheme found for Row {orig_row!r} -- "
                          f"check species_matrix_label_trace.csv")
    genus_fallback = _vector_genus_fallback(orig_row, ds)
    if genus_fallback is not None:
        row, rank, group = genus_fallback
        return row, rank, group, "vector_genus_fallback"
    taxon = DETAILED_SCHEME_TO_TAXON.get(ds)
    if taxon is not None:
        # "Other invertebrates"/"Other mammals" are themselves already real
        # Detailed_scheme category names (categories.py's CATS), not new
        # order/class/kingdom b
        if taxon in CAT_GROUP:
            return taxon, "category (harmonized scheme)", CAT_GROUP[taxon], "taxon_promoted"
        return taxon, TAXON_RANK[taxon], TAXON_GROUP[taxon], "taxon_promoted"
    return ds, "category (harmonized scheme)", CAT_GROUP.get(ds, "Unknown/Excluded"), "detailed_scheme_direct"


_routed = [_route(r) for r in ORIGINAL_ROWS]
_genus_fallback_hits = [orig for orig, r in zip(ORIGINAL_ROWS, _routed) if r[3] == "vector_genus_fallback"]
if _genus_fallback_hits:
    print(f"vector genus fallback fired for {len(_genus_fallback_hits)} row(s) not in VECTOR_ROLLUP: "
          f"{_genus_fallback_hits} -- consider adding them explicitly")
row_fate = pd.DataFrame({
    "Row": ORIGINAL_ROWS,
    "Final_category": [r[0] for r in _routed],
    "Fate": [r[3] for r in _routed],
})
row_fate_out = os.path.join(SC, OUT_PREFIX + "_row_fate.csv")
row_fate.to_csv(row_fate_out, index=False)
print("saved ->", row_fate_out)

ROUTE_OF = {orig: (row, rank, group) for orig, (row, rank, group, _fate) in zip(ORIGINAL_ROWS, _routed)}
long["Rank"], long["Group"] = zip(*[(ROUTE_OF[r][1], ROUTE_OF[r][2]) for r in long["Row"]])
long["Row"] = long["Row"].map(lambda r: ROUTE_OF[r][0])

# No fold-away step: every row above already has a real, established name.
unnamed_detail_out = os.path.join(SC, OUT_PREFIX + "_unnamed_detail.csv")
long.iloc[0:0].to_csv(unnamed_detail_out, index=False)
print("saved ->", unnamed_detail_out, "(always empty now -- nothing is folded away)")

out = long.groupby(["Row", "Rank", "Group", "Tool"], as_index=False)["Count"].sum()
out = out[out["Count"] > 0]

# _route() only relabels rows, it never filters or duplicates records -- so this
# total must match species_matrix.csv's exactly.
_new_total = out["Count"].sum()
assert _new_total == ORIGINAL_TOTAL, (
    f"general_scheme_matrix.csv total ({_new_total}) != species_matrix.csv total "
    f"({ORIGINAL_TOTAL}) -- a routing rule above is dropping or double-counting records"
)

print(f"General scheme: {out['Row'].nunique()} categories, all named (0 folded/unnamed)")
print(f"Total reconciled against species_matrix.csv: {_new_total:,.0f}")

def save(out: pd.DataFrame) -> None:
    """The scheme matrix, long and wide, under OUT_PREFIX so a threshold sweep
    can write beside the committed files rather than over them."""
    long_out = os.path.join(SC, OUT_PREFIX + "_matrix.csv")
    out.to_csv(long_out, index=False)
    wide = out.pivot_table(index=["Row", "Rank", "Group"], columns="Tool",
                           values="Count", fill_value=0)
    wide_out = os.path.join(SC, OUT_PREFIX + "_matrix_wide.csv")
    wide.to_csv(wide_out)
    print("saved ->", long_out)
    print("saved ->", wide_out)


save(out)
