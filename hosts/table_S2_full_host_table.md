# Table S2. Full host table — every entity, no retention threshold

`table_S2_full_host_table.csv`, 1,315 rows, one per host entity, 545,898 records across 17 dataset instances.

The figure draws 50 categories because a species must be named by at least 6 of the 17 dataset instances to hold a row of its own. This table removes that threshold: every host entity appears at the resolution its own source published it at, with the category the figure placed it in and the rule that put it there. It is the audit trail for the collapse, and the answer to what any one row of the figure is made of.

Columns: identity and rank; lineage; the figure category and why; whether the entity carries vector-axis records; how many dataset instances name it; total records; then one column per dataset instance. HostNet's two instances are kept apart here, where the figure sums them.

The **Why** column distinguishes the four routes into a category. The first three keep an entity as a row of its own — the retention threshold, or the explicit vector mapping, or its genus-level fallback. The fourth and commonest, *grouped under the conventional taxon*, covers every entity that did not clear the bar, whether it is a species or a term that names no species; those are the rows the figure compresses.

## What each figure category is made of

| Figure category | Entities | Records |
|---|---:|---:|
| Homo sapiens | 1 | 240,239 |
| Aves | 98 | 67,182 |
| Sus scrofa | 1 | 62,873 |
| Unresolved vertebrates | 1 | 34,864 |
| Gallus gallus | 1 | 28,662 |
| Anas platyrhynchos | 1 | 25,343 |
| Plantae | 445 | 18,115 |
| Culicidae | 44 | 12,433 |
| Canis lupus | 1 | 11,648 |
| Other invertebrates | 28 | 8,477 |
| Bos taurus | 1 | 6,582 |
| Equus caballus | 1 | 3,019 |
| Insects | 151 | 2,499 |
| Meleagris gallopavo | 1 | 2,240 |
| Non-human (undifferentiated) | 1 | 2,127 |
| Carnivora | 24 | 1,597 |
| Fungi | 103 | 1,527 |
| Chiroptera | 64 | 1,518 |
| Vulpes vulpes | 1 | 1,500 |
| Mephitis mephitis | 1 | 1,385 |
| Procyon lotor | 1 | 1,146 |
| Rodentia | 66 | 1,116 |
| Eptesicus fuscus | 1 | 952 |
| Felis catus | 1 | 917 |
| Other mammals | 100 | 914 |
| Fish | 40 | 698 |
| Algae | 4 | 668 |
| Ixodida | 19 | 635 |
| Artiodactyla | 17 | 632 |
| Tadarida brasiliensis | 1 | 519 |
| Non-human primates | 29 | 454 |
| Desmodus rotundus | 1 | 360 |
| Capra hircus | 1 | 344 |
| Mus musculus | 1 | 339 |
| Arachnida | 9 | 289 |
| Reptilia | 21 | 271 |
| Nyctereutes procyonoides | 1 | 248 |
| Struthio camelus | 1 | 240 |
| Chlorocebus aethiops | 1 | 198 |
| Macaca mulatta | 1 | 191 |
| Rattus norvegicus | 1 | 163 |
| Ovis aries | 1 | 142 |
| Pan troglodytes | 1 | 132 |
| Crustacea | 9 | 118 |
| Unknown host | 1 | 84 |
| Protists & oomycetes | 9 | 77 |
| Mesocricetus auratus | 1 | 72 |
| Mustela putorius | 1 | 56 |
| Humans + non-human primates | 1 | 55 |
| Amphibia | 5 | 38 |

| **Total** | **1,315** | **545,898** |
