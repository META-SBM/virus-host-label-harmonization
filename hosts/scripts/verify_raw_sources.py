# -*- coding: utf-8 -*-
"""Checksum manifest for raw_sources/: build it, or verify against it.

    python3 verify_raw_sources.py --write    # regenerate the manifest
    python3 verify_raw_sources.py            # verify, non-zero exit on mismatch
"""
import argparse
import csv
import hashlib
import os
import sys

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
RAW = os.path.join(ROOT, "raw_sources")
MANIFEST = os.path.join(ROOT, "sources", "MANIFEST.csv")  # tracked; raw_sources/ is not
COLUMNS = ["tool", "path", "bytes", "sha256", "source_url", "retrieved", "doi", "local_origin",
           "url_verified", "url_confirmed"]
# Fields a human fills in and a regeneration must not wipe. MISSING is a real
# value here: it says the provenance was looked for and not found, which is not
# the same as an empty cell that nobody has looked at yet.
HAND_ENTERED = ("source_url", "retrieved", "doi", "local_origin",
                "url_verified", "url_confirmed")
SKIP = ("MANIFEST.csv", "00_README.md")


def sha256(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk():
    """Every file under raw_sources/, except the manifest and the README."""
    # followlinks: raw_sources/ is 470 MB of third-party data and is not in git,
    # so a clone that has it at all is likely to have it symlinked in from
    # wherever it was downloaded
    for dirpath, _dirs, files in os.walk(RAW, followlinks=True):
        for fn in sorted(files):
            if fn in SKIP or fn.startswith("."):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, RAW)
            yield rel.split(os.sep)[0], rel, full


def load_manifest() -> dict:
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return {r["path"]: r for r in csv.DictReader(fh)}


def write_manifest(previous: dict) -> int:
    """Rehash everything on disk. The hand-entered fields survive."""
    rows = []
    for tool, rel, full in walk():
        keep = previous.get(rel, {})
        rows.append({
            "tool": tool,
            "path": rel,
            "bytes": os.path.getsize(full),
            "sha256": sha256(full),
            **{f: keep.get(f, "") for f in HAND_ENTERED},
        })
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    n_url = sum(1 for r in rows if r["source_url"] and r["source_url"] != "MISSING")
    print(f"wrote {MANIFEST}: {len(rows)} files, "
          f"{sum(r['bytes'] for r in rows) / 1e6:.0f} MB")
    if n_url < len(rows):
        print(f"  {len(rows) - n_url} of {len(rows)} rows still have no source_url "
              f"-- see this file's docstring")
    return 0


def verify(previous: dict) -> int:
    """The files a clone has must be the files the numbers came from."""
    on_disk = {rel: full for _t, rel, full in walk()}
    missing = sorted(set(previous) - set(on_disk))
    extra = sorted(set(on_disk) - set(previous))
    changed = []
    for rel, row in sorted(previous.items()):
        if rel not in on_disk:
            continue
        if os.path.getsize(on_disk[rel]) != int(row["bytes"]) or sha256(on_disk[rel]) != row["sha256"]:
            changed.append(rel)

    for label, items in (("missing", missing), ("not in manifest", extra),
                         ("CHECKSUM MISMATCH", changed)):
        for i in items:
            print(f"  {label}: {i}")
    bad = missing or extra or changed
    print(f"\n{len(previous)} file(s) in manifest; "
          + ("VERIFIED — every file present and unchanged" if not bad else "FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="regenerate the manifest, preserving any source_url/retrieved already filled in")
    args = ap.parse_args()

    if not os.path.isdir(RAW):
        sys.exit(f"raw_sources/ not found at {RAW} -- nothing to verify")

    previous = load_manifest()
    if args.write:
        return write_manifest(previous)
    if not previous:
        sys.exit(f"no manifest at {MANIFEST} -- run with --write first")
    return verify(previous)


if __name__ == "__main__":
    sys.exit(main())
