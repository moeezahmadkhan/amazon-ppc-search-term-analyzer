"""
Step 1 validation: loads the dummy SPSTR CSV, runs all 4 filters
with hardcoded thresholds, and prints the resulting dataframes.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.analyzer import SearchTermAnalyzer
from tests.generate_dummy_data import generate

THRESHOLDS = {
    "click_threshold": 10,
    "acos_threshold": 0.30,
    "cvr_threshold": 0.10,
    "low_click_threshold": 10,
    "order_threshold": 2,
}

SEPARATOR = "=" * 80


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "dummy_spstr.csv")
    if not os.path.exists(csv_path):
        print("Generating dummy data...")
        generate(csv_path)

    analyzer = SearchTermAnalyzer()
    df = analyzer.load_data(csv_path)

    print(SEPARATOR)
    print(f"LOADED {len(df)} rows  |  Columns: {list(df.columns)}")
    print(SEPARATOR)

    results = analyzer.analyze(THRESHOLDS)

    total_flagged = 0
    for category, data in results.items():
        count = len(data)
        total_flagged += count
        print(f"\n{SEPARATOR}")
        print(f"  {category.upper()}  ({count} rows)")
        print(SEPARATOR)

        if count == 0:
            print("  (no rows matched)")
            continue

        print(data.to_string(index=False, max_rows=10))

        print(f"\n  -- Stats --")
        for col in ["Clicks", "Spend", "Orders", "ACOS", "Conversion Rate"]:
            if col in data.columns:
                print(f"    {col:>20s}  avg={data[col].mean():.4f}  sum={data[col].sum():.2f}")

    print(f"\n{SEPARATOR}")
    print(f"TOTAL FLAGGED: {total_flagged} / {len(df)} rows")
    print(SEPARATOR)


if __name__ == "__main__":
    main()
