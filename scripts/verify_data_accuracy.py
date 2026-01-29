"""
Script to verify data accuracy after normalization.

Compares top companies by revenue to known public data.
"""

import pandas as pd
from pathlib import Path


def main():
    data_dir = Path(__file__).parent.parent / "data"
    analytics = pd.read_parquet(data_dir / "analytics_view.parquet")

    # Filter to 2024 data
    df_2024 = analytics[analytics['fiscal_year'] == 2024].copy()

    print("=" * 70)
    print("Top 10 Companies by Revenue (2024)")
    print("=" * 70)

    top_revenue = df_2024.nlargest(10, 'revenue')[
        ['company_name', 'revenue', 'sector']
    ]

    for idx, (i, row) in enumerate(top_revenue.iterrows(), 1):
        rev_b = row['revenue'] / 1e9
        name = row['company_name'][:40]
        print(f"{idx:2}. {name:<40} SAR {rev_b:>8.1f}B  ({row['sector']})")

    print("\n" + "=" * 70)
    print("Verification Checklist:")
    print("=" * 70)

    # Check if Saudi Aramco is #1 (official name: Saudi Arabian Oil Co.)
    top_company = top_revenue['company_name'].iloc[0]
    top_lower = top_company.lower()
    if 'aramco' in top_lower or 'saudi arabian oil' in top_lower:
        print("[PASS] Saudi Aramco (Saudi Arabian Oil Co.) is #1 by revenue")
    else:
        print(f"[FAIL] Top company is '{top_company}', expected Saudi Aramco")

    # Check Arabian Contracting is NOT in top 10
    top_names = top_revenue['company_name'].str.lower().tolist()
    if any('arabian contracting' in name for name in top_names):
        print("[FAIL] Arabian Contracting is in top 10 (data not normalized)")
    else:
        print("[PASS] Arabian Contracting is NOT in top 10 (as expected)")

    # Check scale factor
    if 'scale_factor' in analytics.columns:
        unique_scales = analytics['scale_factor'].unique()
        if len(unique_scales) == 1 and unique_scales[0] == 1:
            print("[PASS] All scale_factor values are 1 (normalized)")
        else:
            print(f"[FAIL] Scale factors not normalized: {unique_scales}")
    else:
        print("[INFO] No scale_factor column present")

    print("=" * 70)


if __name__ == "__main__":
    main()
