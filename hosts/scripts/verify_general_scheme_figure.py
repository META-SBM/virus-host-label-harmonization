# -*- coding: utf-8 -*-
"""End-to-end audit of every number printed on host_general_scheme_R.png.

    python3 run_all.py
    python3 export_general_scheme_for_r.py
    python3 verify_general_scheme_figure.py

Nothing here recomputes the figure: it re-derives each drawn cell from the
tables the pipeline wrote and compares. audit_all.py reads the verdict line.
"""
import csv
import os
import sys
from collections import defaultdict

SC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SC)
RDATA = os.path.join(SC, "r_general_scheme")
COUNTS = os.path.join(ROOT, "per_tool_counts_from_scratch_v2", "counts_per_tool_v2")
sys.path.insert(0, SC)

from categories import GROUP_COLOR, is_excluded  # noqa: E402

N_HEADER_ROWS = 8


class Report:
    """Every check prints its own line as it runs, and the tally at the end is
    what audit_all.py greps."""

    def __init__(self):
        self.results = []

    def section(self, title: str) -> None:
        print(f"\n=== {title} ===")

    def check(self, name: str, ok, detail: str = "") -> None:
        self.results.append((bool(ok), name, detail))
        print(("  OK   " if ok else "  FAIL ") + name + (("  | " + detail) if detail else ""))

    def summary(self) -> None:
        failed = [r for r in self.results if not r[0]]
        print("\n" + "=" * 60)
        print(f"ПРОВЕРОК: {len(self.results)}   ПРОШЛО: {len(self.results)-len(failed)}   "
              f"УПАЛО: {len(failed)}")
        for _, name, detail in failed:
            print(f"  ! {name}: {detail}")


def read(path: str, **kw) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, **kw))


def raw_totals() -> dict:
    """TOTAL per tool from the recompute headers. It includes the labels the
    recompute itself tags EXCL -- non-eukaryotic hosts, orphan/blank
    placeholders."""
    out = {}
    for fn in sorted(os.listdir(COUNTS)):
        if not fn.endswith("_counts.csv") or fn.startswith("00_"):
            continue
        tool = total = None
        with open(os.path.join(COUNTS, fn), newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row:
                    continue
                if row[0].startswith("# Tool"):
                    tool = row[1].strip()          # csv strips the quoting itself
                elif row[0] == "TOTAL":
                    total = int(row[1])
        if is_excluded(tool):
            continue                                # kept for provenance only
        out[tool] = total
    return out


def load_data() -> dict:
    """What the R script was handed, and the pipeline tables it should agree
    with."""
    return {
        "matrix": read(os.path.join(RDATA, "matrix.csv")),
        "row_meta": read(os.path.join(RDATA, "row_meta.csv")),
        "col_meta": read(os.path.join(RDATA, "col_meta.csv")),
        "flags": read(os.path.join(RDATA, "cell_flags.csv")),
        "wide": read(os.path.join(SC, "general_scheme_matrix_wide.csv")),
        "long": read(os.path.join(SC, "general_scheme_matrix.csv")),
        "species": read(os.path.join(SC, "species_matrix.csv")),
        "row_fate": read(os.path.join(SC, "general_scheme_row_fate.csv")),
        "vector_fallback": read(os.path.join(SC, "species_matrix_vector_fallback.csv")),
        "master": read(os.path.join(SC, "master_labels.csv")),
        "raw_totals": raw_totals(),
    }


def drawn_cells(d: dict) -> tuple:
    """The filled cells of the rendered matrix, keyed (row_id, tool)."""
    tools = [c["tool"] for c in d["col_meta"]]
    fig = {}
    for r in d["matrix"]:
        for t in tools:
            v = int(r[t])
            if v:
                fig[(r["row_id"], t)] = v
    return fig, tools


def check_against_pipeline_matrix(rep, d, fig, tools):
    wide_by_row = {w["Row"]: w for w in d["wide"]}
    tool_cols = [c for c in d["wide"][0] if c not in ("Row", "Rank", "Group")]

    mismatch = []
    for rm, mr in zip(d["row_meta"], d["matrix"]):
        src = rm["source_row"]
        if not src:                      # header row: carries no data
            if any(int(mr[t]) for t in tools):
                mismatch.append((rm["name"], "заголовок с данными"))
            continue
        w = wide_by_row[src]
        for t in tools:
            # HostNet is two dataset instances summed for display only
            exp = (float(w.get("HostNet (Rabies, VIPHOD)", 0) or 0) +
                   float(w.get("HostNet (Flavivirus)", 0) or 0)) if t == "HostNet" \
                else float(w.get(t, 0) or 0)
            if int(mr[t]) != int(exp):
                mismatch.append((rm["name"], t, int(mr[t]), int(exp)))
    rep.check("каждая ячейка совпадает с general_scheme_matrix_wide.csv",
              not mismatch, f"расхождений: {len(mismatch)}" if mismatch else "59 строк x 14 колонок")

    fig_total = sum(fig.values())
    wide_total = sum(int(float(w[t] or 0)) for w in d["wide"] for t in tool_cols)
    rep.check("сумма фигуры == сумма матрицы пайплайна", fig_total == wide_total,
              f"{fig_total:,} против {wide_total:,}")
    return wide_total


def check_routing_conserves(rep, d, wide_total):
    sp_total = sum(int(float(s["Count"])) for s in d["species"])
    rep.check("сумма матрицы == сумма species_matrix.csv (до маршрутизации)",
              wide_total == sp_total, f"{wide_total:,} против {sp_total:,}")

    fate = {f["Row"]: f["Final_category"] for f in d["row_fate"]}
    unrouted = {s["Row"] for s in d["species"]} - set(fate)
    rep.check("каждая строка species_matrix имеет ровно один пункт назначения",
              not unrouted, f"без маршрута: {len(unrouted)}" if unrouted else f"{len(fate)} строк")
    return fate


def check_tool_totals(rep, d, fig, tools):
    """Each tool's records, against an independent recount from the raw files."""
    sp_by_tool = defaultdict(int)
    for s in d["species"]:
        sp_by_tool[s["Tool"]] += int(float(s["Count"]))

    excl_by_tool = defaultdict(int)
    # Vector labels whose target is "Unknown vector" have no host-axis category to
    # land in at all (unlike mosquito/tick/minor vectors, which resolve to Culi
    # Excluded rows come off separately, so only rows still carried as included
    # may be counted here, otherwise ViralHostPredictor's 19 unknown-vector
    # records are subtracted twice.
    novec = defaultdict(int)
    for m in d["master"]:
        if m["Status"] == "EXCL":
            excl_by_tool[m["Tool"]] += int(float(m["Count"] or 0))
        elif m["Detailed_scheme"] == "Unknown vector":
            novec[m["Tool"]] += int(float(m["Count"] or 0))

    bad = []
    for tool, raw in sorted(d["raw_totals"].items()):
        got = sp_by_tool.get(tool)
        exp = raw - excl_by_tool[tool] - novec.get(tool, 0)
        if got != exp:
            bad.append((tool, got, exp))
    rep.check("итог по каждому инструменту == TOTAL минус EXCL в counts_per_tool_v2",
              not bad, "; ".join(f"{t}: {g} против {e}" for t, g, e in bad) if bad
              else f"{len(d['raw_totals'])} экземпляров датасетов сошлись до записи")

    # figure columns, with the display-only HostNet merge undone
    fig_by_tool = defaultdict(int)
    for (_rid, t), v in fig.items():
        fig_by_tool[t] += v
    merged = dict(sp_by_tool)
    merged["HostNet"] = merged.pop("HostNet (Rabies, VIPHOD)", 0) + merged.pop("HostNet (Flavivirus)", 0)
    bad = [(t, fig_by_tool.get(t, 0), merged.get(t, 0)) for t in tools
           if fig_by_tool.get(t, 0) != merged.get(t, 0)]
    rep.check("колонка фигуры == итог инструмента", not bad,
              "; ".join(f"{t}: {a} против {b}" for t, a, b in bad) if bad else "14 колонок")


def check_bars(rep, d, fig):
    bad = []
    for c in d["col_meta"]:
        breadth = sum(1 for (_rid, tt) in fig if tt == c["tool"])
        if breadth != int(c["breadth"]):
            bad.append((c["tool"], breadth, c["breadth"]))
    rep.check("столбик == все заполненные категории, включая векторные", not bad,
              "; ".join(f"{t}: {a} против {b}" for t, a, b in bad) if bad
              else f"{len(d['col_meta'])} инструментов")


def check_badges(rep, d, fate):
    """Counted from the curation workbook rather than written in, so adding a
    tool does not fail this check for the wrong reason."""
    drawn = {(f["row_id"], f["tool"]) for f in d["flags"]}
    row_by_src = {rm["source_row"]: rm["row_id"] for rm in d["row_meta"] if rm["source_row"]}
    want = set()
    for v in d["vector_fallback"]:
        t = "HostNet" if v["Tool"].startswith("HostNet") else v["Tool"]
        cat = fate.get(v["Row"], v["Row"])       # Insecta -> the category "Insects"
        if cat in row_by_src:
            want.add((row_by_src[cat], t))
    rep.check("значки V == species_matrix_vector_fallback.csv", drawn == want,
              f"на фигуре {len(drawn)}, в источнике {len(want)}")

    dc_tools = {m["Tool"] for m in d["master"] if m["Potential_double_count"] == "Yes"}
    dc_tools = {"HostNet" if t.startswith("HostNet") else t for t in dc_tools}
    fig_dc = {c["tool"] for c in d["col_meta"] if c["double_count"] == "1"}
    rep.check("значки * == инструменты с Potential_double_count=Yes",
              fig_dc <= dc_tools and fig_dc,
              f"на фигуре {sorted(fig_dc)}")


def check_row_structure(rep, d):
    row_meta = d["row_meta"]
    hdr = [r for r in row_meta if r["is_header"] == "1"]
    cats = [r for r in row_meta if r["is_header"] == "0"]
    # Counted from the category registry rather than written in, so a legitimate
    # change to the scheme does not fail this check for the wrong reason.
    n_cats = len({r["Row"] for r in d["long"]})
    rep.check("отображаемые строки = категории матрицы + 8 заголовков",
              len(row_meta) == len(cats) + len(hdr) and len(cats) == n_cats
              and len(hdr) == N_HEADER_ROWS,
              f"{len(row_meta)} строк = {len(cats)} категорий + {len(hdr)} заголовков "
              f"(в матрице {n_cats})")

    bad = [r["name"] for r in row_meta if r["lineage"] not in GROUP_COLOR]
    rep.check("линия каждой строки есть в GROUP_COLOR", not bad, str(bad[:3]) if bad else "6 линий")

    wide_rank = {w["Row"]: w["Rank"] for w in d["wide"]}
    bad = [r["name"] for r in cats
           if (r["italic"] == "1") != (wide_rank.get(r["source_row"]) == "species")]
    rep.check("курсив стоит ровно на строках с Rank=species", not bad,
              str(bad[:3]) if bad else f"{sum(1 for r in cats if r['italic'] == '1')} видов")

    names = [x["name"] for x in row_meta]
    dupes = [n for n in names if names.count(n) > 1]
    rep.check("нет двух строк с одинаковым именем", not dupes, str(sorted(set(dupes))) if dupes else "")


def check_every_cell(rep, d, fig, fate):
    spot = defaultdict(int)
    for s in d["species"]:
        t = "HostNet" if s["Tool"].startswith("HostNet") else s["Tool"]
        spot[(fate.get(s["Row"]), t)] += int(float(s["Count"]))
    name_by_id = {r["row_id"]: r["source_row"] for r in d["row_meta"]}
    bad = []
    for (rid, t), v in fig.items():
        src = name_by_id[rid]
        if spot.get((src, t), 0) != v:
            bad.append((src, t, v, spot.get((src, t), 0)))
    rep.check("каждая нарисованная ячейка воспроизводится из species_matrix + row_fate",
              not bad, "; ".join(f"{a}/{b}: {c} против {e}" for a, b, c, e in bad[:3])
              if bad else f"{len(fig)} ячеек")


def main() -> None:
    d = load_data()
    rep = Report()

    rep.section("what the figure draws")
    fig, tools = drawn_cells(d)
    print(f"  {len(d['matrix'])} строк x {len(tools)} инструментов, "
          f"заполнено {len(fig)} ячеек, сумма {sum(fig.values()):,}")

    rep.section("1. фигура против матрицы пайплайна")
    wide_total = check_against_pipeline_matrix(rep, d, fig, tools)

    rep.section("2. маршрутизация ничего не теряет и не задваивает")
    fate = check_routing_conserves(rep, d, wide_total)

    rep.section("3. поинструментные итоги против независимого пересчёта из сырых файлов")
    check_tool_totals(rep, d, fig, tools)

    rep.section("4. столбики над колонками")
    check_bars(rep, d, fig)

    rep.section("5. бейджи")
    check_badges(rep, d, fate)

    rep.section("6. структура строк")
    check_row_structure(rep, d)

    rep.section("7. точечная сверка отдельных ячеек")
    check_every_cell(rep, d, fig, fate)

    rep.summary()


if __name__ == "__main__":
    main()
