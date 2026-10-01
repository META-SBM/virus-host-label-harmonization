#!/usr/bin/env python3
"""Build the order-level taxonomic breadth figure.

    python3 run.py                # output tables and figure from outputs/tools/
    python3 run.py --no-figure    # tables only, no R needed
    python3 run.py --from-raw     # first rebuild outputs/tools/ from the raw downloads

The raw inputs are not distributed with this repository. The per-tool tables
in outputs/tools/ are, so the default run needs nothing else. To check them,
download the sources listed in data/SOURCES.csv into data/input_original/ and
run with --from-raw: each processor in tools/ then rewrites its tool's table.
build_tables.py turns the per-tool tables into outputs/tables/, and
plot_order_figure.R draws the figure from those.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
RAW = REPO / "data" / "input_original"


def run(args: list[str]) -> None:
    print("+", " ".join(str(a) for a in args))
    subprocess.run(args, cwd=REPO, check=True)


def main() -> None:
    if "--from-raw" in sys.argv:
        if not RAW.is_dir():
            raise SystemExit(
                f"{RAW} not found: download the sources in data/SOURCES.csv there, "
                "or run without --from-raw to use the tables in outputs/tools/")
        for processor in sorted((REPO / "tools").glob("*.py")):
            run([sys.executable, str(processor)])
    else:
        print("using the per-tool tables in outputs/tools/ (add --from-raw to rebuild them)")

    run([sys.executable, str(REPO / "build_tables.py")])

    if "--no-figure" in sys.argv:
        return
    rscript = shutil.which("Rscript")
    if not rscript:
        print("Rscript not found; tables are built, figure skipped")
        return
    run([rscript, str(REPO / "plot_order_figure.R")])


if __name__ == "__main__":
    main()
