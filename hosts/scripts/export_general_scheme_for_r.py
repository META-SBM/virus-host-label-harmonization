# -*- coding: utf-8 -*-
"""Export the fully-resolved general-scheme figure data for the R/ComplexHeatmap
renderer (make_general_scheme_heatmap.R).

    python3 export_general_scheme_for_r.py

Writes to scripts/r_general_scheme/:
    matrix.csv     rows x tools, counts (0 = absent; header rows are all 0)
    row_meta.csv   display order, name, gloss, lineage, indent, header flag
    col_meta.csv   tool order, endpoint group, annotation tracks, bar values
    cell_flags.csv (row, tool) pairs carrying the "V" vector-fallback badge
    palette.csv    every colour and label the R script needs

Everything written here comes from make_general_scheme_heatmap.process_data(),
so the R figure cannot disagree with the matplotlib one about a number.
"""
import csv
import os

import matplotlib
import numpy as np
from PIL import Image

import make_general_scheme_heatmap as scheme
from icons import EMOJI_AVAILABLE, emoji_silhouette, tick_silhouette

SC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SC, "r_general_scheme")
ICONS = os.path.join(OUT, "icons")

# One glyph per hierarchy header.
TAXON_EMOJI = {
    "Primates": "\U0001F412", "Artiodactyla": "\U0001F416", "Carnivora": "\U0001F43A",
    "Chiroptera": "\U0001F987", "Rodentia": "\U0001F401", "Aves": "\U0001F426",
    "Insecta": "\U0001F99F",
}
TAXON_DRAWN = {"Arachnida": tick_silhouette}
INK_KEYS = ("INK_PRIMARY", "INK_SECONDARY", "GRID", "BASELINE", "SURFACE", "PAGE",
            "SEQ_450", "SEQ_700", "CAT_RED", "CAT_MAGENTA", "BLANK_CELL")

_hex = lambda c: matplotlib.colors.to_hex(c)
_slug = lambda s: s.lower().replace("/", "_").replace(" ", "_")


def load_data() -> dict:
    """The figure's own rows, columns and cells, built by the script that draws
    them."""
    return scheme.process_data(scheme.load_data())


def cell_values(d: dict) -> np.ndarray:
    """The annotated counts back as numbers, in display order."""
    vals = np.zeros_like(d["state"])
    for i in range(len(d["CATS"])):
        for j in range(len(d["TOOLS"])):
            if d["state"][i, j] == 2:
                vals[i, j] = int(d["annot"][i, j].replace(",", ""))
    return vals


def write_matrix(d: dict, vals: np.ndarray) -> None:
    with open(os.path.join(OUT, "matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id"] + d["TOOLS"])
        for i in range(len(d["CATS"])):
            w.writerow([f"r{i + 1:03d}"] + [int(v) for v in vals[i]])


def write_row_meta(d: dict, vals: np.ndarray) -> None:
    """`parent` lets the R script draw the connector spine without re-deriving
    the hierarchy: a depth-1 row belongs to the nearest header above it."""
    with open(os.path.join(OUT, "row_meta.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "name", "gloss", "italic", "lineage", "depth",
                    "is_header", "parent", "source_row", "total"])
        parent = ""
        for i, (name, grp) in enumerate(d["CATS"]):
            if d["IS_HEADER"][i]:
                parent = name
            w.writerow([
                f"r{i + 1:03d}", name, scheme.COMMON_NAME.get(name, ""),
                int(name in d["SPECIES_ROWS"]), grp, d["row_depth"][i], int(d["IS_HEADER"][i]),
                parent if d["row_depth"][i] else "",
                d["cat_orig_rows"][i] or "", int(vals[i].sum()),
            ])


def write_col_meta(d: dict) -> None:
    bubble = d["bubble_size"]
    bmin, bmax = min(bubble.values()), max(bubble.values())
    with open(os.path.join(OUT, "col_meta.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["tool", "endpoint_id", "endpoint_label", "record_type",
                    "molecule_type", "dataset_size", "bubble_mm",
                    "breadth", "double_count"])
        for j, t in enumerate(d["TOOLS"]):
            cid = d["ENDPOINT_CATEGORY"][t]
            # matplotlib scatter s= is an AREA in pt^2;
            w.writerow([
                t, cid, d["ENDPOINT_LABEL"][cid], d["record_type"][t],
                d["MOLECULE_TYPE"][t][0], d["TOTAL_DATASET_SIZE"][t][0],
                round(2.6 + 4.4 * (bubble[t] - bmin) / (bmax - bmin), 3),
                int(d["breadth_per_tool"][j]),
                int(t in d["DOUBLE_COUNT_TOOLS"]),
            ])


def write_cell_flags(d: dict) -> None:
    with open(os.path.join(OUT, "cell_flags.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "tool"])
        for i in range(len(d["CATS"])):
            for t in d["TOOLS"]:
                if (d["cat_orig_rows"][i], t) in d["VECTOR_FALLBACK_CELLS"]:
                    w.writerow([f"r{i + 1:03d}", t])


def write_palette(d: dict, vals: np.ndarray) -> None:
    """Every colour and label the R figure needs, so it is the same figure and
    not a lookalike."""
    rows = [("meta", "n_real_categories", str(d["N_REAL_CATS"]), ""),
            ("meta", "n_header_rows", str(sum(d["IS_HEADER"])), ""),
            ("meta", "n_tools", str(len(d["TOOLS"])), ""),
            ("meta", "total_records", str(int(vals.sum())), "")]
    for k in INK_KEYS:
        rows.append(("ink", k, _hex(getattr(scheme, k)), ""))
    for g in scheme.GROUP_ORDER:
        rows.append(("lineage", g, _hex(scheme.GROUP_COLOR[g]), _hex(scheme.GROUP_COLOR_EXACT[g])))
    for cid, color in scheme.ENDPOINT_COLOR.items():
        rows.append(("endpoint", cid, _hex(color), d["ENDPOINT_LABEL"][cid]))
    for k, c in scheme.RECTYPE_COLOR.items():
        rows.append(("record_type", k, _hex(c), scheme.RECTYPE_LABEL[k]))
    for k, c in scheme.MOLTYPE_COLOR.items():
        rows.append(("molecule_type", k, _hex(c), scheme.MOLTYPE_LABEL[k]))

    with open(os.path.join(OUT, "palette.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "key", "value", "extra"])
        w.writerows(rows)


def write_icons(d: dict) -> None:
    """The same flat silhouettes the matplotlib figure places, dumped as PNGs
    because R cannot render the emoji font either."""
    headers = {name for (name, _grp), h in zip(d["CATS"], d["IS_HEADER"]) if h}
    missing = headers - set(TAXON_EMOJI) - set(TAXON_DRAWN)
    assert not missing, f"hierarchy header with no icon assigned: {sorted(missing)}"

    os.makedirs(ICONS, exist_ok=True)
    for name, arr in scheme.GROUP_ICON_ARRAY.items():
        Image.fromarray(arr, "RGBA").save(os.path.join(ICONS, f"{_slug(name)}.png"))
    for name, ch in TAXON_EMOJI.items():
        Image.fromarray(emoji_silhouette(ch), "RGBA").save(
            os.path.join(ICONS, f"taxon_{_slug(name)}.png"))
    for name, fn in TAXON_DRAWN.items():
        Image.fromarray(fn(), "RGBA").save(
            os.path.join(ICONS, f"taxon_{_slug(name)}.png"))
    print(f"exported {len(scheme.GROUP_ICON_ARRAY)} lineage + "
          f"{len(TAXON_EMOJI) + len(TAXON_DRAWN)} taxon icons -> {ICONS}")


def save(d: dict) -> None:
    os.makedirs(OUT, exist_ok=True)
    vals = cell_values(d)
    write_matrix(d, vals)
    write_row_meta(d, vals)
    write_col_meta(d)
    write_cell_flags(d)
    write_palette(d, vals)
    if EMOJI_AVAILABLE:
        write_icons(d)
    else:
        # The icons are rasterized from the system's Apple Color Emoji font, so
        # they can only be regenerated on macOS. Elsewhere the committed PNGs in
        # icons/ are kept, which is what the figure reads anyway.
        print(f"icons not regenerated off macOS; keeping the committed ones in {ICONS}")
    print(f"exported {len(d['CATS'])} display rows ({d['N_REAL_CATS']} categories + "
          f"{sum(d['IS_HEADER'])} headers) x {len(d['TOOLS'])} tools -> {OUT}")


if __name__ == "__main__":
    save(load_data())
