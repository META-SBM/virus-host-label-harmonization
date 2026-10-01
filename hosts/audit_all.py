#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One command, one verdict: is host_general_scheme_R.png reproducible today?

    raw files are the ones analysed        verify_raw_sources.py
    counts come from those files           verify_against_committed.py
    tables come from those counts          run_all.py
    the thresholds not used still hold     sweep_threshold.py
    the figure comes from those tables     export + Rscript
    every drawn cell re-derives            verify_general_scheme_figure.py
    the manuscript matches its sources     build_manuscript.py
    every quoted number still holds        verify_reported_numbers.py
    every host entity occupies one row     make_full_host_table.py
    every reported label has a provenance  (checked here)

    python3 audit_all.py                 # everything
    python3 audit_all.py --no-render     # skip the R step (no R toolchain needed)
    python3 audit_all.py --list          # show the stages without running them

The raw files are third-party data and are not distributed. Without them under
raw_sources/ the four stages that read them are skipped and say so; everything else runs
from the committed per-tool counts. Every table is also mirrored to .xlsx by the
last stage.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(ROOT, "scripts")
PT = os.path.join(ROOT, "per_tool_counts_from_scratch_v2")
PY = sys.executable
RAW = os.path.join(ROOT, "raw_sources")


def raw_files_present() -> bool:
    """True when the downloaded tool folders are under raw_sources/, not just
    the manifest and README that are committed."""
    if not os.path.isdir(RAW):
        return False
    return any(os.path.isdir(os.path.join(RAW, d)) for d in os.listdir(RAW))


def rscript() -> str:
    """The Rscript to use, or None if no environment is configured."""
    env = os.environ.get("RENV")
    if env:
        cand = os.path.join(env, "bin", "Rscript")
        if os.path.exists(cand):
            return cand
    return shutil.which("Rscript")


STAGES = [
    ("raw sources match their checksums", SC, [PY, "verify_raw_sources.py"], False),
    ("counts reproduce from raw files", PT, [PY, "verify_against_committed.py"], False),
    ("pipeline rebuilds every table", SC, [PY, "run_all.py"], False),
    ("threshold sweep rebuilt", SC, [PY, "sweep_threshold.py"], False),
    ("figure inputs exported", SC, [PY, "export_general_scheme_for_r.py"], False),
    ("figure rendered", SC, None, True),                      # filled in at runtime
    ("every drawn cell re-derives", SC, [PY, "verify_general_scheme_figure.py"], False),
    ("manuscript assembled from its sources", SC, [PY, "build_manuscript.py"], False),
    ("quoted numbers still hold", SC, [PY, "verify_reported_numbers.py"], False),
    ("provenance table rebuilt", SC, [PY, "make_provenance_table.py"], False),
    ("full host table rebuilt", SC, [PY, "make_full_host_table.py"], False),
    ("pre-harmonization table rebuilt", SC, [PY, "make_before_harmonization_table.py"], False),
    ("VPF-Class exclusion still holds", SC, [PY, "assess_vpf_class.py"], False),
    ("VPF-Class coverage rebuilt", SC, [PY, "make_vpf_class_coverage.py"], False),
    ("tables mirrored to .xlsx", SC, [PY, "export_tables_xlsx.py"], False),
]
# The stages that read the raw files; skipped when they are not downloaded.
NEEDS_RAW = {"raw sources match their checksums", "counts reproduce from raw files",
             "VPF-Class exclusion still holds", "VPF-Class coverage rebuilt"}
# Retired 2026-09-09 with the scope decision. Two stages checked the provenance
# of original_reported_labels.xlsx, whose only consumers were the grey bar on
# two figures that are now legacy. The audit was policing a file nothing needs.
# classify_reported_labels.py is still in the tree and still runs by hand.


def run_stage(cmd: list, cwd: str) -> tuple:
    """A stage fails on a non-zero exit code, or on saying so in its own output:
    the two verifiers report their verdict in the body, not the return code."""
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    dt = time.time() - t0
    body = r.stdout or ""
    if r.returncode != 0:
        return False, dt, body + "\n" + (r.stderr or "")
    if "FAILED" in body or "УПАЛО: " in body and "УПАЛО: 0" not in body:
        return False, dt, body
    return True, dt, body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-render", action="store_true", help="skip the R rendering stage")
    ap.add_argument("--list", action="store_true", help="print the stages and exit")
    args = ap.parse_args()

    if args.list:
        for i, (name, *_rest) in enumerate(STAGES, 1):
            print(f"  {i}. {name}")
        return 0

    rs = None if args.no_render else rscript()
    have_raw = raw_files_present()
    started = time.time()
    width = max(len(s[0]) for s in STAGES) + 2

    for i, (name, cwd, cmd, is_render) in enumerate(STAGES, 1):
        if name in NEEDS_RAW and not have_raw:
            print(f"  {i}. {name:<{width}} SKIPPED  (raw files not in raw_sources/; "
                  f"download them per sources/MANIFEST.csv)")
            continue
        if is_render:
            if rs is None:
                print(f"  {i}. {name:<{width}} SKIPPED  (no R; set RENV or pass --no-render)")
                continue
            cmd = [rs, "make_general_scheme_heatmap.R"]
        ok, dt, body = run_stage(cmd, cwd)
        if not ok:
            print(f"  {i}. {name:<{width}} FAILED   ({dt:.0f}s)\n")
            print(body[-3000:])
            print(f"\nFAILED at stage {i}: {name}")
            return 1
        print(f"  {i}. {name:<{width}} ok       ({dt:.0f}s)")

    if have_raw:
        print(f"\nPASS — the figure and every number in it reproduce from the sources "
              f"({time.time() - started:.0f}s).")
    else:
        print(f"\nPASS from the committed per-tool counts ({time.time() - started:.0f}s); "
              f"the raw-file stages were skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
