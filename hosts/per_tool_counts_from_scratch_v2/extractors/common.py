# -*- coding: utf-8 -*-
"""Shared paths and CSV-writing helper for the 15 per-tool extraction scripts
(extract_NN_<tool>.py in this folder). Each extractor is a standalone script
(runnable on its own for debugging one tool) that reads from RS
(raw_sources/<Tool>/) and writes its own counts_per_tool_v2/<NN>_<Tool>_counts.csv
via write_csv(). recompute_all.py is the orchestrator that imports and runs
all 15 in order and assembles 00_manifest.csv from their return values.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "raw_sources")
OUT = os.path.join(os.path.dirname(HERE), "counts_per_tool_v2")
os.makedirs(OUT, exist_ok=True)


def write_csv(idx, tool, source_desc, rows, note=""):
    """rows: list of (label, count, match_status). Returns a manifest row
    [idx, tool, fname, source_desc, n_labels, total] for the caller to collect."""
    # Canonical order: count descending, then label. pandas leaves ties in an
    # order that depends on its version, and the byte-for-byte check against the
    # committed files would otherwise inherit that.
    rows = sorted(rows, key=lambda r: (-(r[1] if isinstance(r[1], (int, float)) else 0),
                                       str(r[0])))
    fname = f"{idx:02d}_{tool.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '').replace('/', '-')}_counts.csv"
    path = os.path.join(OUT, fname)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Tool", tool])
        w.writerow(["# Recomputed from", source_desc])
        if note:
            w.writerow(["# Note", note])
        w.writerow([])
        w.writerow(["Label (recomputed)", "Count (recomputed, from scratch)", "Match vs original_reported_labels.xlsx"])
        total = 0
        for label, count, status in rows:
            w.writerow([label, count, status])
            if isinstance(count, (int, float)):
                total += count
        w.writerow([])
        w.writerow(["TOTAL", total, ""])
    print(f"  wrote {fname}  (n={len(rows)}, total={total})")
    return [idx, tool, fname, source_desc, len(rows), total]
