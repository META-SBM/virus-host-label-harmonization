# raw_sources/ — one clean folder per tool, exactly the file(s) actually used

Created because the project's raw source files were previously scattered across
two inconsistent locations (`manual_downloads/<Tool>/` — a hand-curated subset,
and `public_sources/<tool>/` — full repo/Zenodo clones), and the recompute
script that reads them (`per_tool_counts_from_scratch_v2/recompute_all.py`) had
dead, session-specific absolute paths (`/sessions/.../mnt/Documents`) that no
longer exist anywhere on this machine — so the pipeline's numbers, while
correct, were not actually reproducible from raw data without knowing which of
two folders (and which of several similarly-named files inside them) to read.

**Selection logic — one rule, no exceptions:** each tool's folder contains
exactly the file(s) named in that tool's `DATASET_SCOPE` entry
(`scripts/categories.py`) and in the "Recomputed from" line of its
`per_tool_counts_from_scratch_v2/counts_per_tool_v2/*_counts.csv`. Nothing
else. In particular, rejected alternative files (train-only splits for the 5
tools where the full dataset is used instead, SPHAK's fuller
"including_out_of_sample" file, GIVAL's incompatible 2-category vBERT split,
etc.) are deliberately NOT copied here — that reasoning lives in
`DATASET_SCOPE`'s notes, not as dead weight in this folder. `original_reported_labels.xlsx` — the one file this project already
documents as unverified (see Scope note on 00_README of the xlsx workbook) —
is also deliberately not copied here.

| Tool | File(s) | Original location |
|---|---|---|
| DeepHoF | `41598_2021_96903_MOESM5_ESM.xlsx` (train_genome_info + test_genome_info sheets) | manual_downloads/DeepHoF/ |
| RNAVirHost | `virus_label(1).csv` | manual_downloads/RNAVirHost/ |
| Host_Taxon_Predictor | `all_viruses_with_desired_attributes.dump` | manual_downloads/HostTaxonPredictor/supplementary_materials/datasets/ |
| EvoMIL | `journal.pcbi.1012597.s002_converted.xlsx` (sheet Table_S2) | per_tool_counts_from_scratch_v2/ — already converted via LibreOffice from the original strict-OOXML file, which no longer exists separately anywhere in this project |
| VIDHOP | `small_paper_version_{Influ,Rabies,Rota}_strict/Y_{train,val,test}.csv` (9 files; only the label files, not the multi-GB sequence/feature data) | manual_downloads/VIDHOP/train_data/ |
| HostNet_Flavivirus | `flavivirus.csv` | manual_downloads/HostNet/ |
| HostNet (Rabies, VIPHOD) | **no separate copy** — reads the same `VIDHOP/small_paper_version_Rabies_strict/Y_{train,test}.csv` as VIDHOP itself (val excluded; see DATASET_SCOPE note). This is not a mistake: HostNet's own Rabies/VIPHOD benchmark IS VIDHOP's published Rabies_strict split. |
| MENB | `msaf127_supplementary_data.pdf` (Supplementary Figure 1A, hand-transcribed — not machine-parseable, see recompute_all.py's `_menb_fig1` dict) | manual_downloads/MENB/ |
| ViralHostPredictor | `BabayanEtAl_VirusData.csv` | manual_downloads/ViralHostPredictor/ |
| Zoonotic_rank | `AllInternalData_Checked.csv` | manual_downloads/ZoonoticRankModel/ |
| HostClassifier | `virus-host-datasets_v4.5.0.csv` (58,058 rows, has `standardized_host`) | public_sources/hostclassifier/host-virus-dataset/.../versioned_datasets/ — NOT manual_downloads/HostClassifier/train.parquet, which is a real but deliberately-unused train-only split (89%, see DATASET_SCOPE) |
| VirHostPRED | `reps70.fasta` (positive class) + `random_dataset_1.fasta` (negative class) | manual_downloads/VirHostPRED/ — corrected this session from a wrong "no_dataset_file" classification; these were sitting there all along |
| SPHAK | `animal_train.csv` + `plant_train.csv` (13,570 records, train_only BY DESIGN) | public_sources/sphak/SPHAK/data/{animal_data,plant_data}/ — NOT the fuller `*_including_out_of_sample.csv` (16,067 records), which exists in the same repo but isn't what SPHAK's own README calls its dataset (see DATASET_SCOPE note) |
| UniVH | `dataset.csv` (81,874 rows, has its own unused `dataset` train/val/test column) | manual_downloads/UniVH/ |
| GIVAL | `df_AIV_before_sample.csv` (121,753 rows) | manual_downloads/GIVAL/ — NOT the tool's own vBERT train/test split, which collapses host labels to Human/Avian only (see DATASET_SCOPE note) |

**Every entry above is traceable to a specific, dated finding this session** —
see the `hostclassifier_standardized_host_rebuild.md` project memory for the
full audit trail (which repos were checked, what was ruled out and why,
including 2 mistakes caught and corrected mid-session: HostNet Flavivirus's
split was initially missed by checking only the zip in manual_downloads, and
VirHostPRED was wrongly marked as having no dataset file at all).

**Total size:** ~389 MB (dominated by HostTaxonPredictor's 94 MB pickle,
HostNet's 126 MB CSV, and GIVAL's 77 MB CSV — everything else is under 30 MB).

## What reads this folder

`per_tool_counts_from_scratch_v2/extractors/` has one standalone script per
tool (`extract_01_deephof.py` ... `extract_15_gival.py`), each reading only
its own subfolder above and writing its own
`counts_per_tool_v2/<NN>_<Tool>_counts.csv`. Every extractor is independently
runnable for debugging one tool (`python3 extractors/extract_11_hostclassifier.py`).
`recompute_all.py` is the thin orchestrator that runs all 15 in order and
assembles `00_manifest.csv`. `verify_against_committed.py` diffs the output
row-by-row against a backup snapshot — see its docstring for usage. As of the
last run, all 15/15 extractors reproduce the committed `counts_per_tool_v2/`
files byte-for-byte from nothing but the files in this folder.

---

## Where the "Original location" column points

`manual_downloads/` and `public_sources/` were the two pre-consolidation staging
directories this folder replaced. **Neither exists any more.** The column above
is kept as the historical record of which staging copy each file was taken from,
not as a path anything can follow today.

Provenance that a reader can act on lives in `MANIFEST.csv`, which since
2026-09-08 carries four provenance columns per file:

| column | meaning |
|---|---|
| `sha256` | the file the committed numbers were computed from. Complete for all 34 |
| `doi` | article or repository DOI, where one is recorded. 9 of 34 |
| `source_url` | a resolvable download or supplementary-material URL. 15 of 34 |
| `retrieved` | retrieval date, where it was recorded at the time. 10 of 34 |
| `local_origin` | the staging path the file came from, per the table above |

`MISSING` in any of these is a statement, not a blank: the provenance was looked
for on 2026-09-08 and is not recorded anywhere in this repository. It is not
reconstructed by guessing, and a retrieval date is never back-filled. Closing
those gaps needs the download to be repeated and dated, which no one has done.

Nothing here redistributes publisher-copyright material: the DOIs and URLs point
at the publishers' own pages, and the article PDFs stay out of git.
