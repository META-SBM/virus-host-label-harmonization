# -*- coding: utf-8 -*-
"""Assembles manuscript_host_general_scheme.md from its three source files.

The manuscript used to be concatenated by hand, and it drifted: a fix that
removed a reference to a retired figure landed in the assembled file and never
made it back into results_section.md. Nothing detected that, because both files
were self-consistent and both parsed. Assembling mechanically means the three
sources are the only place text is edited, and the manuscript cannot say
something its parts do not.

Each source contributes its body: the H1 title and the italic editorial notes
under it are the file's own front matter and are replaced by the header below.
The counting-unit warning is the one piece of prose that moves -- it opens the
Results file so that file stands alone, and it is hoisted into the manuscript
header so it governs the caption and Methods as well.
"""
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript_host_general_scheme.md"

SECTIONS = [
    ("## Figure caption", "figure_captions.md"),
    ("## Methods — 3.3 Host-label harmonization", "methods_3_3_host_label_harmonization.md"),
    ("## Results", "results_section.md"),
]

HEADER = """# Host scheme figure — caption, Methods and Results

**Figure file:** `host_general_scheme_R.png`

*This is the complete manuscript text for that one figure: its caption, the
Methods subsection that produces it, and the Results drawn from it. Key
numerical summaries are recomputed from the committed tables by
`scripts/verify_reported_numbers.py`, which fails if any of them drifts.
Derivations, sensitivity analyses and per-record evidence are in
`supplementary_methods_host_harmonization.md`. Assembled {date} by
`scripts/build_manuscript.py` from the three files it lists -- edit those, not
this one.*

**Counting units differ between dataset instances** (sequence records, virus
taxa, a deduplicated species pool, protein-family profiles). No statement in the
Results aggregates observation counts across instances. Magnitudes are reported
as counts of tools or dataset instances, as presence or absence, or as shares
within a single instance.
"""


def body(text: str) -> str:
    """The file minus its own front matter: the H1 line, then every italic
    editorial note that follows it, up to the first paragraph of real prose."""
    text = re.sub(r"\A#[^\n]*\n", "", text)
    while True:
        stripped = text.lstrip("\n")
        m = re.match(r"\*[^*][^\0]*?\*\n(?=\n|\Z)", stripped)
        if not m:
            return stripped.rstrip("\n")
        text = stripped[m.end():]


def main() -> int:
    parts = [HEADER.format(date=datetime.date.today().isoformat())]
    for heading, name in SECTIONS:
        src = ROOT / name
        if not src.exists():
            print(f"FAILED: {name} is missing", file=sys.stderr)
            return 1
        parts.append(f"---\n\n{heading}\n\n{body(src.read_text())}\n")

    assembled = "\n".join(parts)
    old = OUT.read_text() if OUT.exists() else ""
    OUT.write_text(assembled)

    verb = "unchanged" if assembled == old else "rewritten"
    print(f"{OUT.name} {verb}: {len(assembled.splitlines())} lines from "
          f"{len(SECTIONS)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
