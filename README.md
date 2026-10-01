# Virus–host prediction tools: taxonomic and host coverage of their datasets

Code, processed tables and figures behind two analyses in our review of 16
published virus–host prediction tools. Each folder is self-contained, with its
own README, environment and single run command.

| folder | what it shows | run |
|---|---|---|
| [`taxa/`](taxa/) | which ICTV virus families and orders each tool's datasets cover (order-level heatmap) | `cd taxa && python run.py` |
| [`hosts/`](hosts/) | the hosts each tool's datasets name, harmonized into 50 display categories | `cd hosts && python audit_all.py` |

## Data

The raw inputs are article supplements and tool datasets published by other
authors and are not redistributed here. What is committed is the processing
code, the mapping and reference tables it produces, and every output table and
figure, so both figures rebuild without the raw files. Each raw file is listed
with its location, checksum and DOI in `taxa/data/SOURCES.csv` and
`hosts/sources/MANIFEST.csv`; placing the downloads under `taxa/data/input_original/`
and `hosts/raw_sources/` lets the pipelines also re-derive the processed tables
from them.

Every table is written as `.csv` and as an `.xlsx` copy with the same name.
