#!/usr/bin/env python3
"""Build every output table from the per-tool tables in outputs/tools.

Every table is written twice, as .csv and as .xlsx with the same name.

    per-tool tables -> combined -> eukaryote-associated scope -> order tables
                                                             -> supplementary table
"""

from __future__ import annotations

import pandas as pd

from common import DATA, TABLES, TOOL_TABLES, join_unique, tools, write_sheet, write_table

ICTV_REF = DATA / "intermediate" / "ictv_family_reference.csv"
EUK_SCOPE = DATA / "intermediate" / "ictv_family_host_source_scope.csv"


def combine() -> pd.DataFrame:
    """One row per tool and family, with the source evidence merged."""
    files = sorted(TOOL_TABLES.glob("*.csv"))
    if not files:
        raise SystemExit(f"no per-tool tables in {TOOL_TABLES}; run the processors first")
    raw = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    raw = raw[raw["Current_ICTV_family"].notna()
              & raw["Current_ICTV_family"].astype(str).str.strip().ne("")]
    raw["Source_record_count"] = pd.to_numeric(raw["Source_record_count"], errors="coerce").fillna(0)
    return (
        raw.groupby(["Tool", "Current_ICTV_family"], dropna=False)
        .agg(
            Source_unit=("Source_unit", join_unique),
            Source_record_count_total=("Source_record_count", "sum"),
            Source_files=("Source_file", join_unique),
            Source_labels=("Source_label", join_unique),
            Mapping_methods=("Mapping_method", join_unique),
            Verification_status=("Verification_status", join_unique),
            Notes=("Notes", join_unique),
        )
        .reset_index()
    )


def apply_eukaryotic_scope(combined: pd.DataFrame) -> pd.DataFrame:
    """Keep eukaryote-associated families and attach their ICTV taxonomy."""
    scope = pd.read_csv(EUK_SCOPE)
    keep = scope[scope["Include_in_eukaryotic_main_figure"].astype(str).str.lower().eq("yes")]
    scoped = combined.merge(
        keep[["Current_ICTV_family", "Eukaryotic_scope_status", "Host_sources"]],
        on="Current_ICTV_family", how="inner")
    ictv = pd.read_csv(ICTV_REF)
    scoped = scoped.merge(
        ictv[["Current_ICTV_family", "Realm", "Kingdom", "Phylum", "Class", "Order",
              "Genome", "Genome_class", "Species_count"]],
        on="Current_ICTV_family", how="left")
    scoped["Has_order_assignment"] = scoped["Order"].fillna("").astype(str).str.len().gt(0)
    return scoped


def order_tables(scoped: pd.DataFrame, config: pd.DataFrame) -> None:
    """The order-level long table, matrix and summaries that the figure reads."""
    assigned = scoped[scoped["Has_order_assignment"]].copy()

    long = (
        assigned.groupby(["Tool", "Order"], dropna=False)
        .agg(N_families_in_tool=("Current_ICTV_family", "nunique"),
             Family_names=("Current_ICTV_family", join_unique))
        .reset_index()
        .rename(columns={"Order": "Taxonomic_unit"})
    )
    write_table(long, TABLES / "order_family_count_long.csv")

    # Tools are grouped by prediction endpoint, and within a group the widest
    # family coverage comes first; that order is the figure's column order.
    endpoint_rank = {e: i for i, e in enumerate(config["Endpoint_category"].drop_duplicates())}
    family_totals = scoped.groupby("Tool")["Current_ICTV_family"].nunique()
    config = config.assign(
        Endpoint_rank=config["Endpoint_category"].map(endpoint_rank),
        Family_total=config["Tool"].map(family_totals).fillna(0),
    ).sort_values(["Endpoint_rank", "Family_total", "Tool"], ascending=[True, False, True])

    orders = sorted(assigned["Order"].dropna().unique())
    matrix = pd.DataFrame({"Tool": config["Tool"].tolist()})
    for order in orders:
        matrix[order] = 0
    for _, row in long.iterrows():
        matrix.loc[matrix["Tool"].eq(row["Tool"]), row["Taxonomic_unit"]] = int(row["N_families_in_tool"])
    matrix.insert(1, "N_current_families", matrix[orders].sum(axis=1).astype(int))
    matrix.insert(2, "N_taxonomic_units", (matrix[orders] > 0).sum(axis=1).astype(int))
    write_table(matrix, TABLES / "order_family_count_matrix.csv")

    unassigned = scoped[~scoped["Has_order_assignment"]].copy()
    write_table(
        unassigned.groupby(["Tool", "Current_ICTV_family"], dropna=False)
        .agg(Source_unit=("Source_unit", join_unique), Source_files=("Source_files", join_unique))
        .reset_index(),
        TABLES / "families_without_order.csv")

    per_tool = scoped.groupby("Tool").agg(
        N_families=("Current_ICTV_family", "nunique"),
        N_order_assigned_families=("Has_order_assignment", "sum"),
        N_orders=("Order", lambda s: s.dropna().loc[s.dropna().astype(str).str.len().gt(0)].nunique()),
    ).reset_index()
    per_tool["N_families_without_order"] = per_tool["Tool"].map(
        unassigned.groupby("Tool")["Current_ICTV_family"].nunique()).fillna(0).astype(int)
    tool_summary = config[["Tool", "Endpoint_category", "Evidence_unit_code", "Display_name"]].merge(
        per_tool, on="Tool", how="left").fillna(0)
    write_table(tool_summary, TABLES / "tool_summary.csv")

    write_table(
        assigned.groupby("Order").agg(
            N_tools=("Tool", "nunique"),
            N_families_union=("Current_ICTV_family", "nunique"),
            Genome_class=("Genome_class", join_unique),
        ).reset_index(),
        TABLES / "order_summary.csv")

    print(f"order tables: {matrix.shape[0]} tools x {len(orders)} orders")


SUPPLEMENTARY_COLUMNS = [
    "Tool", "Display_name", "Endpoint_category", "Current_ICTV_family", "ICTV_order",
    "Genome", "Genome_class", "Source_unit", "Source_label_before_harmonization",
    "Source_record_count_total", "Source_files", "Mapping_methods", "Verification_status",
    "Eukaryotic_scope_status", "Host_sources", "Has_order_assignment",
]


def supplementary_table(scoped: pd.DataFrame, config: pd.DataFrame) -> None:
    """One row per tool and family, for the supplementary workbook."""
    out = (
        scoped.merge(config[["Tool", "Display_name", "Endpoint_category"]], on="Tool", how="left")
        .rename(columns={"Order": "ICTV_order", "Source_labels": "Source_label_before_harmonization"})
    )
    out = out[SUPPLEMENTARY_COLUMNS].sort_values(
        ["Endpoint_category", "Tool", "Has_order_assignment", "ICTV_order", "Current_ICTV_family"],
        ascending=[True, True, False, True, True])
    write_table(out, TABLES / "supplementary_family_harmonization_table.csv")

    by_family = (
        out.groupby("Current_ICTV_family", dropna=False)
        .agg(
            ICTV_order=("ICTV_order", lambda s: join_unique(s) or "No official ICTV order assignment"),
            Genome=("Genome", join_unique),
            Tools_covering_taxon_n=("Tool", "nunique"),
            Tools_covering_taxon=("Display_name", join_unique),
            Endpoint_categories=("Endpoint_category", join_unique),
            Source_unit_types=("Source_unit", join_unique),
            Source_labels_before_harmonization=("Source_label_before_harmonization", join_unique),
        )
        .reset_index()
        .sort_values(["ICTV_order", "Current_ICTV_family"])
    )
    write_table(by_family, TABLES / "supplementary_family_harmonization_by_family.csv")

    # The supplementary workbook holds both views; it replaces the one-sheet
    # .xlsx that write_table made for the tool x family table above.
    path = TABLES / "supplementary_family_harmonization_table.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        write_sheet(writer, by_family, "By family")
        write_sheet(writer, out, "Tool x family")
    print(f"supplementary table: {out.shape[0]} tool x family rows, "
          f"{by_family.shape[0]} families")


def main() -> None:
    config = tools()
    combined = combine()

    missing = sorted(set(config["Tool"]) - set(combined["Tool"]))
    if missing:
        raise SystemExit(f"no per-tool table for: {', '.join(missing)}")
    unexpected = sorted(set(combined["Tool"]) - set(config["Tool"]))
    if unexpected:
        raise SystemExit(f"per-tool table not listed in config/tools.csv: {', '.join(unexpected)}")

    scoped = apply_eukaryotic_scope(combined)
    write_table(scoped, TABLES / "family_presence_eukaryotic.csv")
    print(f"eukaryote-associated scope: {scoped['Current_ICTV_family'].nunique()} families, "
          f"{len(scoped)} tool-family cells")

    order_tables(scoped, config)
    supplementary_table(scoped, config)


if __name__ == "__main__":
    main()
