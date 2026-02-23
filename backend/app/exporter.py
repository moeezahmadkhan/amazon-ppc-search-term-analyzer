"""
Generates a 5-sheet Excel analysis report from the analyzer results.
  Sheet 1: Summary Dashboard
  Sheet 2: Wasted Adspend
  Sheet 3: Inefficient Adspend
  Sheet 4: Scaling Opportunity
  Sheet 5: Harvesting Opportunity
"""

from __future__ import annotations

import io
from typing import Dict

import pandas as pd

CATEGORY_ORDER = [
    "Wasted Adspend",
    "Inefficient Adspend",
    "Scaling Opportunity",
    "Harvesting Opportunity",
]

SHEET_COLORS = {
    "Summary Dashboard": "#1F4E79",
    "Wasted Adspend": "#C00000",
    "Inefficient Adspend": "#ED7D31",
    "Scaling Opportunity": "#00B050",
    "Harvesting Opportunity": "#4472C4",
}

PCT_FORMAT_COLS = {"ACOS", "Conversion Rate", "Click-through Rate"}
CURRENCY_FORMAT_COLS = {"Spend", "Sales", "CPC", "ROAS"}


def _build_summary(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate stats across all 4 categories into a summary table."""
    rows = []
    for cat in CATEGORY_ORDER:
        df = results.get(cat, pd.DataFrame())
        n = len(df)
        total_clicks = int(df["Clicks"].sum()) if "Clicks" in df.columns and n else 0
        total_spend = float(df["Spend"].sum()) if "Spend" in df.columns and n else 0.0
        total_sales = float(df["Sales"].sum()) if "Sales" in df.columns and n else 0.0
        total_orders = int(df["Orders"].sum()) if "Orders" in df.columns and n else 0
        avg_acos = float(df["ACOS"].mean()) if "ACOS" in df.columns and n else 0.0
        avg_cvr = float(df["Conversion Rate"].mean()) if "Conversion Rate" in df.columns and n else 0.0

        rows.append({
            "Category": cat,
            "Search Terms": n,
            "Total Clicks": total_clicks,
            "Total Spend": total_spend,
            "Total Sales": total_sales,
            "Total Orders": total_orders,
            "Avg ACOS": avg_acos,
            "Avg CVR": avg_cvr,
        })

    totals_clicks = sum(r["Total Clicks"] for r in rows)
    totals_spend = sum(r["Total Spend"] for r in rows)
    totals_sales = sum(r["Total Sales"] for r in rows)
    totals_orders = sum(r["Total Orders"] for r in rows)
    totals_terms = sum(r["Search Terms"] for r in rows)

    rows.append({
        "Category": "TOTAL",
        "Search Terms": totals_terms,
        "Total Clicks": totals_clicks,
        "Total Spend": totals_spend,
        "Total Sales": totals_sales,
        "Total Orders": totals_orders,
        "Avg ACOS": totals_spend / totals_sales if totals_sales > 0 else 0.0,
        "Avg CVR": totals_orders / totals_clicks if totals_clicks > 0 else 0.0,
    })

    return pd.DataFrame(rows)


def generate_report(
    results: Dict[str, pd.DataFrame],
    output_path: str | None = None,
) -> bytes | str:
    """
    Generate a formatted 5-sheet Excel workbook.
    If output_path is given, writes to disk and returns the path.
    Otherwise returns raw bytes (for streaming via API).
    """
    buffer = io.BytesIO() if output_path is None else output_path

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        wb = writer.book

        # ----- Common formats -----
        header_fmt = wb.add_format({
            "bold": True,
            "bg_color": "#1F4E79",
            "font_color": "#FFFFFF",
            "border": 1,
            "text_wrap": True,
            "valign": "vcenter",
            "align": "center",
        })
        pct_fmt = wb.add_format({"num_format": "0.00%", "align": "center"})
        currency_fmt = wb.add_format({"num_format": "$#,##0.00", "align": "center"})
        int_fmt = wb.add_format({"num_format": "#,##0", "align": "center"})
        text_fmt = wb.add_format({"text_wrap": True, "valign": "vcenter"})
        total_row_fmt = wb.add_format({
            "bold": True,
            "bg_color": "#D9E2F3",
            "border": 1,
            "align": "center",
        })
        total_pct_fmt = wb.add_format({
            "bold": True,
            "bg_color": "#D9E2F3",
            "border": 1,
            "num_format": "0.00%",
            "align": "center",
        })
        total_currency_fmt = wb.add_format({
            "bold": True,
            "bg_color": "#D9E2F3",
            "border": 1,
            "num_format": "$#,##0.00",
            "align": "center",
        })
        total_int_fmt = wb.add_format({
            "bold": True,
            "bg_color": "#D9E2F3",
            "border": 1,
            "num_format": "#,##0",
            "align": "center",
        })

        # ===== Sheet 1: Summary Dashboard =====
        summary_df = _build_summary(results)
        summary_df.to_excel(writer, sheet_name="Summary Dashboard", startrow=1, index=False, header=False)
        ws_summary = writer.sheets["Summary Dashboard"]
        ws_summary.set_tab_color(SHEET_COLORS["Summary Dashboard"])

        for col_idx, col_name in enumerate(summary_df.columns):
            ws_summary.write(0, col_idx, col_name, header_fmt)

        ws_summary.set_column(0, 0, 28, text_fmt)
        ws_summary.set_column(1, 1, 14, int_fmt)
        ws_summary.set_column(2, 2, 14, int_fmt)
        ws_summary.set_column(3, 3, 14, currency_fmt)
        ws_summary.set_column(4, 4, 14, currency_fmt)
        ws_summary.set_column(5, 5, 14, int_fmt)
        ws_summary.set_column(6, 6, 14, pct_fmt)
        ws_summary.set_column(7, 7, 14, pct_fmt)

        total_row_idx = len(summary_df)
        for col_idx in range(len(summary_df.columns)):
            val = summary_df.iloc[-1, col_idx]
            col_name = summary_df.columns[col_idx]
            if col_name in ("Avg ACOS", "Avg CVR"):
                ws_summary.write(total_row_idx, col_idx, val, total_pct_fmt)
            elif col_name in ("Total Spend", "Total Sales"):
                ws_summary.write(total_row_idx, col_idx, val, total_currency_fmt)
            elif col_name in ("Search Terms", "Total Clicks", "Total Orders"):
                ws_summary.write(total_row_idx, col_idx, val, total_int_fmt)
            else:
                ws_summary.write(total_row_idx, col_idx, val, total_row_fmt)

        # ===== Sheets 2-5: Category data =====
        for cat in CATEGORY_ORDER:
            df = results.get(cat, pd.DataFrame())
            sheet_name = cat
            df.to_excel(writer, sheet_name=sheet_name, startrow=1, index=False, header=False)
            ws = writer.sheets[sheet_name]
            ws.set_tab_color(SHEET_COLORS.get(cat, "#000000"))

            if df.empty:
                ws.write(0, 0, "No data matched this category.", text_fmt)
                continue

            for col_idx, col_name in enumerate(df.columns):
                ws.write(0, col_idx, col_name, header_fmt)

            for col_idx, col_name in enumerate(df.columns):
                if col_name in PCT_FORMAT_COLS:
                    ws.set_column(col_idx, col_idx, 16, pct_fmt)
                elif col_name in CURRENCY_FORMAT_COLS:
                    ws.set_column(col_idx, col_idx, 16, currency_fmt)
                elif col_name in ("Impressions", "Clicks", "Orders", "Units"):
                    ws.set_column(col_idx, col_idx, 14, int_fmt)
                elif col_name == "Customer Search Term":
                    ws.set_column(col_idx, col_idx, 35, text_fmt)
                elif "Campaign" in col_name or "Portfolio" in col_name:
                    ws.set_column(col_idx, col_idx, 40, text_fmt)
                elif "Ad Group" in col_name:
                    ws.set_column(col_idx, col_idx, 30, text_fmt)
                else:
                    ws.set_column(col_idx, col_idx, 16, text_fmt)

            ws.autofilter(0, 0, len(df), len(df.columns) - 1)
            ws.freeze_panes(1, 0)

            if cat == "Wasted Adspend" and "Spend" in df.columns:
                spend_col = list(df.columns).index("Spend")
                ws.conditional_format(1, spend_col, len(df), spend_col, {
                    "type": "data_bar",
                    "bar_color": "#C00000",
                })
            elif cat == "Inefficient Adspend" and "ACOS" in df.columns:
                acos_col = list(df.columns).index("ACOS")
                ws.conditional_format(1, acos_col, len(df), acos_col, {
                    "type": "data_bar",
                    "bar_color": "#ED7D31",
                })
            elif cat == "Scaling Opportunity" and "Conversion Rate" in df.columns:
                cvr_col = list(df.columns).index("Conversion Rate")
                ws.conditional_format(1, cvr_col, len(df), cvr_col, {
                    "type": "data_bar",
                    "bar_color": "#00B050",
                })
            elif cat == "Harvesting Opportunity" and "Orders" in df.columns:
                orders_col = list(df.columns).index("Orders")
                ws.conditional_format(1, orders_col, len(df), orders_col, {
                    "type": "data_bar",
                    "bar_color": "#4472C4",
                })

    if output_path is None:
        buffer.seek(0)
        return buffer.read()
    return output_path
