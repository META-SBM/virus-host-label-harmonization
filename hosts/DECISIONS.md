# Decisions

Choices this project made that cannot be verified, only declared. Each one
states the rule, what was rejected, and why. Anything that *can* be verified
lives in `audit_all.py` instead; anything a paper states lives in
`reported_labels_provenance.csv`.

---

## 1. A species stays its own row at ≥6 of 17 dataset instances

Species named by at least six independent dataset instances keep their own
category; the rest fold into their order, class or kingdom. The bar counts
independent instances, not records, so it measures cross-study agreement rather
than the size of any one dataset, and it is recomputed at every build.

The rule exists because four tools were re-extracted to species level, which
ballooned the scheme to 104 categories, most of them a single tool's single
species. Without a bar the "compact" scheme is not compact.

**Why six.** The choice is not free — the whole shape of the figure turns on it:

| bar | share of 17 | species kept | categories |
|---|---|---|---|
| ≥1 | 6% | 1,462 | 1,469 |
| ≥4 | 24% | 293 | 310 |
| ≥5 | 29% | 90 | 109 |
| **≥6** | **35%** | **26** | **49** |
| ≥7 | 41% | 12 | 35 |
| ≥8 | 47% | 8 | 31 |

Recomputed by `sweep_threshold.py`, which runs the real builder at each setting
against its own output prefix, so the row that is not used is as trustworthy as
the row that is. Note that "species kept" is species clearing the bar, which is
a few more than are drawn as their own row below ≥6: the vector and crustacean
mappings are checked first and route some of them to a finer category by name.

`decisions_threshold_5_vs_6.png` renders 5 and 6 side by side at identical row
height. At five the matrix is 109 categories over 117 rows and 36.5% filled: page
after page of *Vicugna pacos*, *Lynx rufus*, *Myodes glareolus*, *Varecia
variegata*, each one tool, each a single-digit count — the singleton-dominated
state the rule exists to prevent. At six it is 49 categories over 57 rows and
43.2% filled.

**Why not seven.** All nine wildlife reservoirs that a virus–host review is
actually about — *Desmodus rotundus*, *Tadarida brasiliensis*, *Eptesicus
fuscus*, *Rattus norvegicus*, *Mus musculus*, *Mesocricetus auratus*, *Pan
troglodytes*, *Macaca mulatta*, *Chlorocebus aethiops* — sit at exactly six.
Seven drops all nine at once, and bats, rodents and primates appear only at
order level, which reads as a figure blind to wildlife ecology.

**The bar moved once, and the reason matters.** It was ≥5 when the corpus had 15
instances. Citation searching added DeePaC-vir and MosViR, the denominator became
17, and because the bar is a *count* a larger denominator loosens it: ≥5 of 17
retained 90 species. The rule is really about a proportion, and ≥6/17 (35%) is
the same bar as ≥5/15 (33%). The nine species above were checked rather than
assumed — every one of them moved from exactly 5 of 15 to exactly 6 of 17,
because DeePaC-vir's Virus-Host DB labels cover all nine. **If another tool is
added, re-check this number.**

---

## 2. Each tool is scored on what its own study calls its dataset

Not on a slice chosen retrospectively. For most instances that is the complete
labelled release with no split filter; for MENB and SPHAK it is the training
corpus, because that is what those studies report.

Several instances ship a usable train/validation/test split that is deliberately
not applied. Restricting to a training slice would report figures against which
no published analysis was computed, and would silently make tools
incomparable — some have a split, some do not. Per-instance reasoning, including
the rejected alternatives by filename, is in `DATASET_SCOPE`.

---

## 3. DeepHoF's `germ` class is excluded as non-eukaryotic

12,020 records. Resolving the accessions shows 11,529 are viruses of bacteria or
archaea and 491 of fungi, protists and algae (`scripts/resolve_germ.py`). This is
a eukaryotic-host review, so the class is dropped rather than shown as an
unresolved host — showing it would put 12,020 prokaryote records into a figure
about eukaryotic hosts under a label that does not say so.

The same logic excludes MosViR's `other viruses` (620,553 sequences): it is the
not-mosquito-associated background for a first classification step, asserts no
host at all, and its accessions are truncated so eukaryotic scope cannot even be
checked.

---

## 4. Vector records are shown, and marked, rather than dropped

Arthropod vector and crustacean taxa are routed to named categories (Culicidae,
Ixodida, Crustacea) rather than folded into "Insects"/"Arachnids", because vector
identity is more informative than taxonomic economy in this field.

Vector records are **added** to their cell even when the cell already holds host
records. An earlier rule filled only empty cells, which made whether a vector
record appeared depend on an unrelated host label — ViralHostPredictor's eleven
minor vector labels vanished because its own "Insect (reservoir)" had already
claimed Insecta.

The "V" badge marks any cell carrying vector records, and those cells count in
the bar like every other. They were once discounted where a cell held nothing
but vector, which kept a vector-only instance from claiming host breadth; that
was a biological judgement laid over a figure that otherwise reports the
harmonization as it stands, and the badge already carries the distinction. The
change moves four cells and two columns: HostNet 15 to 17, ViralHostPredictor
12 to 14.

---

## 5. Infraspecific names collapse to their binomial before counting

Otherwise a species is fragmented by how each study spelled it. The case that
forced this: *Canis lupus familiaris* (5 instances), the bare binomial (5) and
*Canis familiaris* (3) each fall below the retention bar, while the merged
species reaches nine instances and 12,434 records — 61% of all carnivore
records. A host can be erased by nomenclature alone.

Hybrids and provisional determinations (`cf.`, `aff.`) are excluded from the
collapse; the binomial synonyms applied are listed explicitly rather than
inferred.

---

## 6. Only genuine taxa are nested

A hierarchy block is drawn wherever the scheme holds two or more rows of one
parent taxon: the taxon as a data-free header, its members indented, the
parent's remainder relabelled "Other &lt;taxon&gt;" so it is explicit that the
remainder excludes the species above it. Without that relabelling a reader sees
a small Carnivora count and concludes a tool is weak on carnivores, not noticing
the cats and foxes are separate rows.

Harmonized categories that describe how a study *lumped* its labels — "Non-human
primates", "Humans + non-human primates" — are **not** nested, even though they
are primates. They are not taxa, and indenting them under Primates would imply a
rank they do not have. They stand as their own rows at the foot of their lineage.

---

## 7. HostNet's two dataset instances are summed for display only

HostNet released two separately developed datasets, for rabies and for
flaviviruses. They are distinct everywhere in the data and are summed into one
column purely so the figure has one column per tool. Merging upstream would corrupt per-instance breadth and
human-dominance metrics, which are computed before the display merge; the
flavivirus instance is vector-only and its two cells are the ones the merged
column carries a "V" on.

---

## 8. Double counting is preserved, not deduplicated

DeepHoF counts invertebrate and plant tags independently of other tags on the
same record; RNAVirHost expands a multi-host virus into one row per named host.
Both inflate their column totals. Deduplicating would require choosing
arbitrarily which host to keep — an editorial act on someone else's data — so
the counts stand as the tools report them and the columns are marked `*`.

---

## 9. Two palettes, separated by chroma rather than hue

Host lineages and tool prediction targets are different dimensions on one
figure. Their first palettes were near-copies in hue — a blue against a blue, a
green against a green — so the same colour meant two things.

Twelve categories cannot be separated by hue alone; the wheel is full. They are
separated by register instead: lineages are vivid and carry the data, tool groups
are mid-chroma and only group. Distances were computed across all cross-pairs
rather than judged by eye, both at full saturation and at the 68% tint the cells
actually use, because any dark red tints toward the same pastel as a magenta.

---

## 10. A released label is overridden only where the file contradicts itself

SPHAK's `animal_train.csv` gives *Phalacrocorax auritus* — a cormorant, host of
Avian orthoavulavirus 1 — the aggregate category `Plant` (2 records,
`ACT22862`, `ACT22868`). The species column and the aggregate column of the same
row disagree, and this project extracts the species column precisely because it
is the finer of the two, so the label is curated as a bird, matching
HostClassifier's curation of the identical name.

This is the only override of its kind. It was found by the full host table,
which showed one entity occupying two rows — the split is the symptom, and the
same symptom previously exposed four cetaceans curated as fish and a tick
curated as unresolved. Nothing is overridden on plausibility alone: the rule is
that one released row must contradict itself.

The figure never showed the error. Routing takes one vote per tool on the
harmonized category, and HostClassifier's reading of the same name outvoted
SPHAK's, so the records were already drawn under Aves. What the error did reach
was the species-level tables, where the entity sat twice under two lineages, and
the count of plant species, which was 458 with a cormorant among them.

---

## 11. VPF-Class is a column, at the one cut that makes it countable

Its released tables classify viral protein families, not viruses: a row is a
profile and a candidate host, weighted by the share of that profile's hits. A
profile is not a virus — one virus contributes many, one profile spans many —
and a profile names a distribution, up to 82 host genera at once.

That distribution collapses at one place. The shares sum to 100, so above 50%
only one host can qualify: at that cut each profile lands in exactly one cell,
by arithmetic rather than by judgement, and the column is well defined. The
article's own operating point for host prediction, membership ratio 0.3, is not
used here — at 0.3 a profile carries up to three genera and counting it would
count the same profile three times.

So the tool has a column and the column has its own record-type swatch,
"Protein-family profile (not a virus)". The figure already warns that columns
are not comparable as raw counts because the studies count in different units;
this extends that from three ways of counting viruses to a unit that does not
count viruses at all, which is why the swatch says so rather than leaving it to
the caption. 12,253 profiles qualify, 1,995 of them naming a eukaryotic host:
*Homo* 1,247, *Aureococcus* 562, *Apis* 65, *Mus* 54, *Ectocarpus* 45.

Only the genus table is used. The three rank tables are reclassified
independently and do not nest — 219 of the 1,064 profiles the domain table calls
Eukaryota 100% carry a bacterial family one rank down — so they cannot be
combined, and genus is the finest of them. `assess_vpf_class.py` recomputes that
and the other grounds from the raw files and fails if any stops being true;
`make_vpf_class_coverage.py` reports the same coverage at three cuts as Table S3.

Two things this tool alone forces, both recorded because they are visible on the
figure. Its article enumerates no host-label list — it classifies against
whatever its reference database holds — so the "labels reported by the study"
bar is drawn empty rather than as a zero, which would claim it reports none.
And it is the reason the Algae row exists (entry 12): 615 of its 668 records.

The virus-taxonomy tables are not used at all. They have the same shape, and the
three commonest families in them are Myoviridae, Siphoviridae and Podoviridae,
which ICTV abolished in 2021: harmonizing them is a resolution of retired taxa,
not a renaming.

---

## 12. Algae, protists and oomycetes get two lineages of their own

They were pooled into "Unresolved eukaryote", which stated two wrong things at
once: they are resolved, usually to species or genus, and they are not unknown.
745 records — algae 668, protists 62, oomycetes 15 — from diatoms and kelps to
*Acanthamoeba*, *Leishmania* and *Phytophthora*, and including *Aureococcus*,
the brown-tide alga that is VPF-Class's second largest host.

Two named rows, each its own lineage band -- Algae in the green the pair started
with, protists and oomycetes in a purple 96 units from Fungi, its nearest
lineage, where the closest existing lineage pair sits at 90. Three rows was one
too many: protists and oomycetes are 62 and 15 records from the same two
instances, and would have been the two thinnest taxa on a figure whose thinnest
real taxon is Amphibia at 52. The merged row is named "Protists & oomycetes"
rather than letting "Protists" swallow the oomycetes, and Table S2 keeps every
entity apart regardless, which is what makes the merge cost nothing.

Read the two rows against each other with the counting unit in mind. Algae's 668
is 615 profiles from VPF-Class and 53 records from the other two instances, so
in the units every other column uses the algae are the *smaller* of the two
rows, not the larger, and the whole band is 130 records from two instances --
the size of Crustacea. They are kept apart anyway, because which of the two a
host belongs to is a real distinction and the figure marks VPF-Class's unit
where the reader meets it. What the split must not be read as is a difference in
weight of evidence. Algae briefly
sat in the Plants lineage as a cheaper compromise; adding the protists made that
untenable, since nothing here photosynthesises but the algae. These are none of
plants, fungi or animals, and bands that say so are more honest than any of the
six existing ones would have been. Algae carry a wave rather than a coral or a shell: those are animals, and this
figure already drew a tick by hand rather than let a spider stand for Ixodida.
Unicode has no seaweed, so the icon names what the row has in common -- water --
instead of naming the wrong organism.

Oomycetes are named rather than merged into fungi. They are stramenopiles, kin
to the brown algae one row above them, but were classified as fungi for a
century and are still studied as plant pathogens beside them — the name settles
it, the row keeps them apart.

Nothing is left under "Unresolved eukaryote". The last four records were one
instance's literal `unknown`, with the lineage `unclassified sequences`, and
they had reached a eukaryote category only through that extractor's
prokaryote/eukaryote split, which reads anything without Bacteria or Archaea in
its lineage as eukaryotic. That is "not shown to be a prokaryote", not "shown to
be a eukaryote", and the name claimed more than the file says. They are recorded
as host unknown, with the other tools' orphan and blank rows.

The category stays in the vocabulary. It is a real thing for a label to be --
known to be a eukaryote and nothing more -- and the next tool may well produce
one; it is simply unoccupied once everything that was not that has been moved
out of it.

---

## 13. Two labels that were never unresolved, and one that names a virus

Host Taxon Predictor's `Mosquito-Unknown` and `unidentified mosquitos` sat in
"Unresolved eukaryote" while the same tool's own `mosquito` rows went to
Culicidae. The labels were never unresolved: NCBI returns "unclassified
sequences" for these two spellings and Culicoidea for the third, so what failed
was the lineage lookup, not the label. Curated as the tool's other mosquito rows
are.

`Acanthamoeba polyphaga mimivirus` is worse: the host field names a VIRUS, and
the tool's own lineage for that row ends "Mimiviridae, Mimivirus". It had
resolved to the host *Acanthamoeba polyphaga* — because the infraspecific
collapse truncates a three-word capitalised name to its first two words, and a
virus name is not an infraspecific taxon. So a host the file never stated was
being drawn. The label is recorded as host unknown, and the collapse now refuses
any name ending in a virus word, so the next such label cannot become a host by
truncation.

---

## 14. What a study reports and what it released are both recorded

They disagree for eleven of sixteen tools, sometimes wildly: DeePaC-vir states
two host labels and its released tables populate 46 categories; MENB states
eleven where its own composition figure resolves three. Neither number is wrong
and neither is corrected — the gap is the subject of the figure. Which of the
278 reported labels come from a paper and which from a file is recorded per row
in `reported_labels_provenance.csv`.
