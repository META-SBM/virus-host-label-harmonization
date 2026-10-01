# Order-level taxonomic breadth figure

```bash
python3 run.py              # output tables and figure from outputs/tools/
python3 run.py --no-figure  # tables only, no R needed
python3 run.py --from-raw   # rebuild outputs/tools/ from the raw downloads first
```

The figure and tables behind the taxonomic-coverage section of the review:
which ICTV families and orders are represented in the datasets of each of the
16 included host-prediction tools.

## Layout

```
config/tools.csv        the 16 tools: display name, prediction endpoint, evidence unit
config/plot_colors.csv  colours used by the figure
tools/<tool>.py         one processor per tool: raw files -> one standardized table
build_tables.py         per-tool tables -> combined -> eukaryotic scope -> output tables
plot_order_figure.R     the figure, drawn with ComplexHeatmap
run.py                  runs all of the above
data/intermediate/      ICTV reference tables and per-tool taxonomy lookups
data/input_original     raw downloads (not distributed; see data/SOURCES.csv)
outputs/tools/          one standardized table per tool
outputs/tables/         the tables the figure and the manuscript use
outputs/figures/main/   the figure, as png, pdf, svg and tiff
```

## Run

```bash
conda env create -f environment.yml
conda activate viral-order-figure
python3 run.py              # output tables and figure from outputs/tools/
python3 run.py --from-raw   # the same, after rebuilding outputs/tools/ from raw data
python3 tools/evomil.py     # re-run a single tool (needs its raw files)
python3 build_tables.py     # rebuild the tables only
```

The figure step needs R with ComplexHeatmap. Without Rscript on the path the
run stops after the tables and says so.

## What the tables mean

Every table in `outputs/tables/` and `outputs/tools/` is written twice, as `.csv`
and as `.xlsx` with the same name (`write_table` in `common.py`).

`outputs/tables/family_presence_eukaryotic.csv` is the working table: one row
per tool and current ICTV family, restricted to eukaryote-associated families.
Everything else is derived from it.

- `order_family_count_matrix.csv` — tools x orders, cell = unique families
- `order_family_count_long.csv` — the same as one row per tool and order
- `tool_summary.csv` — families, order-assigned families and orders per tool
- `order_summary.csv` — tools and families per order
- `families_without_order.csv` — family-level taxa with no order in MSL41.v1
- `supplementary_family_harmonization_table.csv` / `.xlsx` — the evidence behind
  every cell, with the source labels before harmonization

Counts describe the accessible taxonomic breadth of each tool's datasets, not
record abundance, proportional ICTV coverage or model generalizability.

## Input data and what is in version control

The raw inputs are article supplements and tool datasets published by other
authors. They are not redistributed here: `data/input_original` is a link to a
local copy and is excluded from version control. The pipeline does not read
`data/provenance/data_lineage.csv`; it is a large audit table kept locally and
excluded as well. What is tracked is our own work: the processors, the
configuration, the ICTV reference tables and every output table.

`data/SOURCES.csv` records, per tool, each input path the pipeline reads, its
kind, file count and size, a SHA-256 checksum for single files, and the DOI of
the tool's primary publication; the source URL, retrieval date and license
columns are filled in by hand. To verify the per-tool tables, download these
sources into `data/input_original/` under the listed paths, check them against
the checksums and run `python3 run.py --from-raw`. Without the raw files the
default `python3 run.py` reproduces every output table and the figure from the
per-tool tables in `outputs/tools/`.

## Adding a tool

1. Put its raw files under `data/input_original/manual_downloads/<Tool>/`.
2. Add a processor in `tools/` that writes `outputs/tools/<Tool>.csv` with the
   columns listed in `common.py` (one row per source-supported family).
3. Add a row to `config/tools.csv`.

`build_tables.py` stops if a configured tool has no table, or a table has no
row in the config, so the two never drift apart.
