# Table S4. Host labels as released, before harmonization

`table_S4_labels_as_released.csv`, 6,838 rows — one per tool and label, spelled as the released file spells it. Nothing in this table has been mapped, merged, renamed or resolved.

It is the input to everything else here. Those 6,838 labels become 1,513 host entities in Table S2 and 50 categories on the figure, and reading the three in order shows every editorial act in between: `human`, `Human`, `Homo sapiens` and `Homo sapiens (taxid 9606, positive class)` are four rows in this table and one row in the next.

**Status** says whether a label was carried into the analysis or excluded, and the note says why — non-eukaryotic classes, negative-class placeholders and labels that state no host are excluded, and each one says which it is. **Source file and field** names where the label was read, so any row can be checked against the release it came from.

| Tool | Labels | of which excluded | Records |
|---|---:|---:|---:|
| DeePaC-vir | 2,284 | 559 | 9,496 |
| DeepHoF | 6 | 1 | 66,949 |
| EvoMIL | 18 | 0 | 3,869 |
| GIVAL | 27 | 1 | 121,753 |
| Host Taxon Predictor | 1,218 | 1 | 5,282 |
| HostNet (Flavivirus) | 3 | 0 | 9,626 |
| HostNet (Rabies, VIPHOD) | 17 | 0 | 11,685 |
| MENB | 3 | 0 | 3,600 |
| MosViR | 2 | 0 | 27,002 |
| RNAVirHost | 2,497 | 1 | 17,107 |
| SPHAK | 631 | 0 | 13,570 |
| UniVH | 15 | 0 | 736 |
| VIDHOP | 51 | 0 | 263,962 |
| VPF-Class | 13 | 1 | 12,253 |
| VirHostPRED | 2 | 0 | 4,254 |
| ViralHostPredictor | 35 | 2 | 695 |
| Zoonotic rank | 16 | 2 | 1,258 |
| **Total** | **6,838** | **568** | **573,097** |
