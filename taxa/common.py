"""Shared paths and helpers."""

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"                     # reference tables, and a link to the raw downloads
CONFIG = REPO / "config"
TOOL_TABLES = REPO / "outputs" / "tools"  # one standardized table per tool
TABLES = REPO / "outputs" / "tables"
FIGURES = REPO / "outputs" / "figures"

# Columns every per-tool table must have; one row is one source-supported
# family observation, before per-tool deduplication.
TOOL_COLUMNS = [
    "Tool",
    "Current_ICTV_family",
    "Source_unit",
    "Source_record_count",
    "Source_file",
    "Source_label",
    "Mapping_method",
    "Verification_status",
    "Notes",
]


def write_table(df: pd.DataFrame, path: Path) -> None:
    """Write a table as CSV and as an Excel workbook with the same stem."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path.with_suffix(".csv"), index=False)
    with pd.ExcelWriter(path.with_suffix(".xlsx"), engine="openpyxl") as writer:
        write_sheet(writer, df, path.stem)


def write_sheet(writer: pd.ExcelWriter, df: pd.DataFrame, name: str) -> None:
    """One sheet with a frozen, filterable header and readable column widths."""
    sheet_name = name[:31]  # Excel limit
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    ws = writer.sheets[sheet_name]
    ws.freeze_panes = "A2"
    if df.shape[1]:
        ws.auto_filter.ref = ws.dimensions
    for i, col in enumerate(df.columns, start=1):
        longest = max([len(str(col))] + [len(str(v)) for v in df[col].head(500)])
        ws.column_dimensions[ws.cell(1, i).column_letter].width = min(max(longest + 2, 8), 60)


def join_unique(values: pd.Series) -> str:
    """Sorted unique non-empty values, joined with '; '."""
    cleaned = sorted({str(v).strip() for v in values.dropna() if str(v).strip()})
    return "; ".join(cleaned)


def tools() -> pd.DataFrame:
    return pd.read_csv(CONFIG / "tools.csv", keep_default_na=False)
