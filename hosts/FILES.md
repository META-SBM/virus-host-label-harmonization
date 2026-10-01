# Every file in this repository, and why it is here

The tracked files, each listed below. Every `.csv` table also has an `.xlsx`
copy with the same name, written by `scripts/export_tables_xlsx.py`; those copies
are not listed one by one. Nothing here serves any purpose other than producing
`host_general_scheme_R.png` and the text that describes it.

---

## The deliverable

| file | what it is |
|---|---|
| `host_general_scheme_R.png` | **the figure**, 7646 × 7040 px. 58 drawn rows (50 analytical categories plus 8 taxon headers) by 16 tool columns |
| `manuscript_host_general_scheme.md` | the complete manuscript text for it: caption, Methods 3.3, Results |
| `supplementary_methods_host_harmonization.md` | Supplementary Methods, seven sections: the observation breakdown by counting unit, both confidence weightings, resolution below the display threshold, the threshold sweep, the VirHostPRED and SPHAK findings, the NCBI name checks, the curation rules |
| `figure_captions.md` | the caption on its own, as assembled into the file above |
| `methods_3_3_host_label_harmonization.md` | the Methods on its own |
| `results_section.md` | the Results on its own |

The last three are the sources the consolidated file is assembled from, by
`scripts/build_manuscript.py`. Editing one of them and reassembling is how the
manuscript text is changed. The consolidated file is generated output and is not
edited directly: it used to be, and it drifted from its sources, which is why the
assembly is now a script and an audit stage.

## Supplementary tables

| file | rows | what |
|---|---:|---|
| `table_S1_data_provenance.csv` / `.md` | 17 | per tool: source file and field, dataset scope, counting unit, categories populated |
| `table_S2_full_host_table.csv` / `.md` | 1,513 | every host entity before the display threshold, with the rule that placed it |
| `table_S3_vpf_class_profile_coverage.csv` / `.md` | — | VPF-Class coverage at three membership cuts, counted in profiles |
| `table_S4_labels_as_released.csv` / `.md` | 8,076 | every label exactly as its tool released it, before any harmonization |

## Project documentation

| file | what |
|---|---|
| `README.md` | how to reproduce the figure, the chain, how the numbers are kept honest |
| `FILES.md` | this file |
| `DECISIONS.md` | the editorial choices that data cannot settle, with what was rejected and why |
| `HOST_WORK_PLAN.md` | what was audited, what was settled, what remains open |
| `HOST_METHODS_CLARIFICATIONS.md` | the 2026-09-08 methodological audit: every numeric claim, its source and its formula |
| `HOST_METHODS_RESOLUTION.md` | what was done about that audit, in three revisions |
| `requirements.txt` | the Python environment, pinned |
| `environment-R.yml` | the R environment, pinned, and the traps it documents |
| `.gitignore` | keeps the raw data and the article PDFs out of git |

---

## Stage 1 — raw files to counts

`per_tool_counts_from_scratch_v2/`

| file | what |
|---|---|
| `recompute_all.py` | runs all 18 extractors |
| `verify_against_committed.py` | hashes the counts, re-runs the recompute, hashes again. Any drift fails |
| `extractors/common.py` | the shared CSV writer, and the path to `raw_sources/` |
| `extractors/extract_01_deephof.py` … `extract_18_vpf_class.py` | **18 extractors, one per dataset instance.** Each reads only its own tool's directory and writes one CSV. None knows the others exist, with two deliberate exceptions: `extract_07` reads VIDHOP's Rabies files because HostNet's benchmark *is* that split, and `extract_18` borrows the NCBI lineage embedded in Host Taxon Predictor's dump to decide which VPF-Class host genera are eukaryotic |
| `counts_per_tool_v2/00_manifest.csv` | which extractor produced which counts file |
| `counts_per_tool_v2/01_…_counts.csv` … `18_…_counts.csv` | the labels exactly as released, per instance. This is Table S4's input |

## Stage 2 — the harmonization

`scripts/`

**Registries, imported by nearly everything**

| file | what |
|---|---|
| `categories.py` | the 27-category vocabulary, the 8 lineages, the palettes, and `DATASET_SCOPE`: what each of the 18 instances is represented by and why. Data only, imports nothing from this project |
| `icons.py` | the lineage icons: emoji rendered to flat silhouettes, plus the kelp and the tick, which had to be drawn because Unicode has neither |

**Curation — the only place a human decides**

| file | rows | what |
|---|---:|---|
| `label_categories.csv` | 8,076 | label to category, by hand |
| `label_enrichment.csv` | 8,076 | status, rank, counting unit, and the note saying why |
| `tool_metadata.csv` | 17 | what comes from the article rather than the files: prediction target, dataset size, counting unit, molecule type |

**The chain**

| file | writes | what it does |
|---|---|---|
| `build_master_labels.py` | `master_labels.csv` (8,076) | joins the counts to the two curation tables, and fails loudly if either fails to cover the other |
| `build_species_matrix.py` | `species_matrix.csv` (4,311), `_wide.csv` (1,513 entities), `_label_trace.csv`, `_vector_fallback.csv` | labels to taxa. Synonyms collapsed, infraspecific names folded onto their binomial, vector-axis records routed |
| `build_general_scheme.py` | `general_scheme_matrix.csv` (349 cells), `_wide.csv` (50 categories), `_row_fate.csv`, `_unnamed_detail.csv` | entities to the 50 display categories, by the four-rule routing protocol. `_row_fate` records which rule placed each entity |
| `build_comparison_metrics.py` | `comparison_metrics.csv` | per-tool comparison metrics. Kept because the VirHostPRED flagged-record count is cross-checked against its adjusted human-dominance fraction |
| `run_all.py` | — | runs the four above plus the figure and the Excel copies, in the one order that is valid |
| `export_tables_xlsx.py` | an `.xlsx` next to every table `.csv` | Excel copies for reading; the CSVs stay the files every script reads and verifies |

## Stage 3 — the figure

| file | what |
|---|---|
| `make_general_scheme_heatmap.py` | builds the row order, the cell matrix and the badge masks, and draws a matplotlib rendering as a cross-check. **Its `load_data` and `process_data` are the single source of the figure's data**, imported by the exporter |
| `export_general_scheme_for_r.py` | writes `r_general_scheme/` from that same data, so the two renderings cannot disagree about a number |
| `make_general_scheme_heatmap.R` | the publication rendering, ComplexHeatmap. **Does no harmonization.** It is handed the matrix, the row order, the flags and the palette, and draws them |
| `host_general_scheme.png` | the matplotlib cross-check. Not a publication figure |

`scripts/r_general_scheme/` — what the R script is handed, all generated:

| file | what |
|---|---|
| `matrix.csv` | the cells, 58 rows by 17 tools |
| `row_meta.csv` | display order, name, gloss, italics, lineage, indent, header flag, parent |
| `col_meta.csv` | tool order, prediction target, record and molecule type, bar values |
| `cell_flags.csv` | the (row, tool) pairs carrying the "V" vector badge |
| `palette.csv` | every colour and label the R figure uses |
| `icons/*.png` | 17 icons: 8 lineage, 9 taxon header |

## Stage 4 — verification

| file | what it checks |
|---|---|
| `audit_all.py` | the orchestrator: 15 stages, one verdict, about a minute. Without the raw files the four stages that read them are skipped |
| `verify_raw_sources.py` | every raw file matches the SHA-256 the numbers were computed from |
| `verify_general_scheme_figure.py` | 14 checks. Every drawn cell re-derives from `species_matrix.csv` and the routing table, the routing conserves observations, the badges match their sources, the row structure holds |
| `verify_reported_numbers.py` | 124 numerical claims recomputed from the committed tables, plus a scan of the manuscript files for values left over from earlier builds and for references to figures this work no longer carries |
| `build_manuscript.py` | assembles `manuscript_host_general_scheme.md` from the caption, Methods and Results files, so the consolidated text cannot say something its sources do not |
| `sweep_threshold.py` | rebuilds the scheme at every retention threshold from 1 to 8 into `threshold_sweep.csv`, and asserts the record total is identical at all eight, which is what makes them comparable as displays of one dataset |

## Stage 5 — tables and evidence

| file | writes | what |
|---|---|---|
| `make_provenance_table.py` | Table S1 | per-tool provenance, taken from the figure's own columns |
| `make_full_host_table.py` | Table S2 | every host entity, no display threshold. Asserts each entity occupies exactly one row |
| `make_before_harmonization_table.py` | Table S4 | every label as released |
| `make_vpf_class_coverage.py` | Table S3 | VPF-Class coverage in profiles |
| `assess_vpf_class.py` | `vpf_class_assessment.csv` | the six grounds for VPF-Class carrying no ordinary record count, re-derived from its files. Fails if any stops holding |
| `build_host_harmonization_provenance.py` | `host_harmonization_provenance.csv` (4,477) | one row per released label and resolved entity, naming which curation rule fired. Zero rows are unattributed |
| `build_sphak_duplicate_records.py` | `sphak_duplicate_records.csv` (773) | the exactly duplicated rows in SPHAK's released training file, kept and reported rather than repaired |

**Evidence files, written once and committed**

| file | rows | what |
|---|---:|---|
| `host_name_authority_checks.csv` | 33 | NCBI Taxonomy, accessed 2026-09-08: the 26 standalone species, 3 species named in the Results, and both sides of all 4 binomial synonym substitutions. All CONFIRMED |
| `virhostpred_flagged_records.csv` | 235 | per accession: the two bacteriophage source organisms in VirHostPRED's human-infecting class, with taxid, lineage, genome and evidence URL |
| `reported_labels.csv` | 278 | what each article states it distinguishes |
| `reported_labels_provenance.csv` | 278 | what each of those 278 actually rests on. Only 38 carry a pointer into a paper; the Results uses three of these numbers and the VIDHOP one is cross-checked against our own recompute |

## Raw sources

| file | what |
|---|---|
| `sources/MANIFEST.csv` | 34 files: SHA-256 for all, a resolvable URL for all, a DOI for 25, a retrieval date for 10, and how the URL was verified for 19 |
| `sources/00_README.md` | where each file came from, and what the staging paths in the table mean |

**The raw files themselves are not in git** — about 470 MB of third-party data;
`raw_sources/` is ignored as a whole, and only the two files above describe it.
A clone needs them placed under `raw_sources/<Tool>/` at exactly the paths below,
or symlinked there. `verify_raw_sources.py` follows symlinks deliberately, and
fails if any file is missing, extra, or does not match its checksum. Without
them, `audit_all.py` skips the four stages that read them and builds the figure
and every table from the committed per-tool counts.

```
raw_sources/                       34 файла, ~470 МБ, вне git
├── DeePaC_vir/                 2 файл,  846K
│   ├── VHDB_1_folds_all_nhuman.rds                           508K
│   └── VHDB_1_folds_human.rds                                338K
├── DeepHoF/                    1 файл,    8M
│   └── 41598_2021_96903_MOESM5_ESM.xlsx                        8M
├── EvoMIL/                     1 файл,    7K
│   └── journal.pcbi.1012597.s002_converted.xlsx                7K
├── GIVAL/                      1 файл,   77M
│   └── df_AIV_before_sample.csv                               77M
├── HostClassifier/             1 файл,    9M
│   └── virus-host-datasets_v4.5.0.csv                          9M
├── HostNet_Flavivirus/         1 файл,  126M
│   └── flavivirus.csv                                        126M
├── Host_Taxon_Predictor/       1 файл,   94M
│   └── all_viruses_with_desired_attributes.dump               94M
├── MENB/                       1 файл,    6M
│   └── msaf127_supplementary_data.pdf                          6M
├── MosViR/                     2 файл,    9M
│   ├── arboviruses_500bp.fasta.xz                              7M
│   └── mosquito_500.fasta.xz                                   2M
├── RNAVirHost/                 1 файл,    4M
│   └── virus_label(1).csv                                      4M
├── SPHAK/                      2 файл,    9M
│   ├── animal_train.csv                                        7M
│   └── plant_train.csv                                         1M
├── UniVH/                      1 файл,   28M
│   └── dataset.csv                                            28M
├── VIDHOP/                     9 файл,    5M
│   ├── small_paper_version_Influ_strict/Y_test.csv            16K
│   ├── small_paper_version_Influ_strict/Y_train.csv            4M
│   ├── small_paper_version_Influ_strict/Y_val.csv             16K
│   ├── small_paper_version_Rabies_strict/Y_test.csv            7K
│   ├── small_paper_version_Rabies_strict/Y_train.csv         219K
│   ├── small_paper_version_Rabies_strict/Y_val.csv             7K
│   ├── small_paper_version_Rota_strict/Y_test.csv              2K
│   ├── small_paper_version_Rota_strict/Y_train.csv           768K
│   └── small_paper_version_Rota_strict/Y_val.csv               2K
├── VPF_Class/                  6 файл,   78M
│   ├── 2019_VPF_BaltTax_REclassification_new.tsv               2M
│   ├── 2019_VPF_DomHost_REclassification_new.tsv               3M
│   ├── 2019_VPF_FamHost_REclassification_new.tsv              21M
│   ├── 2019_VPF_FamTax_REclassification_new.tsv                8M
│   ├── 2019_VPF_GenHost_REclassification_new.tsv              23M
│   └── 2019_VPF_GenTax_REclassification_new.tsv               20M
├── VirHostPRED/                2 файл,    2M
│   ├── random_dataset_1.fasta                                693K
│   └── reps70.fasta                                         1007K
├── ViralHostPredictor/         1 файл,   21M
│   └── BabayanEtAl_VirusData.csv                              21M
└── Zoonotic_rank/              1 файл,  106K
    └── AllInternalData_Checked.csv                           106K
```

One instance has no directory of its own. **HostNet (Rabies, VIPHOD)** reads
`VIDHOP/small_paper_version_Rabies_strict/Y_train.csv` and `Y_test.csv`, because
HostNet's own rabies benchmark *is* VIDHOP's published Rabies split. It takes
train and test only, where VIDHOP takes all three, and each matches its own
publication's reported total: 11,685 against 12,025.

---

## What is deliberately absent

Ten figures and everything that fed only them were left behind in the working
repository: the taxon and species heatmaps, the habitat scheme, the comparison,
concentration, distribution and top-category panels, the unnamed breakdowns, and
the 25-sheet workbook with the four builders that supplied it. Also absent:
`original_reported_labels.xlsx` and its builder, whose only live consumers were
two of those figures. That is 2,900 lines of code and 33 output files that this
figure never touches.
