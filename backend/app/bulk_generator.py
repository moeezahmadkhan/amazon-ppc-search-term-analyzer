"""
Generates an Amazon-format bulk negation CSV from Wasted Adspend results.
Matches the exact column order and values from the provided negation bulk sample:
  - Entity: "Campaign Negative Keyword"
  - Match Type: "Negative Exact"
  - Keyword Text: the wasted Customer Search Term
  - All metrics zeroed out
  - Campaign Name + Portfolio Name preserved from source row
"""

from __future__ import annotations

import csv
import io
from typing import List

import pandas as pd

BULK_COLUMNS = [
    "Product",
    "Entity",
    "Campaign Name (Informational only)",
    "Ad Group Name (Informational only)",
    "Portfolio Name (Informational only)",
    "State",
    "Campaign State (Informational only)",
    "Ad Group State (Informational only)",
    "Keyword Text",
    "Match Type",
    "Impressions",
    "Clicks",
    "Click-through Rate",
    "Spend",
    "Sales",
    "Orders",
    "Units",
    "Conversion Rate",
    "ACOS",
    "CPC",
    "ROAS",
]


def _build_negation_row(source_row: dict) -> dict:
    """Transform a Wasted Adspend row into a bulk negation row."""
    return {
        "Product": "Sponsored Products",
        "Entity": "Campaign Negative Keyword",
        "Campaign Name (Informational only)": source_row.get("Campaign Name (Informational only)", ""),
        "Ad Group Name (Informational only)": "",
        "Portfolio Name (Informational only)": source_row.get("Portfolio Name (Informational only)", ""),
        "State": "enabled",
        "Campaign State (Informational only)": "enabled",
        "Ad Group State (Informational only)": "",
        "Keyword Text": source_row.get("Customer Search Term", ""),
        "Match Type": "Negative Exact",
        "Impressions": 0,
        "Clicks": 0,
        "Click-through Rate": 0,
        "Spend": 0,
        "Sales": 0,
        "Orders": 0,
        "Units": 0,
        "Conversion Rate": 0,
        "ACOS": 0,
        "CPC": 0,
        "ROAS": 0,
    }


def generate_bulk_csv(
    wasted_df: pd.DataFrame,
    output_path: str | None = None,
) -> bytes | str:
    """
    Generate a bulk negation CSV from the Wasted Adspend DataFrame.
    If output_path is given, writes to disk and returns the path.
    Otherwise returns raw CSV bytes (for streaming via API).
    """
    rows: List[dict] = []
    seen_terms: set = set()

    for _, row in wasted_df.iterrows():
        search_term = str(row.get("Customer Search Term", "")).strip()
        campaign = str(row.get("Campaign Name (Informational only)", "")).strip()
        key = (search_term.lower(), campaign)

        if not search_term or key in seen_terms:
            continue
        seen_terms.add(key)

        rows.append(_build_negation_row(row.to_dict()))

    if output_path is not None:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=BULK_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        return output_path

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=BULK_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
