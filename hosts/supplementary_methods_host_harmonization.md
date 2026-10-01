# Supplementary Methods — host-label harmonization

*Companion to Methods 3.3. Every value here is recomputed from the committed
tables by `scripts/verify_reported_numbers.py`. Compiled 2026-09-08.*

---

## S1. Composition of the 603,953 total source observations

The figure is built from 18 dataset instances that do not count the same thing.
The sum below is used in one place only, as a checksum on the routing step: the
observations entering the step leave it unchanged. **It is not a corpus size,
and no share of it is quoted in Methods or Results.**

| counting unit | observations | what one unit is |
|---|---:|---|
| sequence record | 531,286 | one nucleotide or protein sequence |
| virus taxon | 69,936 | one virus species |
| deduplicated pool entry | 736 | one entry of a deduplicated species pool |
| protein-family profile | 1,995 | one profile, which is not a virus |
| **total** | **603,953** | |

A protein-family profile spans many viruses and a virus contributes many
profiles, so the last row is not convertible into any of the others. One
instance, VIDHOP, supplies 43.7% of the total on its own.

## S2. Mapping confidence, both weightings

| basis | high | medium | low | denominator |
|---|---:|---:|---:|---|
| **per label (used in Methods)** | **91.6%** | **8.1%** | **0.3%** | 7,508 label rows |
| per label, counts | 6,881 | 605 | 22 | |
| observation-weighted | 92.8% | 6.5% | 0.6% | 603,953 observations |

The observation-weighted row is reported for completeness and is not used to
support any claim. It pools counting units that are not interconvertible, and
VIDHOP alone contributes 43.7% of its denominator while being entirely high
confidence. Within a single counting-unit class the high-confidence share is
93.6% for sequence-counting instances, 86.7% for taxon-counting, 68.6% for the
deduplicated pool and 100% for profiles. Per instance it runs from 0% (MENB) to
100% (seven instances).

**The 22 low-confidence labels in full.** These are every label whose category
was fixed by something other than an explicit taxonomic name. Counts are that
label's observations in its own instance's counting unit.

| tool | label as released | records | placed in |
|---|---|---:|---|
| DeepHoF | `- (untagged)` | 9 | Unknown host |
| GIVAL | Primates (PRI), post-hoc CoV grouping | uncounted | Other/unresolved mammals |
| GIVAL | Chiroptera (CHI), post-hoc CoV grouping | uncounted | Other/unresolved mammals |
| GIVAL | Suiformes/Artiodactyla, post-hoc CoV grouping | uncounted | Other/unresolved mammals |
| HostClassifier | Other (species not recorded) | 635 | Unknown host |
| HostClassifier | Unknown | 254 | Unknown host |
| HostClassifier | blank (host not recorded) | 166 | Unknown host |
| HostClassifier | Avian (species not recorded) | 100 | Birds |
| HostClassifier | Mammal (species not recorded) | 85 | Other mammals |
| HostClassifier | Plant (species not recorded) | 81 | Plants |
| HostClassifier | cell culture | 56 | Unknown host |
| HostClassifier | Insect (species not recorded) | 47 | Insects |
| HostClassifier | Fish (species not recorded) | 18 | Fish |
| HostClassifier | unknown | 15 | Unknown host |
| HostClassifier | Cell Culture | 4 | Unknown host |
| HostClassifier | Cell culture | 3 | Unknown host |
| HostClassifier | Fungi (species not recorded) | 2 | Fungi |
| HostClassifier | Crustacean (species not recorded) | 2 | Other invertebrates |
| HostClassifier | Amphibian (species not recorded) | 1 | Amphibians |
| HostClassifier | Reptile (species not recorded) | 1 | Reptiles |
| UniVH | Animalia (other, no class match) | 231 | Other/unresolved invertebrates |
| VirHostPRED | NOT Homo sapiens (negative class) | 2,127 | Non-human (undifferentiated) |

Three of the 22 are the GIVAL groupings, which the article names but does not
count separately. They are recorded here and carry no observations, so they
enter no total. The 19 that do carry observations are dominated by two entries,
VirHostPRED's negative class and HostClassifier's unrecorded hosts, which is why
the low-confidence share is larger when weighted by observations than per label.

## S3. Resolution below the display threshold

A resolved species is drawn as its own entity only if at least two dataset
instances name it, or one instance gives it at least one hundred observations.

| quantity | value |
|---|---:|
| distinct species names recovered | 3,227 |
| drawn as their own entity | 1,461 |
| below the materiality bar, displayed inside a residual row | 1,766 |
| residual rows absorbing them | 19 |
| plant species names recovered / drawn as their own entity | 1,044 / 457 |
| fungal species names recovered / drawn as their own entity | 189 / 102 |

None of the 457 plant or 102 fungal entities clears the six-instance retention
threshold, so none appears as a standalone species row on the 50-category
figure. They are rows of the full host table, Table S2, only.

## S4. Retention-threshold sensitivity

`scripts/threshold_sweep.csv` rebuilds the scheme at every threshold from 1 to
8. The record total is identical at all eight, which is what makes them
comparable as displays of one dataset.

| threshold | share of instances | display categories | species clearing it | species drawn separately |
|---:|---:|---:|---:|---:|
| 1 | 6% | 1,469 | 1,461 | 1,445 |
| 4 | 22% | 311 | 293 | 287 |
| **5** | 28% | **110** | **90** | **86** |
| **6 (used)** | **33%** | **50** | **26** | **26** |
| **7** | 39% | **36** | **12** | **12** |
| 8 | 44% | 32 | 8 | 8 |

At threshold 5 the two species columns differ: 90 species clear the bar but 86
are drawn separately, because four of them (*Aedes aegypti*, *Amblyomma
americanum*, *Penaeus monodon*, *Penaeus vannamei*) are pooled by the vector and
crustacean rule, which outranks the threshold. At 6 and 7 the columns agree.

Raising the threshold to 7 would return every bat, rodent and non-human primate
to an order-level row. The sweep shows a monotone trade-off with no interior
optimum, so 6 is an editorial choice and is described as one.

## S5. VirHostPRED positive-class composition

The human-infecting class released with VirHostPRED (`reps70.fasta`, 2,127
protein records, 217 distinct source organisms) contains 235 records from two
organisms that are bacteriophages.

| organism label in the release | records | taxid | placement | genome |
|---|---:|---:|---|---|
| *Staphylococcus phage 6ec* | 141 | 1500386 | Caudoviricetes, *Sextaecvirus sextaec* | NC_024355.1 |
| *IAS virus* | 94 | 1450749 | Caudoviricetes, **Crassvirales**, *Paundivirus hollandii* | NC_049978.1 |

The link is by accession, not by name. The released FASTA headers carry RefSeq
protein accessions verbatim, for example `>YP_009981710.1 |hypothetical protein
H3301_gp001, partial [IAS virus]`. Each organism's records occupy one contiguous
accession block, YP_009042507.1 to YP_009042648.1 and YP_009981710.1 to
YP_009981806.1. Three accessions from each block, including both endpoints, were
queried individually against NCBI on 2026-09-08 and each returned the taxid and
genome above. The remaining 229 are recorded as inherited from the identical
organism label and the same contiguous block, stated per row in the
`verification` column of `scripts/virhostpred_flagged_records.csv`.

The records were retained to preserve the released class composition. They
remain inside the *Homo sapiens* by VirHostPRED cell. A human-dominance fraction
computed with and without them is reported separately in
`scripts/comparison_metrics.csv`. **No claim is made about the source study's
own quality control**, which this repository does not hold.

## S5b. SPHAK training-file duplication

`scripts/sphak_duplicate_records.csv`, one row per duplicated accession,
regenerated by `build_sphak_duplicate_records.py` from the released file.

773 accessions in `animal_train.csv` appear twice. All 773 pairs are identical
in every field, including `Sequence`, so the second row of each pair carries no
information. `plant_train.csv` has none. The redundancy is concentrated in
influenza: *Alphainfluenzavirus influenzae* accounts for 724 of the 773.

| host | rows in this instance | of which redundant |
|---|---:|---:|
| *Homo sapiens* | 5,480 | 235 |
| *Sus scrofa* | 740 | 138 |
| *Gallus gallus* | 922 | 126 |
| Anatidae | 361 | 55 |
| *Anas platyrhynchos* | 219 | 38 |

The instance contributes 13,570 observations, of which 773, or 5.7%, are these
redundant rows. Deduplicated it would contribute 12,797.

**They were kept.** SPHAK's own reported dataset total counts them, and this
project represents each instance by what its study reports. Removing them would
improve the count and break the correspondence with the publication, and the
correspondence is the only external check this project has on that column. The
duplication is therefore reported, not repaired.

**What the article says, and where the released files differ.** The article
(10.1038/s41598-026-52373-2, open access as PMC13365375) reports a curated
animal dataset of 10,965 protein sequences, which is exactly
`animal_data_excluding_out_of_sample.csv`, and after filtering an animal dataset
of 10,207 sequences, 8,165 for training and 2,042 for testing, against a plant
dataset of 4,346, being 3,476 for training and 870 for testing. `plant_train.csv`
matches its stated 3,476 exactly. `animal_train.csv` does not match its stated
8,165: the released file carries 10,094 rows and 9,321 distinct accessions. The
article accounts for the direction of that gap, since it states that
out-of-sample data were integrated into the reference database only after
evaluation was complete, and 74 of the 90 out-of-sample accessions are indeed
present in the released `animal_train.csv`. The released file therefore appears
to be the post-integration state rather than the one the reported evaluation
used. **The value 13,570 does not appear in the article.** An earlier note in
this repository claimed it matched the tool's reported total. It does not, and
that claim has been withdrawn. The released files are used as released and the
mismatch is reported here rather than reconciled by substituting a different
file.

**Why out-of-sample is not added.** 77 of its 100 records are already inside
the released training files this project counts, because the article states the
holdout was integrated back into the reference database once evaluation was
complete. Appending the file would count those 77 twice in order to gain 23
records, whose hosts are with one exception already rows of the matrix. The one
new name, *Melia dubia*, does not clear the materiality bar. SPHAK released no
validation split at all: none of the 93 files in its repository matches
val, valid, holdout or dev, and the article uses "validation" only for this
temporal holdout and for general corroboration of its design choices.

**What out-of-sample is for.** The article defines it as a temporal holdout:
sequences deposited in NCBI Virus between 31 December 2024 and 31 May 2025,
after the 30 December 2024 cutoff of the main collection, excluded from training
and from building the reference database so that evaluation ran on independent
data. It is small, 90 animal and 10 plant records. The animal set is dominated
by HIV (51 of 90) with coronaviruses next, and the plant set is 10 geminivirus
and related records on new hosts. The authors report that where predictions
failed, the cause was k-mers absent from the reference database.

The same file's `animal_test.csv` carries a further 42 duplicated accessions and
overlaps `animal_train.csv` by 412 accessions, which is why the two are not
combined: concatenating them would count 1,227 records twice. SPHAK's repository
also ships a separately curated animal set
(`animal_data_excluding_out_of_sample.csv`, 10,965 records, no duplicates at
all) that is neither a superset nor a subset of train and test, differing by
1,139 accessions in one direction and 713 in the other, and carrying 11.1%
influenza against the training file's 27.6%. There is therefore no single
"complete release" for this tool to fall back on.

## S6. Name checks against an authority

`scripts/host_name_authority_checks.csv`, NCBI Taxonomy, accessed 2026-09-08.
33 checks, all CONFIRMED.

- **26 standalone species rows.** Each returned by an exact `[Scientific Name]`
  search at rank species.
- **3 species named in the Results text**: *Solanum lycopersicum* (taxid 4081),
  *Zea mays* (4577), *Oryza sativa* (4530).
- **4 binomial synonym substitutions**, each confirmed from the target's own
  `OtherNames` block:

| substitution | NCBI record |
|---|---|
| *Canis familiaris* → *Canis lupus* | synonym of taxid 9615 *Canis lupus familiaris*, subspecies, parent taxid 9612 *Canis lupus* |
| *Capra aegagrus hircus* → *Capra hircus* | synonym of taxid 9925 *Capra hircus* |
| *Equus ferus caballus* → *Equus caballus* | synonym of taxid 9796 *Equus caballus* |
| *Litopenaeus vannamei* → *Penaeus vannamei* | synonym of taxid 6689 *Penaeus vannamei* |

The dog substitution is the only one that crosses a rank: NCBI places *Canis
familiaris* as a synonym of a subspecies whose parent is the species used here,
so the substitution is this project's infraspecific-to-binomial collapse and
agrees with that parentage.

**Scope of these checks.** 30 of the 1,513 host entities carry a taxid. The
other 1,483 were not checked against any authority, and the harmonization
provenance table records them as manual curation with taxid MISSING. Several
display labels used in the scheme are project constructs that no taxonomic
authority can confirm, for example "Simiiformes (monkey, family unresolved)" and
"Equus (hybrid: mule)". These are display categories, not taxonomic names.

## S7. Manual curation rules

Every rewrite in `scripts/host_harmonization_provenance.csv` is attributed to
one of these, and none is unattributed.

| rule | pairs | table in `build_species_matrix.py` |
|---|---:|---|
| below the materiality bar | 1,766 | threshold, not a table |
| identity, label already names the entity | 1,449 | — |
| category residual, label names no taxon | 892 | — |
| infraspecific collapse | 274 | `collapse_to_binomial()` |
| higher-rank mapping | 56 | `HIGHER`, 96 entries |
| synonym rewrite | 30 | `RESOLVE`, 49 entries |
| vector fallback | 5 | `VECTOR_FALLBACK_TARGET_OVERRIDE`, 5 entries |
| binomial synonym | 4 | `BINOMIAL_SYNONYM`, 4 entries |
| low-materiality fallback | 1 | `LOW_MATERIALITY_FALLBACK`, 1 entry |
