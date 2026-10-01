# -*- coding: utf-8 -*-
"""Are the committed per-tool counts reproducible from the raw files?

Hashes every counts CSV, re-runs recompute_all.py, hashes again, and reports any
file whose bytes changed. If nothing changed, the numbers this project publishes
are exactly what the raw sources produce today.

The previous version compared against a *manual backup snapshot* that you had to
remember to create before running the recompute -- and when the snapshot was
absent it printed a notice and exited 0, so a check that had never run looked
like a check that had passed. This version needs no ritual and fails loudly.

    python3 verify_against_committed.py

Also reports, separately and for information only, which counts files differ
from git HEAD: that is uncommitted work, not a reproducibility failure.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COUNTS = os.path.join(HERE, "counts_per_tool_v2")
ROOT = os.path.dirname(HERE)


def digests() -> dict:
    out = {}
    for fn in sorted(os.listdir(COUNTS)):
        if fn.endswith(".csv"):
            with open(os.path.join(COUNTS, fn), "rb") as fh:
                out[fn] = hashlib.sha256(fh.read()).hexdigest()
    return out


def recompute() -> None:
    """Rewrite every counts file from the raw sources. Exits if it cannot."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "recompute_all.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        sys.exit("recompute_all.py FAILED -- the raw sources no longer produce these numbers")


def report_uncommitted() -> None:
    """Uncommitted-but-intentional edits are a different thing; say so
    separately."""
    g = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--",
                        os.path.relpath(COUNTS, ROOT)], capture_output=True, text=True)
    dirty = [l.split(maxsplit=1)[-1] for l in g.stdout.splitlines() if l.strip()]
    if dirty:
        print(f"\nfor information: {len(dirty)} counts file(s) differ from git HEAD "
              f"(uncommitted work, not a reproducibility failure):")
        for d in dirty:
            print("   ", d)


def main() -> int:
    if not os.path.isdir(COUNTS):
        sys.exit(f"not found: {COUNTS}")

    before = digests()
    if not before:
        sys.exit(f"no counts CSVs in {COUNTS}")
    print(f"hashed {len(before)} counts file(s); re-running recompute_all.py ...\n")

    recompute()
    after = digests()
    changed = sorted(f for f in before if before[f] != after.get(f))
    vanished = sorted(set(before) - set(after))
    appeared = sorted(set(after) - set(before))

    for f in changed:
        print(f"  CHANGED   {f}")
    for f in vanished:
        print(f"  VANISHED  {f}")
    for f in appeared:
        print(f"  NEW       {f}")

    ok = not (changed or vanished or appeared)
    print(("\nVERIFIED — all %d counts files reproduce byte-for-byte from raw_sources/"
           % len(before)) if ok else "\nFAILED — the recompute does not reproduce the counts on disk")

    report_uncommitted()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
