"""
u4_ingestion.py

Loads the Unit 4 SEC data workbook and reshapes the "Data" sheet into
an analysis-ready long format.
"""

import sys
from pathlib import Path
import pandas as pd

# Make sure the repo root is on the path
sys.path.insert(0, str(Path(__file__).parent))
from ingestion import ingest_excel, print_schema


FILE_NAME = "bana6420_u4_assignment-sec-data.xlsx"
SHEET_NAME = "Data"


def _clean_company_name(raw_name: str) -> str:
    """Convert values like '3M ($ million)' to '3M'."""
    return str(raw_name).split(" (")[0].strip()


def load_u4_sec_data(drop_empty_values: bool = False) -> pd.DataFrame:
    """
    Ingest Unit 4 SEC data and return long-format records.

    Parameters
    ----------
    drop_empty_values:
        If True, rows with missing numeric values are removed.

    Returns
    -------
    pd.DataFrame
        Columns: company, metric, year, value
    """
    raw = ingest_excel(FILE_NAME, sheet_name=SHEET_NAME, verbose=False)
    if raw is None:
        raise FileNotFoundError(f"Could not load {FILE_NAME} from data directory.")

    # Work with explicit integer column labels for stable row/column indexing.
    raw = raw.copy()
    raw.columns = range(raw.shape[1])

    header_mask = raw[1].astype(str).str.contains(r"\(\$ million\)", na=False)
    header_rows = raw.index[header_mask].tolist()

    records = []

    for i, start_row in enumerate(header_rows):
        company = _clean_company_name(raw.at[start_row, 1])
        end_row = header_rows[i + 1] if i + 1 < len(header_rows) else len(raw)

        years = [int(y) for y in raw.loc[start_row, 2:7].tolist() if pd.notna(y)]

        for row_idx in range(start_row + 1, end_row):
            metric = raw.at[row_idx, 1]
            if pd.isna(metric):
                continue

            metric = str(metric).strip()
            for col_offset, year in enumerate(years, start=2):
                value = pd.to_numeric(raw.at[row_idx, col_offset], errors="coerce")
                records.append(
                    {
                        "company": company,
                        "metric": metric,
                        "year": year,
                        "value": value,
                    }
                )

    df = pd.DataFrame(records)
    if drop_empty_values:
        df = df.dropna(subset=["value"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = load_u4_sec_data(drop_empty_values=False)
    print_schema(df)
    print(df.head(24).to_string(index=False))
