# -*- coding: utf-8 -*-
"""The exactly-duplicated rows inside SPHAK's released training files.

    python3 build_sphak_duplicate_records.py

Writes scripts/sphak_duplicate_records.csv, one row per duplicated accession.

These records are NOT removed. SPHAK's own reported dataset total counts them,
and this project's rule is to represent each tool by what its study reports, so
removing them here would put our figure out of step with the publication it
describes. The duplication is reported instead, the same way VirHostPRED's
positive-class composition is: as a property of the released file, not as
something silently corrected.

What makes them different from the multi-host records of DeepHoF and RNAVirHost:
there a single record legitimately carries several hosts, so one virus lands in
several rows by design. Here every field of the two rows is identical, including
the sequence, so the second row adds no information at all.
"""
import collections
import csv
import os

SC = os.path.dirname(os.path.abspath(__file__))
RS = os.path.join(os.path.dirname(SC), "raw_sources", "SPHAK")
OUT = os.path.join(SC, "sphak_duplicate_records.csv")
FILES = ("animal_train.csv", "plant_train.csv")

COLUMNS = ["source_file", "accession", "occurrences", "extra_rows", "host",
           "virus_species", "virus_family", "identical_in_every_field"]


def load_data() -> dict:
    out = {}
    for fn in FILES:
        path = os.path.join(RS, fn)
        if not os.path.exists(path):
            raise SystemExit(f"missing raw file {path} -- this script needs raw_sources/")
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            out[fn] = list(csv.DictReader(fh))
    return out


def process_data(data: dict) -> list:
    """One row per accession that appears more than once, with the check that
    decides what kind of duplication it is."""
    rows = []
    for fn, records in data.items():
        by_accession = collections.defaultdict(list)
        for r in records:
            by_accession[r["Accession"]].append(r)
        for accession, group in by_accession.items():
            if len(group) == 1:
                continue
            fingerprints = {tuple(sorted(g.items())) for g in group}
            rows.append({
                "source_file": fn,
                "accession": accession,
                "occurrences": len(group),
                "extra_rows": len(group) - 1,
                "host": group[0]["Host"],
                "virus_species": group[0]["Species"],
                "virus_family": group[0]["Family"],
                "identical_in_every_field": "yes" if len(fingerprints) == 1 else "no",
            })
    rows.sort(key=lambda r: (r["source_file"], r["accession"]))
    return rows


def save(rows: list) -> None:
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    extra = sum(r["extra_rows"] for r in rows)
    identical = sum(1 for r in rows if r["identical_in_every_field"] == "yes")
    print("saved ->", OUT)
    print(f"   {len(rows)} duplicated accessions, {extra} redundant rows, "
          f"{identical} identical in every field")
    for fn in FILES:
        n = sum(r["extra_rows"] for r in rows if r["source_file"] == fn)
        print(f"   {fn:<20}{n:>6} redundant rows")
    top = collections.Counter()
    for r in rows:
        top[r["host"]] += r["extra_rows"]
    print("   most affected hosts:", ", ".join(f"{h} +{n}" for h, n in top.most_common(4)))


if __name__ == "__main__":
    save(process_data(load_data()))
