# Results

*Key numerical summaries in this section are recomputed from the committed
tables by `scripts/verify_reported_numbers.py`. Revised 2026-09-09: the
cross-dataset paragraph no longer points at a figure that is no longer part of
this work.*

*Counting units differ between dataset instances (sequence records, virus taxa,
a deduplicated species pool, protein-family profiles). No statement below
aggregates observation counts across instances. Magnitudes are reported either
as counts of tools or dataset instances, as presence or absence, or as shares
within a single instance.*

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
