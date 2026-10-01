# Figure caption — host_general_scheme.png

**Figure Y. Harmonized host coverage across 17 virus–host prediction tools over
18 dataset instances.**

**(Top)** Per tool, how many of this figure's 50 harmonized categories that
tool's data populate.

**(Bottom)** Heatmap of tools (columns) × harmonized host categories (rows),
grouped by lineage. The figure draws 58 rows: 50 analytical categories that
carry data, and 8 bold taxon headers that carry none and exist only to show
which species sit under which taxon. Rows indented beneath a header belong to
that taxon, and "Other *taxon*" holds its remaining records once the species
listed above it are removed. Rows mix taxonomic ranks: species (italicised)
where the source data support it, otherwise order, class, subphylum or kingdom
(see Methods).

Cell colour: saturated = exact count reported, hue = lineage; white = category
absent from that tool's data. **"V"** marks a cell whose records are
arthropod-vector annotations rather than host annotations, used to fill a cell
where that instance reported no host for the row. **"\*"** above a tool name
marks a release that annotates more than one host per virus, so one record can
be counted in several rows of that column and the column total can exceed the
dataset size the study reports.

Squares above each column give the counting unit and the input molecule type.
**The counting unit differs between columns:** ten instances count sequence
records, five count virus taxa, one a deduplicated species pool, and one
(VPF-Class) counts protein-family profiles, which are not viruses at all. **Cell
values are therefore not comparable horizontally between columns as absolute
counts.** They are informative along a row, for which tools cover a given host,
and within a column, for what one dataset consists of. Columns are grouped by
prediction target (coloured band), and HostNet's two dataset instances are
summed into one column for display only.
