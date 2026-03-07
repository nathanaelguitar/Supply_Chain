"""
sec_api_u4.py

Fetch Unit 4 assignment financial data directly from SEC EDGAR APIs
for 3M, P&G, and Walmart (2016-2021), then compute DAR/DI/DAP/CCC.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


# SEC requests should identify requester with name + email.
USER_AGENT = os.getenv("SEC_USER_AGENT", "Nathanael Gill (nathanael@example.com)")
YEARS = list(range(2016, 2022))
TICKERS = ["MMM", "PG", "WMT"]
BASE_URL = "https://data.sec.gov"
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
OUTPUT_CSV = Path("data/u4_sec_api_results_2016_2021.csv")


@dataclass(frozen=True)
class MetricConfig:
    label: str
    tag_candidates: list[str]
    metric_type: str  # "stock" (balance sheet) or "flow" (income statement)


METRICS = [
    MetricConfig("Accounts Receivable", ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], "stock"),
    MetricConfig("Inventory", ["InventoryNet"], "stock"),
    MetricConfig("Accounts Payable", ["AccountsPayableCurrent"], "stock"),
    MetricConfig(
        "Annual Sales",
        [
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
        ],
        "flow",
    ),
    MetricConfig("Annual COGS", ["CostOfGoodsSold", "CostOfGoodsAndServicesSold", "CostOfRevenue"], "flow"),
]


def _get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _ticker_to_cik_map() -> dict[str, str]:
    raw = _get_json(TICKER_MAP_URL)
    mapping = {}
    for _, record in raw.items():
        ticker = record["ticker"].upper()
        cik = str(record["cik_str"]).zfill(10)
        mapping[ticker] = cik
    return mapping


def _annual_10k_rows(company_facts: dict[str, Any], tag: str, metric_type: str) -> list[dict[str, Any]]:
    try:
        rows = company_facts["facts"]["us-gaap"][tag]["units"]["USD"]
    except KeyError:
        return []

    annual = []
    for row in rows:
        form = str(row.get("form", ""))
        if not form.startswith("10-K"):
            continue
        if row.get("fp") != "FY":
            continue
        end = str(row.get("end", ""))
        if len(end) < 4:
            continue
        if int(end[:4]) not in YEARS:
            continue

        if metric_type == "flow":
            start = row.get("start")
            if not start:
                continue
            try:
                days = (pd.to_datetime(end) - pd.to_datetime(start)).days
            except Exception:
                continue
            # Keep full-year values only.
            if days < 330 or days > 370:
                continue

        annual.append(row)
    return annual


def _merged_tag_values(
    company_facts: dict[str, Any], tag_candidates: list[str], metric_type: str
) -> tuple[str, dict[int, float]]:
    """
    Merge values across candidate tags in priority order.
    First candidate wins for a year; later candidates fill missing years.
    """
    merged: dict[int, float] = {}
    used_tags: list[str] = []

    for tag in tag_candidates:
        rows = _annual_10k_rows(company_facts, tag, metric_type)
        if not rows:
            continue

        latest_by_year: dict[int, dict[str, Any]] = {}
        for row in rows:
            year = int(str(row["end"])[:4])
            prior = latest_by_year.get(year)
            if prior is None or str(row.get("filed", "")) > str(prior.get("filed", "")):
                latest_by_year[year] = row

        values = {year: float(rec["val"]) for year, rec in latest_by_year.items()}
        if not values:
            continue

        for year in YEARS:
            if year not in merged and year in values:
                merged[year] = values[year]

        used_tags.append(tag)
        if len(merged) == len(YEARS):
            break

    tag_note = ";".join(used_tags) if used_tags else "MISSING"
    return tag_note, merged


def _compute_days_and_ccc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Days of Accounts Receivable"] = (df["Accounts Receivable"] / df["Annual Sales"]) * 365
    df["Days of Inventory"] = (df["Inventory"] / df["Annual COGS"]) * 365
    df["Days of Accounts Payable"] = (df["Accounts Payable"] / df["Annual COGS"]) * 365
    df["Cash Conversion Cycle"] = (
        df["Days of Accounts Receivable"] + df["Days of Inventory"] - df["Days of Accounts Payable"]
    )
    return df


def fetch_u4_sec_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns
    -------
    results_df:
        One row per company/year with financial values and computed day metrics.
    tag_audit_df:
        Chosen XBRL tag for each metric/company for traceability.
    """
    ticker_map = _ticker_to_cik_map()
    records: list[dict[str, Any]] = []
    tag_audit: list[dict[str, str]] = []

    for ticker in TICKERS:
        cik = ticker_map[ticker]
        company_facts = _get_json(f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json")
        company_name = company_facts.get("entityName", ticker)

        company_metric_values: dict[str, dict[int, float]] = {}
        for metric in METRICS:
            tag, values = _merged_tag_values(company_facts, metric.tag_candidates, metric.metric_type)
            company_metric_values[metric.label] = values
            tag_audit.append(
                {
                    "ticker": ticker,
                    "company": company_name,
                    "metric": metric.label,
                    "selected_tag": tag or "MISSING",
                }
            )

        for year in YEARS:
            row = {"ticker": ticker, "company": company_name, "year": year}
            for metric in METRICS:
                row[metric.label] = company_metric_values[metric.label].get(year)
            records.append(row)

        # SEC fair-access pacing.
        time.sleep(0.2)

    results_df = pd.DataFrame(records)
    results_df = _compute_days_and_ccc(results_df)
    results_df = results_df.sort_values(["ticker", "year"]).reset_index(drop=True)
    tag_audit_df = pd.DataFrame(tag_audit)
    return results_df, tag_audit_df


def save_outputs(results_df: pd.DataFrame, tag_audit_df: pd.DataFrame) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)
    tag_audit_df.to_csv(OUTPUT_CSV.with_name("u4_sec_api_tag_audit.csv"), index=False)


if __name__ == "__main__":
    results, audit = fetch_u4_sec_data()
    save_outputs(results, audit)

    print("\nSEC data fetched and saved.")
    print(f"Results: {OUTPUT_CSV}")
    print(f"Tag audit: {OUTPUT_CSV.with_name('u4_sec_api_tag_audit.csv')}")
    print("\nPreview:")
    print(results.round(3).to_string(index=False))
