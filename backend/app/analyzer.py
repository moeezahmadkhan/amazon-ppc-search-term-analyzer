"""
SearchTermAnalyzer -- Core engine that ingests an Amazon SP Search Term Report
and segregates rows into 4 performance buckets based on user-defined thresholds.
"""

from __future__ import annotations

import io
from typing import BinaryIO, Dict, Union

import pandas as pd

PCT_COLUMNS = ["Click-through Rate", "Conversion Rate", "ACOS"]

TARGETED_MATCH_TYPES = {"Exact", "Phrase", "Broad"}

OUTPUT_COLUMNS = [
    "Customer Search Term",
    "Campaign Name (Informational only)",
    "Ad Group Name (Informational only)",
    "Portfolio Name (Informational only)",
    "Match Type",
    "Impressions",
    "Clicks",
    "Spend",
    "Sales",
    "Orders",
    "ACOS",
    "Conversion Rate",
    "CPC",
    "ROAS",
]

DEFAULT_THRESHOLDS = {
    "click_threshold": 10,
    "acos_threshold": 0.30,
    "cvr_threshold": 0.10,
    "low_click_threshold": 10,
    "order_threshold": 2,
}


class SearchTermAnalyzer:
    """Stateless analyzer: load data, normalize, then run any combination of filters."""

    def __init__(self):
        self.df: pd.DataFrame | None = None
        self._raw_df: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_data(self, source: Union[str, BinaryIO, bytes], file_type: str = "auto") -> pd.DataFrame:
        """
        Read an Excel or CSV file into a DataFrame.
        `source` can be a file path (str), file-like object, or raw bytes.
        `file_type` can be 'csv', 'excel', or 'auto' (detect from extension / content).
        """
        if isinstance(source, bytes):
            source = io.BytesIO(source)

        if file_type == "auto":
            if isinstance(source, str):
                file_type = "csv" if source.lower().endswith(".csv") else "excel"
            else:
                file_type = "excel"

        if file_type == "csv":
            self.df = pd.read_csv(source)
        else:
            self.df = pd.read_excel(source, engine="openpyxl")

        self._raw_df = self.df.copy()
        self._normalize()
        return self.df

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------
    def _normalize(self):
        self._strip_column_names()
        self._normalize_percentages()
        self._coerce_numeric_columns()
        self._drop_impression_share()

    def _strip_column_names(self):
        self.df.columns = self.df.columns.str.strip()

    def _normalize_percentages(self):
        """Convert '1.84%' style strings to 0.0184 floats."""
        for col in PCT_COLUMNS:
            if col not in self.df.columns:
                continue
            series = self.df[col]
            if series.dtype == object:
                self.df[col] = (
                    series.astype(str)
                    .str.strip()
                    .str.rstrip("%")
                    .replace("", "0")
                    .astype(float)
                    / 100.0
                )
            elif not pd.api.types.is_float_dtype(series):
                self.df[col] = pd.to_numeric(series, errors="coerce").fillna(0.0)

    def _coerce_numeric_columns(self):
        numeric_cols = ["Impressions", "Clicks", "Spend", "Sales", "Orders", "Units", "CPC", "ROAS"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0)

    def _drop_impression_share(self):
        for col in list(self.df.columns):
            if "impression share" in col.lower():
                self.df.drop(columns=[col], inplace=True)

    # ------------------------------------------------------------------
    # Filter methods
    # ------------------------------------------------------------------
    def filter_wasted_adspend(self, click_threshold: int = 10) -> pd.DataFrame:
        """Clicks >= threshold AND Orders == 0"""
        mask = (self.df["Clicks"] >= click_threshold) & (self.df["Orders"] == 0)
        return self._select_output(mask)

    def filter_inefficient_adspend(self, acos_threshold: float = 0.30) -> pd.DataFrame:
        """ACOS >= threshold AND Orders > 0"""
        mask = (self.df["ACOS"] >= acos_threshold) & (self.df["Orders"] > 0)
        return self._select_output(mask)

    def filter_scaling_opportunity(
        self, cvr_threshold: float = 0.10, low_click_threshold: int = 10
    ) -> pd.DataFrame:
        """Match Type == 'Exact' AND Conversion Rate >= threshold AND Clicks <= low_click_threshold"""
        mask = (
            (self.df["Match Type"].str.strip().str.lower() == "exact")
            & (self.df["Conversion Rate"] >= cvr_threshold)
            & (self.df["Clicks"] <= low_click_threshold)
        )
        return self._select_output(mask)

    def filter_harvesting_opportunity(self, order_threshold: int = 2) -> pd.DataFrame:
        """Match Type NOT in targeted set AND Orders > threshold"""
        targeted_lower = {m.lower() for m in TARGETED_MATCH_TYPES}
        mask = (
            (~self.df["Match Type"].str.strip().str.lower().isin(targeted_lower))
            & (self.df["Orders"] > order_threshold)
        )
        return self._select_output(mask)

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------
    def analyze(self, thresholds: Dict[str, float] | None = None) -> Dict[str, pd.DataFrame]:
        """Run all 4 filters and return a dict keyed by category name."""
        t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        return {
            "Wasted Adspend": self.filter_wasted_adspend(
                click_threshold=int(t["click_threshold"]),
            ),
            "Inefficient Adspend": self.filter_inefficient_adspend(
                acos_threshold=float(t["acos_threshold"]),
            ),
            "Scaling Opportunity": self.filter_scaling_opportunity(
                cvr_threshold=float(t["cvr_threshold"]),
                low_click_threshold=int(t["low_click_threshold"]),
            ),
            "Harvesting Opportunity": self.filter_harvesting_opportunity(
                order_threshold=int(t["order_threshold"]),
            ),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _select_output(self, mask: pd.Series) -> pd.DataFrame:
        available = [c for c in OUTPUT_COLUMNS if c in self.df.columns]
        return self.df.loc[mask, available].reset_index(drop=True)

    @property
    def raw_dataframe(self) -> pd.DataFrame | None:
        return self._raw_df

    @property
    def dataframe(self) -> pd.DataFrame | None:
        return self.df
