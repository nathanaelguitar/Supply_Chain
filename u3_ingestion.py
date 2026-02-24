"""
u3_ingestion.py

Loads the Finger Lakes data from the Unit 3 assignment xlsx
using the existing ingestion pipeline and returns a clean DataFrame.

Columns produced:
    product       – wine product line name
    price         – selling price per unit
    demand_mean   – demand mean (mu)
    demand_std    – demand std  (sigma)
"""

import sys
from pathlib import Path
import pandas as pd

# Make sure the repo root is on the path
sys.path.insert(0, str(Path(__file__).parent))
from ingestion import ingest_excel, print_schema


FILE_NAME  = "bana6420_u3_assignment-finger-lakes-data.xlsx"
SHEET_NAME = "Data"


def load_finger_lakes() -> pd.DataFrame:
    """
    Ingest the Finger Lakes xlsx and return a clean product-level DataFrame.

    Returns
    -------
    pd.DataFrame with columns: product, price, demand_mean, demand_std
    """
    raw = ingest_excel(FILE_NAME, sheet_name=SHEET_NAME, verbose=False)

    # Row 2 (index 2) holds the true header; rows 3-13 are the product data
    # (row 14 is "Total" — dropped)
    df = raw.iloc[3:14].copy()                          # product rows only
    df.columns = raw.iloc[2].tolist()                   # promote header row

    # Keep and rename the four useful columns
    df = df[["Product Lines", "Price", "Demand Mean", "Demand Std"]].copy()
    df.columns = ["product", "price", "demand_mean", "demand_std"]

    # Cast numerics and reset index
    for col in ["price", "demand_mean", "demand_std"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["product"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = load_finger_lakes()
    print_schema(df)
    print(df.to_string(index=False))
