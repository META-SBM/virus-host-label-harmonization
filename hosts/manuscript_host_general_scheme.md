# Host scheme figure — caption, Methods and Results

**Figure file:** `host_general_scheme_R.png`

*This is the complete manuscript text for that one figure: its caption, the
Methods subsection that produces it, and the Results drawn from it. Key
numerical summaries are recomputed from the committed tables by
`scripts/verify_reported_numbers.py`, which fails if any of them drifts.
Derivations, sensitivity analyses and per-record evidence are in
`supplementary_methods_host_harmonization.md`. Assembled 2026-10-01 by
`scripts/build_manuscript.py` from the three files it lists -- edit those, not
this one.*

**Counting units differ between dataset instances** (sequence records, virus
taxa, a deduplicated species pool, protein-family profiles). No statement in the
Results aggregates observation counts across instances. Magnitudes are reported
as counts of tools or dataset instances, as presence or absence, or as shares
within a single instance.

---

## Figure caption

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

---

## Methods — 3.3 Host-label harmonization

## Sources and scope

Host labels from 17 published virus–host prediction tools were independently
recomputed from each tool's original raw source files or supplementary data,
rather than taken from secondary descriptions. HostNet contributes two dataset
instances, developed separately for rabies virus and for flaviviruses, giving 18
dataset instances across 17 tools. These are treated as
distinct throughout and summed into a single column only for display. Extraction
yielded 8,076 raw label records.

Each tool is represented by the complete labeled pool its study released, with
three documented departures: MENB and SPHAK, where the training corpus is what
the study reports as its dataset, and HostNet (Rabies, VIPHOD), where a released
validation split is excluded because including it contradicts the tool's own
reported total. Elsewhere, available train, validation and test splits were
deliberately not applied, since restricting to a training slice would report
figures against which no published analysis was computed. Per-instance scope,
with the alternatives rejected and the reason, is recorded in `DATASET_SCOPE`.

Every raw file is identified by SHA-256 in `sources/MANIFEST.csv`, which also
carries a DOI or download URL where one is recorded and the marker MISSING where
none is. All 34 files now carry a resolvable download URL, and for 19 of them the
published file was re-fetched and confirmed identical to the copy the numbers were
computed from, by SHA-256 where the file could be downloaded whole and by the
size and checksum a repository or archive declares for it where it could not.
Provenance is not complete in one respect: 24 files have no recorded retrieval
date, and a date cannot be reconstructed after the fact, so those read MISSING.

## Counting units

Counting-unit granularity and input-molecule type were recorded per tool from
its article. Ten instances count sequence records, five count virus taxa, one a
deduplicated species pool, and one protein-family profiles. The last is
VPF-Class, whose values are not comparable with any record count elsewhere and
which carries its own record-type mark on the figure. **These units are not
interconvertible, and no analysis in this work sums observations across
instances of different units.** The one quantity that does span all instances,
603,953 total source observations, is used solely as a processing checksum on
the routing step and is not a corpus size, a dataset size, a number of records
analysed or a number of viruses. Its composition is given in Supplementary
Methods.

Releases that allow multi-host annotation per virus, DeepHoF and RNAVirHost,
were preserved as reported, to preserve the source annotation structure and
avoid arbitrary selection of a single host. The affected columns are marked on
the figure, and their column totals exceed the dataset size their studies report.

## Where the host was hardest to determine

These releases are not one corpus sampled in different ways. What a single record
is differs between them, and the studies name their own record type in twelve
different ways, among them genome records, sequence records, accession-pair rows,
virus-host associations, pathogen records, database records and protein-family
profiles. The host was read from a different place in each release, and those
places are not of one kind. Most carry a host column in a table. Host Taxon
Predictor carries a free-text host field beside an NCBI lineage inside a pickled
Python object. VirHostPRED and MosViR carry it in FASTA headers, DeePaC-vir in an
R data object, VPF-Class in a table of protein-family profiles, and MENB only in
a figure in a supplementary PDF, the one instance whose labels could not be read
from a machine-readable file at all. Per-instance detail is in Table S1.

Five situations arose in which no reading of the release yields a host in the
sense the other instances mean. Each is marked in the data rather than smoothed
away.

1. **The host is absent.** 1,148 records across four instances name no host,
   1,133 of them in HostClassifier, where the field reads "Unknown", some
   spelling of "cell culture", or nothing. A further 972 HostClassifier records
   give a class but no species, such as "Avian" or "Mammal" with the species
   field blank. These enter the matrix at the rank the release supports and no
   finer.

2. **The host is defined by exclusion.** VirHostPRED's negative class is 2,127
   records labelled only as not human. There is no taxon to resolve. What the
   class contains is a design choice of the study and not a statement about
   which hosts the virus has.

3. **The record names a vector rather than a host.** HostNet (Flavivirus) and
   ViralHostPredictor contribute 9,766 records whose annotation is the arthropod
   the virus was collected from, 9,721 of them in cells that are wholly
   vector. These fill the mosquito and tick rows and carry a "V" mark on the
   figure, so that a vector annotation is never read as a host record.

4. **One record names several hosts.** RNAVirHost annotates 17,063 records
   through 2,496 multi-host labels, and DeepHoF 12,211 records through a
   multi-tag host column. One such record contributes to every row its hosts
   fall in.

5. **The unit is not a virus.** VPF-Class classifies viral protein families
   rather than viruses. A row of its release is a profile and a candidate host,
   weighted by the share of that profile's hits, so one virus contributes many
   profiles and one profile spans many viruses. A profile also names a
   distribution rather than a host, up to 82 genera at once, with a median hit
   share of 1.6% on its eukaryotic rows. That distribution collapses at one cut
   only. The shares sum to one hundred, so above 50% at most one host can
   qualify, and each profile then lands in exactly one cell by arithmetic rather
   than by judgement. 12,253 of the 19,056 profiles in the genus-level table
   clear that cut, and 1,995 of those name a eukaryotic host genus, led by
   *Homo* with 1,247 and *Aureococcus* with 562. The remaining 10,258 name a
   bacterial or archaeal genus and fall outside a review of eukaryotic hosts.
   The article's own operating point for host prediction, a membership ratio of
   0.3, is not used, because at that cut one profile can carry three genera and
   counting it would count the same profile three times. Only the genus table is
   used. The three rank tables are reclassified independently and do not nest,
   with 219 of the 1,064 profiles the domain table calls Eukaryota at 100%
   carrying a bacterial family one rank down, so they cannot be combined and
   genus is the finest of them. The column therefore carries its own record-type
   mark stating that a profile is not a virus, and its values stand beside no
   other column as counts. Coverage at three membership cuts is in Table S3, and
   `scripts/assess_vpf_class.py` recomputes each of these grounds from the raw
   files and fails if any stops being true.

A sixth difficulty runs through all of them and is a property of the names
rather than the records. The same species arrives under different spellings,
*Canis lupus* under eight of them, and vernacular names sit in the same field as
binomials, as with Host Taxon Predictor's "human", "bovine" and "goose". This is
what the synonym collapse described below is for, and it is the reason a label
counted as released is not the same thing as a host.

## Mapping confidence

Every label was assigned a mapping confidence recording how directly its text
determines the category it was placed in. Of the 7,508 labels carried into the
analysis, 91.6% are high confidence, meaning direct taxonomic matches such as
*Sus scrofa*. A further 8.1% required interpretation but admitted only one
defensible reading. These are mainly of two kinds. One is an informal name used
in place of a taxon, as with GIVAL's "Canine" and "Equine", HostClassifier's
"arthropod", or Host Taxon Predictor's "bovine" and "goose". The other is a
genus standing in for a coarser display class, as with SPHAK's *Capsicum* placed
in Plants or HostClassifier's *Simia* placed in Non-human primates.

The remaining 0.3% were low confidence, denoting no taxon at all or one fixed
only by a convention internal to the source. All 22 are listed in Supplementary
Methods, and they fall into three kinds. The largest records that no host was
captured, as with HostClassifier's 635 records reading "Other (species not
recorded)" and its 63 records spread over three spellings of "cell culture". The
second is a class defined by exclusion rather than by a taxon, VirHostPRED's
2,127 records labelled only as not human. The third is a grouping a study
introduced after the fact, as with GIVAL's post-hoc coronavirus subsets PRI and
CHI, which the article names but does not count separately. Shares are given per label.
Observation-weighted equivalents are reported in Supplementary Methods, where
their dependence on a single instance is set out. 568 labels carrying 27,199
observations were excluded, 563 of them non-eukaryotic hosts and the remaining 5
placeholders naming no host.

## Taxonomic resolution

Resolution was curatorial. Host names were normalised against a
project-internal synonym table and a per-label category assignment, without a
pinned release of any external taxonomic database. Every individual
harmonization act is recorded in `scripts/host_harmonization_provenance.csv`,
one row per released label and resolved entity, naming which curation rule
fired. Infraspecific names were collapsed onto their binomials prior to counting
to prevent fragmentation, so that *Canis familiaris* and *Canis lupus
familiaris* were treated as *Canis lupus*. Hybrids and provisional
determinations, cf. and aff., were excluded from this collapse.

A subset of names was checked against NCBI Taxonomy on 2026-09-08 and is
recorded with taxid, rank and query URL in
`scripts/host_name_authority_checks.csv`: all 26 species drawn as standalone
rows on the figure, the three species named in the Results text, and both sides
of all four binomial synonym substitutions. All 33 checks returned the accepted
scientific name at rank species, and every substitution is recorded by NCBI as a
synonym of the target used here. **The remaining host entities carry no
taxonomic identifier**, and this is stated as a limitation rather than implied
otherwise: 30 of the 1,513 entities have a taxid.

Resolution recovers more species than the figure displays. A species is drawn as
its own entity only if at least two dataset instances name it or one gives it at
least one hundred observations. Names below that materiality bar are displayed
inside their category's residual row. Counts are in Supplementary Methods. The
matrix therefore holds 1,513 distinct host entities, which is a display figure
and not the number of species the data name.

## Routing to display categories

To prevent the final matrix from being dominated by singletons, entities were
routed to 50 display categories using a fixed-priority protocol:

1. **Cross-study species consensus.** A species independently annotated by at
   least 6 of the 18 dataset instances was retained as its own category. This
   threshold preserved 26 species, spanning major domestic animals (*Homo
   sapiens*, *Sus scrofa*, *Gallus gallus*) and key wildlife reservoirs
   (*Desmodus rotundus*, *Vulpes vulpes*, *Macaca mulatta*). The threshold is an
   editorial choice and not an optimum. A sweep over every threshold from 1 to 8
   instances informed it and is reported in Supplementary Methods.

2. **Vector and crustacean carve-outs.** Mosquitoes (Culicidae) and ticks
   (Ixodida) were retained as named categories irrespective of the consensus
   rule, given their role as arboviral vectors. Crustacea was retained on a
   separate ground, that the aquaculture hosts it holds have no dedicated
   category in the harmonized vocabulary. Nineteen entities were mapped
   explicitly and a further 70 caught by a genus-level rule, so that a newly
   resolved vector species cannot fall through into a generic invertebrate
   bucket. The three rows sit at three taxonomic ranks, family, order and
   subphylum, since the carve-out is by biological role and not by rank.

3. **Mapping to a prespecified higher-rank display category.** The remaining 830
   entities were mapped to one of eleven prespecified higher-rank categories
   (Chiroptera, Rodentia, Carnivora, Artiodactyla, Aves, Reptilia, Amphibia,
   Arachnida, Plantae, Other mammals, Other invertebrates) on the basis of their
   harmonized category rather than by stepwise ascent of a taxonomy. The
   destination may therefore stand several ranks above the entity. A further 568
   entities were used unchanged, their harmonized category serving directly as
   the display row.

## Reading the matrix

The 50 display rows form a partition of the 1,513 host entities, in that each
entity occupies exactly one row, and this is asserted at build time. It does not
follow that each viral record occupies one row. For the two releases that
annotate several hosts per virus, one record contributes to every row its hosts
fall in. The routing step itself conserves observations exactly, which is the
checksum described above.

Raw absolute counts must not be compared horizontally between columns, and each
column carries a mark stating its unit. To prevent misinterpretation of the
rows, residual class- and order-level rows that lost species to the retention
rule are displayed as one of eight headers over their constituent species and an
"Other" residual, so that Carnivora heads *Canis lupus*, *Vulpes vulpes* and
"Other Carnivora", giving 58 drawn rows for 50 categories.

Two properties of released files are reported rather than silently corrected,
on the same principle that each instance is represented as its study released
it. 235 records in VirHostPRED's human-infecting class derive from two
bacteriophage source organisms. 773 rows of SPHAK's animal training file are
exact duplicates of another row in the same file, identical in every field
including the sequence, and they account for 5.7% of that instance's
observations. Both were retained, the first to preserve the released class
composition and the second because SPHAK's own reported dataset total counts
them, so removing them would put this figure out of step with the publication it
describes. Neither is a multi-host record of the kind DeepHoF and RNAVirHost
carry. Both are flagged per accession, with detail and evidence in Supplementary
Methods.

Full label-level provenance is provided in Supplementary Data. Table S4 gives
every label as its tool released it, Table S2 every host entity before the
display threshold, Table S1 the per-tool source file, field and scope, and Table
S3 the profile coverage behind the one instance that counts protein families
rather than viruses.

The figure and every number quoted from it rebuild from the archived raw files
by a single command, which verifies the 34 source files against their checksums,
recomputes the per-tool counts, rebuilds each table in dependency order,
re-renders the figure, re-derives every drawn cell, and re-checks every value
stated in this section and in the Results against the rebuilt tables.

---

## Results

We brought the host labels of eighteen dataset instances into one vocabulary and
obtained a matrix of 50 analytical categories by 17 tools, drawn as 58 rows once
the eight taxon headers are counted, with 349 of the 850 possible
tool-by-category combinations filled, or 41.1% occupancy (Figure Y). The 603,953
source observations behind it serve as a processing checksum only, for the
reasons set out in the Methods, and no share of that number is quoted here.

The bars above each column of Figure Y report how many of the 50 harmonized
categories a study's data populate. Set against what each article says it
distinguishes, the two disagree, and in both directions. VIDHOP reports 51
labels of its own but populates 22 categories, because its labels are tied to
particular viruses rather than to taxonomy, so many of them fall into the same
category. Host Taxon Predictor reports 6 but populates 48, because its released
file carries a full host lineage beside the coarse class the tool predicts, and
we counted that lineage. DeePaC-vir states 2 classes and populates 48 for the
same reason. The number a study reports therefore says little about what its
data contain: the harmonized categories describe the dataset, not the resolution
at which the tool answers. Category breadth spans almost the whole scheme, from
2 categories of 50 in three instances to 48 in two others, and it does not track
counting unit, since the two widest are one taxon-counting and one
sequence-counting instance.

*Homo sapiens* is the only category that most of the field shares. It is named
by 15 of the 18 dataset instances, and by instances of all four counting-unit
classes. The three exceptions are not gaps in coverage but differences in
subject: ViralHostPredictor resolves humans only inside an order-level primate
category, while HostNet (Flavivirus) and MosViR annotate vectors rather than
hosts. No other category comes close. Three are named by 11 instances (Aves,
Carnivora, Plantae), and the median category is named by 7. Two of the 50 are
named by a single instance each. Agreement across the field is thin almost
everywhere outside humans.

The domestic dog is the next most widely recognised mammal, but seeing it took
work. *Canis lupus* is named by 9 of the 18 instances, and it reaches the matrix
under eight different spellings. "*Canis lupus*" and "*Canis lupus familiaris*"
are each used by 5 instances and "*Canis familiaris*" by 3, none of which clears
the six-instance threshold on its own. Counted as released, the signal dissolves
into the generic carnivore row, and it appears only once synonyms are merged
before counting. Its weight within a dataset varies as much as its spelling.
Across the 12 instances that hold any carnivore records at all, the dog's share
of that instance's own carnivore records runs from 0% to 68.2%, and it is the
largest carnivore row in 5 of those 12. The two rabies datasets, VIDHOP and
HostNet (Rabies, VIPHOD), sit at the top of that range.

Wild hosts are widely recognised across the field but thinly sampled inside each
dataset. Nine bat, rodent and non-human primate species clear the retention
threshold, among them *Desmodus rotundus*, *Rattus norvegicus* and *Pan
troglodytes*, and every one of them is named by exactly six instances, one third
of the field. Their weight inside any one dataset is small: of the 54
instance-by-species cells they occupy, 44 account for 1% or less of that
instance's own records, and the largest reaches 4.5%. A host can be recognised
by a third of the field and still be a rounding error in every dataset that
recognises it.

A cross-dataset summary hides how little the datasets overlap in subject.
Computed per column of Figure Y, the human share of an instance's own records
covers the whole available range: three instances hold none at all,
HostClassifier takes 54.3% and DeepHoF 59.1%. Seven instances take at least 40%
from humans, six take 12% or less. The
number of broad lineages an instance touches at all runs from one to eight.
VirHostPRED has only a human and a non-human class, both of them mammalian by
construction, while DeePaC-vir and Host Taxon Predictor alone hold records in
all eight. What separates these tools is subject, not size, and subject does not
follow from purpose: plants supply 32.3% of RNAVirHost's records and 27.9% of
DeePaC-vir's, yet 0% of VIDHOP's and of VirHostPRED's, though DeePaC-vir and
VirHostPRED are both human-infectivity classifiers. Invertebrates supply 45.2%
of HostNet's merged column. Two tools of the same size can share almost no host.

The human-infectivity tools deserve a separate note. In these, the animal labels
mainly define the non-human class rather than taxa the tool can name. The
presence of bat, rodent or avian viruses in their data therefore cannot be read
as an ability to identify those hosts.

Plants and fungi stayed at kingdom level on the figure not because the data are
missing, but because the retention threshold is out of reach for them. The
distinction matters at two levels. Resolution recovered 1,044 plant species
names and 189 fungal ones. Of these, 457 plant and 102 fungal species clear the
materiality bar and hold a row of their own in the full host table, Table S2.
None of them clears the six-instance retention threshold, so **not one appears
as a standalone species row in the 50-category figure**, where every plant sits
inside Plantae and every fungus inside Fungi. The reason is structural rather
than biological: only 5 of the 18 dataset instances name a plant species at all,
and only 4 name a fungal species, against 15 that name a mammal species. No
plant species can therefore be reported by more than five instances, and a
six-instance threshold is unreachable by construction. The most frequently named
are ordinary crop and model species, *Solanum lycopersicum*, *Zea mays* and
*Oryza sativa*. Amphibians are named by 4 instances and reptiles by 7, showing
the same pattern. Coverage beyond mammals and birds is broad in category names
but shallow in how many datasets support it.

Three caveats govern how the figure is read. The rows are mutually exclusive as
a vocabulary, so a row and the header above it must not be summed: "Other
Carnivora" is carnivores minus the species drawn under the same header. That
exclusivity is a property of the row set and not of the underlying records,
since two releases annotate several hosts per virus, so one record can
contribute to more than one row, which is why their column totals exceed the
dataset size their studies report. And cell values are informative along a row,
for which tools cover a given host, and within a column, for what one dataset
consists of, but not between columns as raw counts, since the studies count in
different units and report datasets of differing scope. For that reason no
statement above sums observations across dataset instances.
