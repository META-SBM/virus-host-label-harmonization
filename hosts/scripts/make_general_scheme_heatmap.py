# -*- coding: utf-8 -*-
"""General (few-category) host scheme heatmap, styled identically to
host_taxon_heatmap.png (make_heatmap.py), same palette, icons, exact/
presence-only cell encoding, swatches, dataset-size bubbles, top barplot and
right-side legend stack. Only the row categories differ: a row here is
either a genuine taxonomic identity (species/order/class/kingdom, resolved
in build_species_matrix.py) or one of the always-complete Detailed_scheme
categories host_taxon_heatmap.png itself uses: every row is named, there
is no "Unnamed"/fold row of any kind (see build_general_scheme.py's
module docstring for the routing rules and the history of why that fold
used to exist and was removed).

    python3 make_general_scheme_heatmap.py

Four other scripts import load_data() and process_data() to get the row order,
the cell matrix and the palette this figure draws, so that no second script can
disagree with the figure about a number.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.offsetbox import AnnotationBbox, OffsetImage  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

from categories import (GROUP_COLOR, MOLTYPE_COLOR, MOLTYPE_LABEL,  # noqa: E402
                        RECTYPE_COLOR, RECTYPE_LABEL)
from icons import ICON_COLOR, lineage_icons  # noqa: E402

SC = os.path.dirname(os.path.abspath(__file__))
OUT_PNG = os.path.join(os.path.dirname(SC), "host_general_scheme.png")

# ---- palette (identical to make_heatmap.py) ----
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#ffffff"
PAGE = "#ffffff"
SEQ_450 = "#2a78d6"
SEQ_700 = "#0d366b"
BLANK_CELL = SURFACE
CAT_MAGENTA = "#e87ba4"
CAT_RED = "#e34948"

# Distinct from GROUP_COLOR (taxonomic row groups, categories.py), this is a
# separate column-wise grouping (what the tool predicts), shown as a semi-tra
ENDPOINT_COLOR = {
    "A": "#4472a8",
    "B": "#4a9169",
    "C": "#c9a227",
    "D": "#c1584a",
    "E": "#8064a8",
    "F": "#3f9e9e",
}


def _tint(hex_color, amount):
    r, g, b = matplotlib.colors.to_rgb(hex_color)
    R, G, B = matplotlib.colors.to_rgb(SURFACE)
    return (r + (R - r) * amount, g + (G - g) * amount, b + (B - b) * amount)


GROUP_COLOR_EXACT = {g: _tint(c, 0.35) for g, c in GROUP_COLOR.items()}

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["text.color"] = INK_PRIMARY
plt.rcParams["axes.edgecolor"] = BASELINE

# ---- geometry ----
FIG_SIZE = (28.3, 28.0)
LEFT, RIGHT = 0.355, 0.75  # 0.29 -> 0.31 (English common names) -> 0.33 (hierarchical 'Other ...' rows)
CAT_NAME_X = -0.012
CHILD_INDENT = 0.075
S_MIN, S_MAX = 45, 850
ENDPOINT_BACK_TOP = -0.14
ENDPOINT_GROUP_GAP = 0.08
ICON_ZOOM = 0.16

# ---- row layout ----
GROUP_ORDER = ["Mammals", "Non-mammalian vertebrates", "Invertebrates", "Plants",
               "Algae", "Protists & oomycetes", "Fungi", "Unknown/Excluded"]
# Displayed as "Unknown", not "Unknown/Excluded".
GROUP_DISPLAY = {"Non-mammalian vertebrates": "Non-mammalian\nvertebrates",
                 "Unknown/Excluded": "Unknown"}
HIERARCHY = [
    # header, [child rows, in display order], row that becomes "Other <header>"
    # Only genuine taxa are nested.
    ("Primates", ["Homo sapiens", "Pan troglodytes", "Macaca mulatta",
                  "Chlorocebus aethiops"], None),
    ("Artiodactyla", ["Sus scrofa", "Bos taurus", "Ovis aries", "Capra hircus"], "Artiodactyla"),
    ("Carnivora", ["Canis lupus", "Vulpes vulpes", "Procyon lotor", "Felis catus",
                   "Mephitis mephitis", "Cerdocyon thous", "Mustela putorius",
                   "Nyctereutes procyonoides"], "Carnivora"),
    ("Chiroptera", ["Eptesicus fuscus", "Tadarida brasiliensis", "Desmodus rotundus"], "Chiroptera"),
    ("Rodentia", ["Mus musculus", "Rattus norvegicus", "Mesocricetus auratus"], "Rodentia"),
    ("Aves", ["Gallus gallus", "Anas platyrhynchos", "Meleagris gallopavo", "Struthio camelus"], "Aves"),
    # Mosquitoes are insects and ticks are arachnids;
    ("Insecta", ["Culicidae"], "Insects"),
    ("Arachnida", ["Ixodida"], "Arachnida"),
]
# Generic buckets sort to the foot of their lineage rather than among the named
# taxa by size, they are what is left once the taxa are accounted for, not
GENERIC_ROWS = {
    "Other mammals", "Other invertebrates", "Non-human (undifferentiated)",
    "Non-human primates", "Humans + non-human primates",
    "Unresolved vertebrates", "Unresolved eukaryote", "Unknown host",
    "Undefined label",
}
# Latin row names carry an English common name in parentheses: a reader who
# knows "raccoon dog" should not have to look up Nyctereutes procyonoides.
COMMON_NAME = {
    "Homo sapiens": "human", "Sus scrofa": "pig", "Bos taurus": "cattle",
    "Equus caballus": "horse", "Felis catus": "domestic cat", "Capra hircus": "goat",
    "Procyon lotor": "raccoon", "Vulpes vulpes": "red fox",
    "Nyctereutes procyonoides": "raccoon dog",
    # Merged from "Canis lupus", "Canis lupus familiaris" and "Canis
    # familiaris".
    "Canis lupus": "wolf / domestic dog",
    "Gallus gallus": "chicken", "Anas platyrhynchos": "mallard duck",
    # Added when the retention threshold moved 6 -> 5.
    "Pan troglodytes": "chimpanzee", "Macaca mulatta": "rhesus macaque",
    "Chlorocebus aethiops": "green monkey", "Ovis aries": "sheep",
    "Mephitis mephitis": "striped skunk", "Cerdocyon thous": "crab-eating fox",
    "Mustela putorius": "European polecat", "Eptesicus fuscus": "big brown bat",
    "Tadarida brasiliensis": "Brazilian free-tailed bat", "Desmodus rotundus": "vampire bat",
    "Mus musculus": "house mouse", "Rattus norvegicus": "brown rat",
    "Mesocricetus auratus": "golden hamster", "Meleagris gallopavo": "turkey",
    "Struthio camelus": "ostrich",
    # "other" on exactly the three rows that ARE residuals, i.e.
    "Carnivora": "carnivorans", "Artiodactyla": "even-toed ungulates",
    "Aves": "birds",  # "Primates" needs no gloss -- the Latin and English are the same word
    # No parenthetical on the residual rows: the bold parent header directly
    # above plus the indent already say "everything in this taxon except the
    # species listed".
    "Rodentia": "rodents", "Chiroptera": "bats",
    "Reptilia": "reptiles", "Amphibia": "amphibians",
    "Culicidae": "mosquitoes", "Ixodida": "ticks", "Crustacea": "crustaceans",
    "Insecta": "insects", "Arachnida": "arachnids",
    "Plantae": "plants",
}

GROUP_ICON_ARRAY = lineage_icons(GROUP_ORDER)


def bubble_area(n, log_min, log_max):
    """Bubble area for a dataset of n records, on the log scale the columns
    share. Also used for the legend's round numbers, which are not any tool."""
    frac = (math.log10(n) - log_min) / (log_max - log_min)
    return S_MIN + frac * (S_MAX - S_MIN)


def place_group_icon(ax, cx, cy_data, name, zoom=ICON_ZOOM):
    arr = GROUP_ICON_ARRAY.get(name)
    if arr is None:
        return
    disp = ax.transData.transform((0, cy_data))
    _, ay = ax.transAxes.inverted().transform(disp)
    ab = AnnotationBbox(OffsetImage(arr, zoom=zoom), (cx, ay), xycoords="axes fraction",
                         frameon=False, box_alignment=(0.5, 0.5), pad=0, zorder=6)
    ax.add_artist(ab)


def load_data():
    """The scheme matrix and the four tables that badge, order and describe it.
    Nothing here is computed."""
    read = lambda name: pd.read_csv(os.path.join(SC, name))
    return {
        "wide": read("general_scheme_matrix_wide.csv"),
        "vector_fallback": read("species_matrix_vector_fallback.csv"),
        "row_fate": read("general_scheme_row_fate.csv"),
        "label_trace": read("species_matrix_label_trace.csv"),
        "species_matrix": read("species_matrix.csv"),
        "tool_metadata": _drop_excluded(read("tool_metadata.csv").sort_values("order")),
        "master": pd.read_csv(os.path.join(SC, "master_labels.csv"),
                              keep_default_na=False, na_values=[]),
    }


def _badge_cells(data):
    """Which cells carry a "V" (vector, not host) and which columns carry a "*"
    (one record counted in more than one row). Both are looked up through
    general_scheme_row_fate, not matched on the raw row name."""
    vf, fate = data["vector_fallback"], data["row_fate"]
    fate_of = dict(zip(fate["Row"], fate["Final_category"]))
    merged = lambda t: "HostNet" if str(t).startswith("HostNet") else t
    vector_cells = set((fate_of.get(row, row), merged(tool))
                       for row, tool in zip(vf["Row"], vf["Tool"]))

    dc = data["master"]
    dc = dc[dc["Potential_double_count"] == "Yes"][["Tool", "Original_label"]].drop_duplicates()
    dc = data["label_trace"].merge(dc, on=["Tool", "Original_label"]).merge(fate, on="Row")
    return vector_cells, set(dc["Tool"].map(merged))



def _drop_excluded(tm):
    """Tools flagged include_in_analysis = no stay in the tree but not in the
    figure; categories.excluded_instances() is the single source of that flag."""
    from categories import excluded_instances
    dropped = excluded_instances()
    return tm[~tm["tool"].isin(dropped)].copy()


def _columns(tm):
    """Column order, and everything the swatches under a column say about it.
    Columns are grouped by what the tool predicts, not listed alphabetically."""
    tools = tm["tool"].tolist()
    endpoint_category = dict(zip(tm["tool"], tm["endpoint_id"]))
    endpoint_label = dict(zip(tm["endpoint_id"], tm["endpoint_label"]))
    segments = []
    seg_start = 0
    tool_endpoint = [endpoint_category[t] for t in tools]
    for k in range(1, len(tool_endpoint) + 1):
        if k == len(tool_endpoint) or tool_endpoint[k] != tool_endpoint[seg_start]:
            segments.append((seg_start, k, tool_endpoint[seg_start]))
            seg_start = k
    return {
        "TOOLS": tools,
        "ENDPOINT_CATEGORY": endpoint_category,
        "ENDPOINT_LABEL": endpoint_label,
        "ENDPOINT_SEGMENTS": segments,
        "TOTAL_DATASET_SIZE": {r.tool: (int(r.dataset_size), r.dataset_size_unit)
                               for r in tm.itertuples()},
        "record_type": dict(zip(tm["tool"], tm["counting_unit"])),
        "MOLECULE_TYPE": {r.tool: (r.molecule_type, r.molecule_detail)
                          for r in tm.itertuples()},
    }


def _display_rows(wide, tools, species_matrix):
    """Row order: hierarchy blocks and standalone rows interleaved by weight,
    biggest first, generic buckets last within their lineage. Returns one tuple
    per drawn row, (label, lineage, index into wide or None for a header, depth)."""
    by_label = {lab: idx for idx, lab in wide["Label"].items()}
    hierarchy = [(h, list(kids), res) for h, kids, res in HIERARCHY]
    # A species named in HIERARCHY may legitimately have no row: the retention
    # threshold in build_general_scheme.py decides which species stand alone, and a
    # species that falls
    species_rows = set(species_matrix.query("Rank == 'species'")["Row"])
    pooled = []
    for i, (h, kids, res) in enumerate(hierarchy):
        absent = [k for k in kids + ([res] if res else []) if k not in by_label]
        typos = [k for k in absent if k not in species_rows]
        assert not typos, f"HIERARCHY names that are not rows at all: {typos}"
        if absent:
            pooled.extend(absent)
            hierarchy[i] = (h, [k for k in kids if k in by_label], res)
    if pooled:
        print(f"  {len(pooled)} species below the retention threshold are pooled into their "
              f"parent rows rather than shown by name: " + ", ".join(sorted(pooled)))

    child_of = {c: h for h, kids, _ in hierarchy for c in kids}
    residual_of = {res: h for h, _, res in hierarchy if res is not None}
    rows_out = []
    for grp in GROUP_ORDER:
        sub = wide[wide["Group"] == grp]
        named = sub[~sub["is_fold"]]
        # Sort blocks and standalone rows together by weight, so "biggest first"
        # still holds, a block's weight is its parent residual plus its children.
        blocks = []
        for idx, row in named.iterrows():
            lab = row["Label"]
            if lab in child_of or lab in residual_of:
                continue  # handled with its block
            blocks.append((lab in GENERIC_ROWS, row["total"], [(lab, grp, idx, 0)]))
        for header, kids, residual in hierarchy:
            kid_idx = [by_label[k] for k in kids if by_label[k] in named.index]
            res_idx = by_label[residual] if residual and by_label[residual] in named.index else None
            if not kid_idx and res_idx is None:
                continue  # this block's rows are not in this group
            weight = sum(wide.loc[i, "total"] for i in kid_idx)
            rows = [(header, grp, None, 0)]
            # inside a block: named taxa by size, then the block's own generic
            # members, then the residual
            for i in sorted(kid_idx, key=lambda i: (wide.loc[i, "Label"] in GENERIC_ROWS,
                                                    -wide.loc[i, "total"])):
                rows.append((wide.loc[i, "Label"], grp, i, 1))
            if res_idx is not None:
                weight += wide.loc[res_idx, "total"]
                rows.append((f"Other {header}", grp, res_idx, 1))  # residual always last
            blocks.append((False, weight, rows))
        blocks.sort(key=lambda b: (b[0], -b[1]))
        for _, _, rows in blocks:
            rows_out += rows
        for idx in sub[sub["is_fold"]].index:
            rows_out.append((wide.loc[idx, "Label"], grp, idx, 0))
    return rows_out


def process_data(data):
    """Rows, columns, the cell matrix and the badge masks. The input frames are
    not modified; every drawn number leaves here and nothing is recomputed
    downstream, in this script or in the four that import it."""
    wide = data["wide"].copy()
    # HostNet trains 2 task-specific models (Rabies/VIPHOD and Flavivirus) that used
    # to show up as 2 separate columns from 1 tool, per explicit user request
    wide["HostNet"] = wide.get("HostNet (Rabies, VIPHOD)", 0.0) + wide.get("HostNet (Flavivirus)", 0.0)

    cols = _columns(data["tool_metadata"])
    tools = cols["TOOLS"]
    for t in tools:
        if t not in wide.columns:
            wide[t] = 0.0

    # Row list: plain display names (no "(species)"/"(order)" tags, unlike
    # host_species_matrix.png, this heatmap's whole point is to look like
    # host_taxon_heatmap.png, which nev
    wide["Label"] = wide.apply(
        lambda r: "Unnamed (<4 tools)" if r["Rank"] == "mixed (folded)"
        else r["Row"].split("  (")[0], axis=1)  # strip " (not resolved to species)" etc.
    wide["total"] = wide[tools].sum(axis=1)
    wide["is_fold"] = wide["Rank"] == "mixed (folded)"
    # Keyed on the display label, so two rows cleaning to the same string would
    # collapse to whichever comes last, with no error and no visible gap.
    dupes = wide["Label"][wide["Label"].duplicated(keep=False)].tolist()
    assert not dupes, f"duplicate display labels would be silently dropped: {sorted(set(dupes))}"

    display_rows = _display_rows(wide, tools, data["species_matrix"])
    cats = [(lab, grp) for lab, grp, _, _ in display_rows]
    row_src = [src for _, _, src, _ in display_rows]
    is_header = [src is None for src in row_src]
    cat_groups = [c[1] for c in cats]

    # Species names are italicised, everything above genus is not, the standard
    # convention, and a hard requirement for publication.
    species_rows = {r for r, rk in zip(wide["Label"], wide["Rank"]) if rk == "species"}

    def row_label(name):
        latin = (r"$\mathit{" + name.replace(" ", r"\ ") + "}$") if name in species_rows else name
        return f"{latin} ({COMMON_NAME[name]})" if name in COMMON_NAME else latin

    # state[row, col]: 0 = not present, 2 = exact count.
    state = np.zeros((len(cats), len(tools)), dtype=float)
    annot = np.empty((len(cats), len(tools)), dtype=object)
    annot[:] = ""
    for i in range(len(cats)):
        if row_src[i] is None:
            continue  # header row -- carries no data by construction
        for j, tool in enumerate(tools):
            val = wide.loc[row_src[i], tool]
            if val and val > 0:
                state[i, j] = 2
                annot[i, j] = f"{int(val):,}"

    group_bounds = []
    start = 0
    for k in range(1, len(cat_groups) + 1):
        if k == len(cat_groups) or cat_groups[k] != cat_groups[start]:
            group_bounds.append((start, k - 1, cat_groups[start]))
            start = k

    log_n = {t: math.log10(cols["TOTAL_DATASET_SIZE"][t][0]) for t in tools}
    log_min, log_max = min(log_n.values()), max(log_n.values())

    vector_cells, double_count_tools = _badge_cells(data)
    out = dict(cols)
    out.update({
        "CATS": cats,
        "state": state,
        "annot": annot,
        "row_src": row_src,
        "row_depth": [d for _, _, _, d in display_rows],
        "IS_HEADER": is_header,
        # Header rows are typography, not categories, the scheme still has 34.
        "N_REAL_CATS": sum(1 for h in is_header if not h),
        "cat_labels": [row_label(c[0]) for c in cats],
        "cat_groups": cat_groups,
        # Pre-clean_label source names, for the vector-fallback badge lookup.
        "cat_orig_rows": [wide.loc[s, "Row"] if s is not None else None for s in row_src],
        "SPECIES_ROWS": species_rows,
        "group_bounds": group_bounds,
        "VECTOR_FALLBACK_CELLS": vector_cells,
        "DOUBLE_COUNT_TOOLS": double_count_tools,
        # Every populated category counts, vector cells included. They used to be
        # discounted where a cell held nothing but vector records, which put a
        # biological judgement (a mosquito is not a host) on top of a figure that
        # otherwise reports the harmonization as it stands. The cells are still marked
        # "V", so which of them carry vector records is visible per cell.
        "breadth_per_tool": (state > 0).sum(axis=0).astype(int),
        "LOG_MIN": log_min,
        "LOG_MAX": log_max,
        "bubble_size": {t: bubble_area(cols["TOTAL_DATASET_SIZE"][t][0], log_min, log_max)
                        for t in tools},
    })
    return out


def generate_visualization(d):
    """Draw and save. Every number is taken from d as it is; nothing is counted,
    sorted or rounded here."""
    CATS, TOOLS = d["CATS"], d["TOOLS"]
    state, annot = d["state"], d["annot"]
    IS_HEADER, row_depth = d["IS_HEADER"], d["row_depth"]
    cat_labels, cat_groups, cat_orig_rows = d["cat_labels"], d["cat_groups"], d["cat_orig_rows"]
    N_REAL_CATS = d["N_REAL_CATS"]
    ENDPOINT_CATEGORY, ENDPOINT_LABEL = d["ENDPOINT_CATEGORY"], d["ENDPOINT_LABEL"]
    MOLECULE_TYPE, record_type = d["MOLECULE_TYPE"], d["record_type"]
    bubble_size, breadth_per_tool = d["bubble_size"], d["breadth_per_tool"]
    LOG_MIN, LOG_MAX = d["LOG_MIN"], d["LOG_MAX"]

    # The figure no longer draws a "labels reported by the study" bar. Of the 278
    # labels in that workbook, only 38 carry a pointer into an article; 174 are the
    # release's own labels, reproduced exactly by the recompute, and 48 match on
    # count alone, which is not evidence. The quantity was not what its name said.

    # Figure height/bottom margin shrunk back down (19.5in/0.425 -> 16.3in/0.312)
    # now that the prediction-target band ends at the (semi-transparent) backing
    fig = plt.figure(figsize=FIG_SIZE, facecolor=PAGE)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 3.85], hspace=0.10,
                           top=0.975, bottom=0.243, left=LEFT, right=RIGHT)
    ax_bar = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1], sharex=ax_bar)
    ax.set_facecolor(SURFACE)
    ax_bar.set_facecolor(PAGE)

    rgba = np.zeros((len(CATS), len(TOOLS), 4))
    page_rgba = matplotlib.colors.to_rgba(PAGE)
    for i in range(len(CATS)):
        grp = cat_groups[i]
        exact = (*GROUP_COLOR_EXACT[grp], 1.0)
        blank = matplotlib.colors.to_rgba(BLANK_CELL)
        for j in range(len(TOOLS)):
            # Header rows get the page colour, not the empty-cell colour: an
            # unfilled BLANK_CELL row would read as "this taxon is absent from every
            # tool", which is the opposite of what
            if IS_HEADER[i]:
                rgba[i, j] = page_rgba
            else:
                rgba[i, j] = exact if state[i, j] == 2 else blank
    ax.imshow(rgba, aspect="auto")

    ax.set_xticks(np.arange(-.5, len(TOOLS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(CATS), 1), minor=True)
    ax.grid(which="minor", color=PAGE, linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(range(len(TOOLS)))
    ax.set_xticklabels([])
    ax.tick_params(axis="x", length=0)
    ax.set_yticks(range(len(CATS)))
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    row_trans = ax.get_yaxis_transform()
    # Headers sit flush against the grid in bold;
    for i, label in enumerate(cat_labels):
        x = CAT_NAME_X - (CHILD_INDENT if row_depth[i] else 0.0)
        ax.text(x, i, label, ha="right", va="center", fontsize=19,
                fontweight="bold" if IS_HEADER[i] else "normal",
                color=INK_PRIMARY, transform=row_trans)

    # Bold type and an indent alone did not read as a hierarchy at a glance, so the
    # relationship is drawn explicitly: a spine dropping from each header with a
    # short arm into ev
    TREE_SPINE_X = CAT_NAME_X - CHILD_INDENT + 0.014
    TREE_ARM_X = CAT_NAME_X - 0.004
    for i in range(len(CATS)):
        if not IS_HEADER[i]:
            continue
        kids = [k for k in range(i + 1, len(CATS)) if row_depth[k] == 1]
        kids = [k for k in kids if all(row_depth[m] == 1 for m in range(i + 1, k + 1))]
        if not kids:
            continue
        ax.plot([TREE_SPINE_X, TREE_SPINE_X], [i + 0.15, kids[-1]],
                color=INK_SECONDARY, linewidth=1.7, transform=row_trans, clip_on=False, zorder=3)
        for k in kids:
            ax.plot([TREE_SPINE_X, TREE_ARM_X], [k, k],
                    color=INK_SECONDARY, linewidth=1.7, transform=row_trans, clip_on=False, zorder=3)

    for i in range(len(CATS)):
        for j in range(len(TOOLS)):
            if state[i, j] == 2:
                ax.text(j, i, annot[i, j], ha="center", va="center", fontsize=14.5,
                         color=INK_PRIMARY, fontweight="bold")
                if (cat_orig_rows[i], TOOLS[j]) in d["VECTOR_FALLBACK_CELLS"]:
                    ax.text(j + 0.40, i - 0.36, "V", ha="center", va="center", fontsize=12,
                            color=INK_PRIMARY, fontweight="bold",
                            bbox=dict(boxstyle="circle,pad=0.18", facecolor=CAT_MAGENTA, edgecolor="none"),
                            zorder=8)

    # The group block (stripe | icon | group name) sits to the LEFT of the row
    # labels, so its x positions depend on how far the longest row label reaches.
    fig.canvas.draw()
    _r = fig.canvas.get_renderer()
    _inv = ax.transAxes.inverted()
    _label_left = min(_inv.transform((t.get_window_extent(renderer=_r).x0, 0))[0]
                       for t in ax.texts if t.get_text() in cat_labels)
    _probe = [ax.text(0, 0, GROUP_DISPLAY.get(n, n), fontsize=16, fontweight="bold",
                       linespacing=1.25, transform=ax.transAxes)
               for _, _, n in d["group_bounds"]]
    _gname_w = max(_inv.transform((t.get_window_extent(renderer=_r).x1, 0))[0]
                    - _inv.transform((t.get_window_extent(renderer=_r).x0, 0))[0] for t in _probe)
    for t in _probe:
        t.remove()
    # Gaps kept tight on purpose: the stripe/icon/name block is the widest fixed
    # cost on the left of the figure, and every unit of padding here is a unit of
    # total figure width
    GNAME_X = _label_left - 0.001 - _gname_w
    ICON_X = GNAME_X - 0.020
    DIVIDER_X = ICON_X - 0.026
    STRIPE_X, STRIPE_W = DIVIDER_X - 0.014, 0.014
    ax.add_line(Line2D([DIVIDER_X, DIVIDER_X], [-0.5, len(CATS) - 0.5], color=BASELINE,
                        linewidth=1.0, transform=row_trans, clip_on=False))
    for (s, e, name) in d["group_bounds"]:
        if s > 0:
            ax.axhline(s - 0.5, color=BASELINE, linewidth=1.1, xmin=STRIPE_X - 0.02, xmax=1, clip_on=False)
        mid = (s + e) / 2
        ax.add_patch(Rectangle((STRIPE_X, s - 0.5 + 0.05), STRIPE_W, (e - s + 1) - 0.10,
                                facecolor=GROUP_COLOR[name], edgecolor="none",
                                transform=row_trans, clip_on=False, zorder=4))
        place_group_icon(ax, ICON_X, mid, name)
        ax.text(GNAME_X, mid, GROUP_DISPLAY.get(name, name), ha="left", va="center", fontsize=18,
                color=INK_PRIMARY, fontweight="bold", transform=row_trans, linespacing=1.25)

    col_trans = ax.get_xaxis_transform()
    for j, tool in enumerate(TOOLS):
        mol_key, mol_detail = MOLECULE_TYPE[tool]
        ax.add_patch(Rectangle((j - 0.34, -0.046), 0.30, 0.028, facecolor=RECTYPE_COLOR[record_type[tool]],
                                edgecolor="none", transform=col_trans, clip_on=False, zorder=5))
        ax.add_patch(Rectangle((j + 0.04, -0.046), 0.30, 0.028, facecolor=MOLTYPE_COLOR[mol_key],
                                edgecolor="none", transform=col_trans, clip_on=False, zorder=5))
        ax.scatter([j], [-0.098], s=bubble_size[tool], color=SEQ_450, edgecolor=SEQ_700,
                   linewidth=0.6, alpha=0.85, transform=col_trans, clip_on=False, zorder=6)
        if tool in d["DOUBLE_COUNT_TOOLS"]:
            ax.text(j, -0.128, "*", ha="center", va="center", fontsize=15,
                    color=SURFACE, fontweight="bold",
                    bbox=dict(boxstyle="circle,pad=0.14", facecolor=CAT_RED, edgecolor="none"),
                    transform=col_trans, clip_on=False, zorder=8)
        ax.text(j, -0.145, tool, rotation=90, ha="right", va="top", fontsize=21,
                fontweight="bold", color=INK_PRIMARY, transform=col_trans, zorder=7)
    ax.text(-0.5, -0.046 + 0.014, "record / molecule type", ha="right", va="center", fontsize=13.5,
            color=INK_PRIMARY, fontweight="bold", transform=col_trans)
    ax.text(-0.5, -0.098, "dataset size", ha="right", va="center", fontsize=13.5,
            color=INK_PRIMARY, fontweight="bold", transform=col_trans)

    # Semi-transparent prediction-target backing.
    fig.canvas.draw()
    _renderer = fig.canvas.get_renderer()
    _name_bottoms_px = [t.get_window_extent(renderer=_renderer).y0 for t in ax.texts
                         if t.get_rotation() == 90 and t.get_text() in TOOLS]
    _deepest_px = min(_name_bottoms_px)
    ENDPOINT_BRACKET_TOP = ax.transAxes.inverted().transform((0, _deepest_px))[1]
    ENDPOINT_BACK_H = ENDPOINT_BACK_TOP - ENDPOINT_BRACKET_TOP
    for seg_start, seg_end, cid in d["ENDPOINT_SEGMENTS"]:
        x0, x1 = seg_start - 0.5 + ENDPOINT_GROUP_GAP, seg_end - 0.5 - ENDPOINT_GROUP_GAP
        ax.add_patch(Rectangle((x0, ENDPOINT_BRACKET_TOP), x1 - x0, ENDPOINT_BACK_H,
                                facecolor=ENDPOINT_COLOR[cid], alpha=0.28, edgecolor="none",
                                transform=col_trans, clip_on=False, zorder=4))

    bar_new = list(breadth_per_tool)
    BAR_W = 0.52
    x = np.arange(len(TOOLS))
    ax_bar.bar(x, bar_new, width=BAR_W, color=SEQ_450, edgecolor=SEQ_700,
               linewidth=0.6, zorder=3, label=f"of {N_REAL_CATS}, vector cells included")
    top = max(bar_new)
    for j in range(len(TOOLS)):
        ax_bar.text(j, bar_new[j] + top * 0.025, str(bar_new[j]), ha="center", va="bottom",
                    fontsize=14, color=INK_PRIMARY, fontweight="bold")
    ax_bar.set_ylim(0, top * 1.22)
    ax_bar.set_xlim(-0.5, len(TOOLS) - 0.5)
    ax_bar.set_xticks([])
    ax_bar.set_yticks([])
    for spine in ax_bar.spines.values():
        spine.set_visible(False)
    ax_bar.text(-0.012, 0.5, "Categories\npopulated", ha="right", va="center", fontsize=16,
                color=INK_PRIMARY, fontweight="bold", transform=ax_bar.transAxes, linespacing=1.2)
    # Moved outside the plot (to the right, like every other legend on this figure)
    # instead of floating inside the top-right corner of the bars -- it used t
    ax_bar.text(1.045, 0.5, "Categories populated", transform=ax_bar.transAxes,
                ha="left", va="center", fontsize=16, fontweight="bold", color=INK_PRIMARY)

    resolution_legend = [
        Patch(facecolor=GROUP_COLOR_EXACT["Mammals"], edgecolor="none", label="Exact count (colored by category)"),
        Patch(facecolor=BLANK_CELL, edgecolor=BASELINE, linewidth=1, label="Not present"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=CAT_MAGENTA, markeredgecolor="none",
               markersize=10, label="V = vector, not host"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=CAT_RED, markeredgecolor="none",
               markersize=10, label="* = this tool can count one record in several rows"),
    ]
    leg1 = ax.legend(handles=resolution_legend, loc="upper left", bbox_to_anchor=(1.045, 1.0),
                      ncol=1, frameon=False, fontsize=16, labelcolor=INK_PRIMARY,
                      handlelength=1.4, handleheight=1.4, title="Cell = resolution",
                      title_fontsize=17, alignment="left")
    leg1.get_title().set_color(INK_PRIMARY)
    leg1.get_title().set_fontweight("bold")
    ax.add_artist(leg1)

    rectype_legend = [Patch(facecolor=c, edgecolor="none", label=RECTYPE_LABEL[k]) for k, c in RECTYPE_COLOR.items()]
    leg2 = ax.legend(handles=rectype_legend, loc="upper left", bbox_to_anchor=(1.045, 0.80),
                      ncol=1, frameon=False, fontsize=16, labelcolor=INK_PRIMARY,
                      handlelength=1.4, handleheight=1.4, title="Record type",
                      title_fontsize=17, alignment="left")
    leg2.get_title().set_color(INK_PRIMARY)
    leg2.get_title().set_fontweight("bold")
    ax.add_artist(leg2)

    moltype_legend = [Patch(facecolor=c, edgecolor="none", label=MOLTYPE_LABEL[k]) for k, c in MOLTYPE_COLOR.items()]
    leg3 = ax.legend(handles=moltype_legend, loc="upper left", bbox_to_anchor=(1.045, 0.56),
                      ncol=1, frameon=False, fontsize=16, labelcolor=INK_PRIMARY,
                      handlelength=1.4, handleheight=1.4, title="Molecule type",
                      title_fontsize=17, alignment="left")
    leg3.get_title().set_color(INK_PRIMARY)
    leg3.get_title().set_fontweight("bold")
    ax.add_artist(leg3)

    size_examples = [1000, 15000, 250000]
    size_handles = [Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=SEQ_450,
                            markeredgecolor=SEQ_700,
                            markersize=math.sqrt(bubble_area(v, LOG_MIN, LOG_MAX)),
                            label=f"n = {v:,}")
                     for v in size_examples]
    leg4 = ax.legend(handles=size_handles, loc="upper left", bbox_to_anchor=(1.045, 0.30),
                      ncol=1, frameon=False, fontsize=16, labelcolor=INK_PRIMARY,
                      handletextpad=1.1, labelspacing=1.0, title="Dataset size (bubble area)",
                      title_fontsize=17, alignment="left")
    leg4.get_title().set_color(INK_PRIMARY)
    leg4.get_title().set_fontweight("bold")
    ax.add_artist(leg4)

    # Prediction-target legend: writing the category name under each group of
    # columns (tried a bracket, then leader lines) kept adding visual clutter under
    # an already dense cha
    endpoint_legend_handles = [Patch(facecolor=ENDPOINT_COLOR[cid], edgecolor="none", label=ENDPOINT_LABEL[cid])
                                for cid in ENDPOINT_COLOR]
    leg_endpoint = ax.legend(handles=endpoint_legend_handles, loc="upper left", bbox_to_anchor=(1.045, 0.02),
                              ncol=1, frameon=False, fontsize=16, labelcolor=INK_PRIMARY,
                              handlelength=1.4, handleheight=1.4, title="Prediction target",
                              title_fontsize=17, alignment="left")
    leg_endpoint.get_title().set_color(INK_PRIMARY)
    leg_endpoint.get_title().set_fontweight("bold")

    fig.savefig(OUT_PNG, dpi=220, facecolor=PAGE)
    print("saved", OUT_PNG, "|", N_REAL_CATS, "categories +", sum(IS_HEADER), "header rows")


if __name__ == "__main__":
    generate_visualization(process_data(load_data()))
