# -*- coding: utf-8 -*-
"""
Runs the full pipeline in the one order that's actually valid, so a data
edit anywhere upstream (most often master_labels.csv or one of its rules)
can't leave a downstream CSV, PNG, or xlsx sheet stale without anyone
noticing. Stops at the first failure -- a broken stage should never let
later stages run on data it didn't actually produce.

Order mirrors the dependency chain:
  1. build_master_labels.py          -> master_labels.csv (joins
                                        counts_per_tool_v2/*.csv +
                                        label_enrichment.csv + label_categories.csv)
  2. build_comparison_metrics.py     \ both read master_labels.csv only
     build_species_matrix.py        /
  3. build_general_scheme.py           reads species_matrix.csv
  4. make_general_scheme_heatmap.py  -> the one figure the pipeline still
                                       builds (see the note on stage 4)
  5. export_tables_xlsx.py           -> an .xlsx copy of every table
"""
import subprocess
import sys
import time
from pathlib import Path

SC = Path(__file__).resolve().parent

STAGES = [
    ("1 - core harmonization", ["build_master_labels.py"]),
    ("2 - first-layer derivatives (read master_labels.csv)", [
        "build_comparison_metrics.py",
        "build_species_matrix.py",
    ]),
    ("3 - second-layer derivative (reads species_matrix.csv)", [
        "build_general_scheme.py",
    ]),
    # This tree builds one figure. make_general_scheme_heatmap.py is here for
    # two reasons: it draws a matplotlib rendering of the same matrix, which is
    # a cross-check rather than a publication figure, and
    # export_general_scheme_for_r imports its load_data/process_data, so running
    # it is the cheapest way to know that shared code still works.
    ("4 - figure", [
        "make_general_scheme_heatmap.py",
    ]),    # Every table again as .xlsx next to its CSV. Last, so nothing is stale.
    ("5 - Excel copies of the tables", [
        "export_tables_xlsx.py",
    ]),
]


def main():
    t0 = time.time()
    for stage_name, scripts in STAGES:
        print(f"\n=== Stage {stage_name} ===")
        for script in scripts:
            path = SC / script
            print(f"-> {script}")
            result = subprocess.run([sys.executable, str(path)], cwd=SC)
            if result.returncode != 0:
                print(f"\nFAILED at {script} (stage {stage_name}) -- stopping, "
                      f"later stages were not run and may now be stale relative "
                      f"to whatever this script did produce.", file=sys.stderr)
                sys.exit(result.returncode)
    print(f"\nAll stages completed in {time.time() - t0:.1f}s.")


if __name__ == "__main__":
    main()
