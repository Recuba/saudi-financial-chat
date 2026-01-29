# Saudi Financial Data Fix & Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix data accuracy issues, normalize scale factors, and integrate proper number formatting into the Streamlit app display pipeline.

**Architecture:** Create a data processing layer (`utils/data_processing.py`) that normalizes all values to SAR at scale 1 during load, then integrate existing formatting functions from `components/tables/metrics.py` into the app's display pipeline. Fix dataframe height constraints and add currency indicators.

**Tech Stack:** Python, Pandas, Parquet, Streamlit

---

## Problem Summary

1. **Only 9 companies visible** - Streamlit's default dataframe height truncates display
2. **Raw unformatted numbers** - Values show as `14373754325000` instead of `SAR 14.4B`
3. **Scale factor inconsistency** - 67% scale=1, 32% scale=1000, 1% scale=1000000 (stored mixed, not normalized)
4. **Inaccurate rankings** - Mixed scales cause Arabian Contracting (small company) to appear as #1 by revenue
5. **Currency mismatch** - Both SAR and USD data mixed without distinction

---

## Task 1: Create Data Normalization Utility

**Files:**
- Create: `utils/__init__.py`
- Create: `utils/data_processing.py`
- Test: `tests/test_data_processing.py`

**Step 1: Write the failing test**

```python
# tests/test_data_processing.py
import pytest
import pandas as pd
from utils.data_processing import normalize_to_sar

def test_normalize_scale_1():
    """Values with scale_factor=1 should remain unchanged."""
    df = pd.DataFrame({
        'revenue': [1000000.0],
        'scale_factor': [1]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_scale_1000():
    """Values with scale_factor=1000 should be multiplied by 1000."""
    df = pd.DataFrame({
        'revenue': [1000.0],
        'scale_factor': [1000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_scale_1000000():
    """Values with scale_factor=1000000 should be multiplied by 1000000."""
    df = pd.DataFrame({
        'revenue': [1.0],
        'scale_factor': [1000000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_handles_null():
    """Null values should remain null after normalization."""
    df = pd.DataFrame({
        'revenue': [None],
        'scale_factor': [1000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert pd.isna(result['revenue'].iloc[0])
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_data_processing.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'utils'"

**Step 3: Write minimal implementation**

```python
# utils/__init__.py
"""Utility functions for Saudi Financial Chat."""
from .data_processing import normalize_to_sar, format_dataframe_for_display

__all__ = ['normalize_to_sar', 'format_dataframe_for_display']
```

```python
# utils/data_processing.py
"""
Data Processing Utilities for Saudi Financial Chat.

Handles scale factor normalization and value formatting for display.
"""

from __future__ import annotations
from typing import List, Optional
import pandas as pd


# Currency columns that need scale normalization
CURRENCY_COLUMNS = [
    'revenue', 'net_profit', 'gross_profit', 'operating_profit',
    'total_assets', 'total_equity', 'total_liabilities',
    'current_assets', 'current_liabilities', 'inventory',
    'receivables', 'capex', 'interest_expense', 'cost_of_sales',
    'operating_cash_flow', 'fcf', 'value_sar'
]

# Ratio columns (already normalized, no scale adjustment needed)
RATIO_COLUMNS = [
    'roe', 'roa', 'gross_margin', 'net_margin', 'operating_margin',
    'current_ratio', 'quick_ratio', 'debt_to_equity', 'debt_to_assets',
    'interest_coverage', 'asset_turnover', 'inventory_turnover',
    'receivables_days', 'cash_conversion', 'ocf_to_current_liabilities'
]


def normalize_to_sar(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    scale_column: str = 'scale_factor'
) -> pd.DataFrame:
    """
    Normalize currency values to SAR at scale=1.

    Args:
        df: DataFrame with financial data
        columns: Columns to normalize (defaults to CURRENCY_COLUMNS)
        scale_column: Column containing scale factor

    Returns:
        DataFrame with normalized values
    """
    result = df.copy()
    cols_to_normalize = columns or [c for c in CURRENCY_COLUMNS if c in df.columns]

    if scale_column not in result.columns:
        return result

    for col in cols_to_normalize:
        if col not in result.columns:
            continue
        # Multiply value by scale_factor to get actual SAR amount
        result[col] = result[col] * result[scale_column]

    return result


def get_column_type(column_name: str) -> str:
    """
    Detect column type for formatting.

    Args:
        column_name: Name of the column

    Returns:
        'currency', 'percentage', 'ratio', or 'text'
    """
    col_lower = column_name.lower()

    # Check for ratio columns (percentages stored as decimals)
    if col_lower in ['roe', 'roa', 'gross_margin', 'net_margin', 'operating_margin']:
        return 'percentage'

    # Check for ratio columns (displayed with 'x')
    if col_lower in ['current_ratio', 'quick_ratio', 'debt_to_equity', 'debt_to_assets',
                     'interest_coverage', 'asset_turnover', 'inventory_turnover']:
        return 'ratio'

    # Check for currency columns
    if col_lower in CURRENCY_COLUMNS or any(kw in col_lower for kw in
        ['revenue', 'profit', 'asset', 'equity', 'liability', 'cash', 'expense', 'sar']):
        return 'currency'

    return 'text'


def format_sar_abbreviated(value: float) -> str:
    """
    Format a SAR value with K/M/B abbreviations.

    Args:
        value: Numeric value in SAR

    Returns:
        Formatted string like 'SAR 1.5B'
    """
    if pd.isna(value):
        return '-'

    abs_val = abs(value)

    if abs_val >= 1e12:
        return f'SAR {value / 1e12:.1f}T'
    elif abs_val >= 1e9:
        return f'SAR {value / 1e9:.1f}B'
    elif abs_val >= 1e6:
        return f'SAR {value / 1e6:.1f}M'
    elif abs_val >= 1e3:
        return f'SAR {value / 1e3:.1f}K'
    else:
        return f'SAR {value:,.0f}'


def format_percentage(value: float) -> str:
    """
    Format a decimal value as percentage.

    Args:
        value: Decimal value (0.25 = 25%)

    Returns:
        Formatted string like '25.0%'
    """
    if pd.isna(value):
        return '-'
    return f'{value * 100:.1f}%'


def format_ratio(value: float) -> str:
    """
    Format a ratio value.

    Args:
        value: Ratio value

    Returns:
        Formatted string like '2.15x'
    """
    if pd.isna(value):
        return '-'
    return f'{value:.2f}x'


def format_dataframe_for_display(
    df: pd.DataFrame,
    normalize: bool = True,
    format_values: bool = True
) -> pd.DataFrame:
    """
    Prepare a DataFrame for display with normalization and formatting.

    Args:
        df: Raw DataFrame from parquet
        normalize: Apply scale factor normalization
        format_values: Apply value formatting

    Returns:
        Display-ready DataFrame
    """
    result = df.copy()

    # Step 1: Normalize scale factors
    if normalize and 'scale_factor' in result.columns:
        result = normalize_to_sar(result)

    # Step 2: Format values for display
    if format_values:
        for col in result.columns:
            col_type = get_column_type(col)

            if col_type == 'currency':
                result[col] = result[col].apply(format_sar_abbreviated)
            elif col_type == 'percentage':
                result[col] = result[col].apply(format_percentage)
            elif col_type == 'ratio':
                result[col] = result[col].apply(format_ratio)

    return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_data_processing.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add utils/__init__.py utils/data_processing.py tests/test_data_processing.py
git commit -m "$(cat <<'EOF'
feat: add data normalization utility for scale factors

- Add normalize_to_sar() to multiply values by scale_factor
- Add format functions for SAR, percentage, and ratio values
- Add format_dataframe_for_display() for display pipeline

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Add Formatting Tests

**Files:**
- Modify: `tests/test_data_processing.py`

**Step 1: Write the failing tests**

```python
# Add to tests/test_data_processing.py
from utils.data_processing import (
    format_sar_abbreviated,
    format_percentage,
    format_ratio,
    get_column_type
)

class TestFormatSarAbbreviated:
    def test_billions(self):
        assert format_sar_abbreviated(1_500_000_000) == 'SAR 1.5B'

    def test_millions(self):
        assert format_sar_abbreviated(2_500_000) == 'SAR 2.5M'

    def test_thousands(self):
        assert format_sar_abbreviated(5_500) == 'SAR 5.5K'

    def test_small_values(self):
        assert format_sar_abbreviated(500) == 'SAR 500'

    def test_negative(self):
        assert format_sar_abbreviated(-1_500_000_000) == 'SAR -1.5B'

    def test_null(self):
        assert format_sar_abbreviated(None) == '-'

class TestFormatPercentage:
    def test_positive(self):
        assert format_percentage(0.25) == '25.0%'

    def test_negative(self):
        assert format_percentage(-0.10) == '-10.0%'

    def test_null(self):
        assert format_percentage(None) == '-'

class TestFormatRatio:
    def test_normal(self):
        assert format_ratio(2.15) == '2.15x'

    def test_null(self):
        assert format_ratio(None) == '-'

class TestGetColumnType:
    def test_currency_column(self):
        assert get_column_type('revenue') == 'currency'
        assert get_column_type('net_profit') == 'currency'

    def test_percentage_column(self):
        assert get_column_type('roe') == 'percentage'
        assert get_column_type('gross_margin') == 'percentage'

    def test_ratio_column(self):
        assert get_column_type('current_ratio') == 'ratio'
        assert get_column_type('debt_to_equity') == 'ratio'

    def test_unknown_column(self):
        assert get_column_type('company_name') == 'text'
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_data_processing.py -v`
Expected: PASS (all tests)

**Step 3: Commit**

```bash
git add tests/test_data_processing.py
git commit -m "$(cat <<'EOF'
test: add comprehensive formatting function tests

- Test SAR abbreviation for B/M/K/small values
- Test percentage and ratio formatting
- Test column type detection

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Create Normalized Parquet Files

**Files:**
- Create: `scripts/normalize_parquet.py`
- Modify: `data/analytics_view.parquet` (regenerated)
- Modify: `data/facts_numeric.parquet` (regenerated)

**Step 1: Write the normalization script**

```python
# scripts/normalize_parquet.py
"""
Script to normalize parquet files with consistent scale factors.

Run: python scripts/normalize_parquet.py
"""

import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processing import CURRENCY_COLUMNS


def normalize_analytics_view(input_path: Path, output_path: Path) -> None:
    """Normalize analytics_view.parquet."""
    print(f"Processing {input_path}...")
    df = pd.read_parquet(input_path)

    print(f"  Original rows: {len(df)}")
    print(f"  Scale factor distribution:")
    print(df['scale_factor'].value_counts())

    # Normalize currency columns
    for col in CURRENCY_COLUMNS:
        if col in df.columns:
            df[col] = df[col] * df['scale_factor']

    # Set scale_factor to 1 (all now normalized)
    df['scale_factor'] = 1

    # Save
    df.to_parquet(output_path, index=False)
    print(f"  Saved to {output_path}")


def normalize_facts_numeric(input_path: Path, output_path: Path, filings_path: Path) -> None:
    """Normalize facts_numeric.parquet using filing scale factors."""
    print(f"Processing {input_path}...")
    df = pd.read_parquet(input_path)
    filings = pd.read_parquet(filings_path)

    print(f"  Original rows: {len(df)}")

    # Merge scale_factor from filings
    df = df.merge(
        filings[['filing_id', 'scale_factor']],
        on='filing_id',
        how='left'
    )

    # Normalize value_sar
    df['value_sar'] = df['value_sar'] * df['scale_factor'].fillna(1)

    # Drop scale_factor column
    df = df.drop(columns=['scale_factor'])

    # Save
    df.to_parquet(output_path, index=False)
    print(f"  Saved to {output_path}")


def main():
    data_dir = Path(__file__).parent.parent / "data"
    backup_dir = data_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    # Backup originals
    print("Creating backups...")
    for f in ['analytics_view.parquet', 'facts_numeric.parquet']:
        src = data_dir / f
        if src.exists():
            import shutil
            shutil.copy(src, backup_dir / f)
            print(f"  Backed up {f}")

    # Normalize
    normalize_analytics_view(
        data_dir / "analytics_view.parquet",
        data_dir / "analytics_view.parquet"
    )

    normalize_facts_numeric(
        data_dir / "facts_numeric.parquet",
        data_dir / "facts_numeric.parquet",
        data_dir / "filings.parquet"
    )

    print("\nDone! Original files backed up to data/backup/")


if __name__ == "__main__":
    main()
```

**Step 2: Run the normalization script**

Run: `python scripts/normalize_parquet.py`
Expected: Files normalized with output showing scale factor distribution

**Step 3: Verify normalization worked**

Run: `python -c "import pandas as pd; df = pd.read_parquet('data/analytics_view.parquet'); print(df['scale_factor'].value_counts())"`
Expected: All rows show scale_factor=1

**Step 4: Commit**

```bash
git add scripts/normalize_parquet.py data/backup/
git commit -m "$(cat <<'EOF'
feat: add parquet normalization script

- Create backup of original files
- Normalize all currency values to scale_factor=1
- Preserve original data in data/backup/

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Fix Data Preview Height

**Files:**
- Modify: `app.py:329-337`

**Step 1: Read current implementation**

Current code at line 337:
```python
st.dataframe(dataset_map[dataset_choice].head(10), use_container_width=True)
```

**Step 2: Update dataframe display with explicit height**

```python
# app.py:329-337 - Replace the expander content
with st.expander("📄 Data Preview", expanded=False):
    filings, facts, ratios, analytics = load_data()
    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }
    st.dataframe(
        dataset_map[dataset_choice].head(10),
        use_container_width=True,
        height=400  # Explicit height to show all 10 rows
    )
```

**Step 3: Test locally**

Run: `streamlit run app.py`
Expected: Data preview shows all 10 rows instead of 9

**Step 4: Commit**

```bash
git add app.py
git commit -m "$(cat <<'EOF'
fix: set explicit dataframe height to show all 10 rows

Streamlit's default dataframe height truncated display to 9 rows.
Adding height=400 ensures all 10 preview rows are visible.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Integrate Formatting into Data Loading

**Files:**
- Modify: `app.py:271-279`

**Step 1: Read current load_data function**

Current code:
```python
@st.cache_data
def load_data():
    base_path = Path(__file__).parent / "data"
    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")
    return filings, facts, ratios, analytics
```

**Step 2: Add import at top of file**

Add after line 14:
```python
from utils.data_processing import normalize_to_sar
```

**Step 3: Update load_data to normalize values**

```python
@st.cache_data
def load_data():
    """Load and normalize financial data from parquet files."""
    base_path = Path(__file__).parent / "data"

    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")

    # Normalize scale factors if not already normalized
    if 'scale_factor' in analytics.columns and (analytics['scale_factor'] != 1).any():
        analytics = normalize_to_sar(analytics)

    return filings, facts, ratios, analytics
```

**Step 4: Test locally**

Run: `streamlit run app.py`
Expected: No errors on load, data values are normalized

**Step 5: Commit**

```bash
git add app.py
git commit -m "$(cat <<'EOF'
feat: integrate scale factor normalization into data loading

- Import normalize_to_sar utility
- Normalize analytics view if scale factors are mixed
- Values now consistent for accurate comparisons

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Create Display Formatting Helper

**Files:**
- Modify: `utils/data_processing.py`

**Step 1: Add pandas Styler formatting function**

Add to end of `utils/data_processing.py`:

```python
def create_styled_dataframe(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """
    Create a styled DataFrame with proper number formatting.

    Args:
        df: DataFrame to style

    Returns:
        Styled DataFrame ready for st.dataframe()
    """
    # Build format dict based on column types
    format_dict = {}

    for col in df.columns:
        col_type = get_column_type(col)

        if col_type == 'currency':
            # Use lambda with default arg to capture value
            format_dict[col] = lambda x: format_sar_abbreviated(x) if pd.notna(x) else '-'
        elif col_type == 'percentage':
            format_dict[col] = lambda x: format_percentage(x) if pd.notna(x) else '-'
        elif col_type == 'ratio':
            format_dict[col] = lambda x: format_ratio(x) if pd.notna(x) else '-'

    # Apply formatting
    return df.style.format(format_dict, na_rep='-')
```

**Step 2: Add test**

Add to `tests/test_data_processing.py`:

```python
from utils.data_processing import create_styled_dataframe

def test_create_styled_dataframe():
    """Styled dataframe should return Styler object."""
    df = pd.DataFrame({
        'revenue': [1_000_000_000],
        'roe': [0.25],
        'current_ratio': [1.5]
    })
    styled = create_styled_dataframe(df)
    assert isinstance(styled, pd.io.formats.style.Styler)
```

**Step 3: Run tests**

Run: `pytest tests/test_data_processing.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add utils/data_processing.py tests/test_data_processing.py
git commit -m "$(cat <<'EOF'
feat: add create_styled_dataframe for pandas Styler formatting

- Apply SAR/percentage/ratio formatting via pandas Styler
- Returns Styler compatible with st.dataframe()

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Integrate Formatting into Chat Response Display

**Files:**
- Modify: `app.py:388-416`

**Step 1: Add import**

Add to imports section:
```python
from utils.data_processing import format_dataframe_for_display
```

**Step 2: Update chat response handling**

Replace lines 391-394:
```python
if response.type == 'dataframe':
    tabResult, tabCode = st.tabs(["Result", "Code"])
    with tabResult:
        st.dataframe(response.value, use_container_width=True, hide_index=True)
```

With:
```python
if response.type == 'dataframe':
    tabResult, tabCode = st.tabs(["Result", "Code"])
    with tabResult:
        # Format the dataframe for display
        display_df = format_dataframe_for_display(
            response.value,
            normalize=False,  # Already normalized at load
            format_values=True
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
```

**Step 3: Test locally**

Run: `streamlit run app.py`
Test query: "Top 10 companies by revenue 2024"
Expected: Revenue values display as "SAR 243.6B" not "243630000000"

**Step 4: Commit**

```bash
git add app.py
git commit -m "$(cat <<'EOF'
feat: apply formatting to chat response dataframes

- Format currency values as SAR with B/M/K abbreviations
- Format percentages and ratios appropriately
- Display is now human-readable

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Add Currency Column to Output

**Files:**
- Modify: `utils/data_processing.py`

**Step 1: Update format_sar_abbreviated to handle currency parameter**

```python
def format_currency_value(value: float, currency: str = 'SAR') -> str:
    """
    Format a currency value with K/M/B abbreviations.

    Args:
        value: Numeric value
        currency: Currency code (SAR, USD)

    Returns:
        Formatted string like 'SAR 1.5B' or 'USD 1.5B'
    """
    if pd.isna(value):
        return '-'

    abs_val = abs(value)

    if abs_val >= 1e12:
        return f'{currency} {value / 1e12:.1f}T'
    elif abs_val >= 1e9:
        return f'{currency} {value / 1e9:.1f}B'
    elif abs_val >= 1e6:
        return f'{currency} {value / 1e6:.1f}M'
    elif abs_val >= 1e3:
        return f'{currency} {value / 1e3:.1f}K'
    else:
        return f'{currency} {value:,.0f}'
```

**Step 2: Update format_dataframe_for_display to use currency column**

```python
def format_dataframe_for_display(
    df: pd.DataFrame,
    normalize: bool = True,
    format_values: bool = True,
    currency_column: str = 'currency'
) -> pd.DataFrame:
    """
    Prepare a DataFrame for display with normalization and formatting.

    Args:
        df: Raw DataFrame from parquet
        normalize: Apply scale factor normalization
        format_values: Apply value formatting
        currency_column: Column containing currency code

    Returns:
        Display-ready DataFrame
    """
    result = df.copy()

    # Step 1: Normalize scale factors
    if normalize and 'scale_factor' in result.columns:
        result = normalize_to_sar(result)

    # Step 2: Format values for display
    if format_values:
        # Determine default currency
        default_currency = 'SAR'

        for col in result.columns:
            col_type = get_column_type(col)

            if col_type == 'currency':
                if currency_column in result.columns:
                    # Format with per-row currency
                    result[col] = result.apply(
                        lambda row: format_currency_value(
                            row[col],
                            'SAR' if 'Riyal' in str(row.get(currency_column, '')) else
                            'USD' if 'Dollar' in str(row.get(currency_column, '')) else 'SAR'
                        ),
                        axis=1
                    )
                else:
                    result[col] = result[col].apply(
                        lambda x: format_currency_value(x, default_currency)
                    )
            elif col_type == 'percentage':
                result[col] = result[col].apply(format_percentage)
            elif col_type == 'ratio':
                result[col] = result[col].apply(format_ratio)

    return result
```

**Step 3: Add test**

```python
def test_format_currency_value_usd():
    from utils.data_processing import format_currency_value
    assert format_currency_value(1_000_000, 'USD') == 'USD 1.0M'
```

**Step 4: Run tests**

Run: `pytest tests/test_data_processing.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add utils/data_processing.py tests/test_data_processing.py
git commit -m "$(cat <<'EOF'
feat: add currency-aware formatting (SAR/USD)

- format_currency_value accepts currency parameter
- format_dataframe_for_display checks currency column
- USD values now display correctly

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Verify Data Accuracy

**Files:**
- Create: `scripts/verify_data_accuracy.py`

**Step 1: Write verification script**

```python
# scripts/verify_data_accuracy.py
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

    print("Top 10 Companies by Revenue (2024):")
    print("-" * 60)

    top_revenue = df_2024.nlargest(10, 'revenue')[
        ['company_name', 'revenue', 'sector']
    ]

    for i, row in top_revenue.iterrows():
        rev_b = row['revenue'] / 1e9
        print(f"{row['company_name'][:40]:<40} SAR {rev_b:>8.1f}B  ({row['sector']})")

    print("\n" + "-" * 60)
    print("Verification checklist:")
    print("- Saudi Aramco should be #1 (>400B SAR)")
    print("- Saudi Telecom should be in top 10")
    print("- Saudi Electricity should be in top 10")
    print("- Arabian Contracting should NOT be in top 10")

if __name__ == "__main__":
    main()
```

**Step 2: Run verification**

Run: `python scripts/verify_data_accuracy.py`
Expected: Saudi Aramco at top, not Arabian Contracting

**Step 3: Commit**

```bash
git add scripts/verify_data_accuracy.py
git commit -m "$(cat <<'EOF'
chore: add data accuracy verification script

- Lists top 10 companies by revenue for 2024
- Provides checklist for manual verification
- Confirms normalization fixed ranking issues

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Update Data Preview with Formatting

**Files:**
- Modify: `app.py:329-337`

**Step 1: Update data preview to use formatted display**

```python
# Show data preview
with st.expander("📄 Data Preview", expanded=False):
    filings, facts, ratios, analytics = load_data()
    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }

    # Format for display
    preview_df = format_dataframe_for_display(
        dataset_map[dataset_choice].head(10),
        normalize=False,  # Already normalized at load
        format_values=True
    )

    st.dataframe(
        preview_df,
        use_container_width=True,
        height=400
    )
```

**Step 2: Test locally**

Run: `streamlit run app.py`
Expected: Data preview shows formatted values (SAR 1.5B, 25.0%, 2.15x)

**Step 3: Commit**

```bash
git add app.py
git commit -m "$(cat <<'EOF'
feat: apply formatting to data preview

- Currency values show as SAR with abbreviations
- Percentages display with % symbol
- Ratios display with x suffix

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Final Integration Test

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

```python
# tests/test_integration.py
"""Integration tests for the full data pipeline."""

import pandas as pd
import pytest
from pathlib import Path

def test_analytics_view_normalized():
    """All analytics values should be at scale_factor=1."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "analytics_view.parquet")

    # Check scale factor is 1
    if 'scale_factor' in df.columns:
        assert (df['scale_factor'] == 1).all(), "Not all rows have scale_factor=1"

def test_top_revenue_is_aramco():
    """Saudi Aramco should be the top company by revenue."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "analytics_view.parquet")

    # Filter to most recent year with data
    latest_year = df['fiscal_year'].max()
    df_latest = df[df['fiscal_year'] == latest_year]

    top_company = df_latest.nlargest(1, 'revenue')['company_name'].iloc[0]

    assert 'Aramco' in top_company or 'aramco' in top_company.lower(), \
        f"Top company is {top_company}, expected Saudi Aramco"

def test_no_scientific_notation_in_formatted():
    """Formatted values should not contain scientific notation."""
    from utils.data_processing import format_sar_abbreviated

    test_values = [1e12, 1e9, 1e6, 1e3, 100]

    for val in test_values:
        formatted = format_sar_abbreviated(val)
        assert 'e+' not in formatted.lower(), f"Scientific notation found in {formatted}"

def test_ratios_file_unchanged():
    """Ratios file should not be modified (already normalized decimals)."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "ratios.parquet")

    # Check typical ratio values are in expected range
    if 'value' in df.columns:
        # Most ratios should be between -10 and 10
        in_range = ((df['value'] > -100) & (df['value'] < 100)).mean()
        assert in_range > 0.95, "Ratio values appear out of expected range"
```

**Step 2: Run integration tests**

Run: `pytest tests/test_integration.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "$(cat <<'EOF'
test: add integration tests for data pipeline

- Verify scale factor normalization
- Verify top revenue company is Saudi Aramco
- Verify no scientific notation in formatted output
- Verify ratios file integrity

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Summary

After completing all tasks:

1. **Scale factors normalized** - All currency values now at scale=1
2. **Formatting integrated** - SAR 1.5B format instead of 1500000000
3. **Data preview fixed** - Shows all 10 rows
4. **Accurate rankings** - Saudi Aramco correctly at top, not Arabian Contracting
5. **Currency-aware** - SAR and USD values distinguished
6. **Tests in place** - Unit and integration tests verify correctness

## Quick Verification Commands

```bash
# Run all tests
pytest tests/ -v

# Verify data normalization
python scripts/verify_data_accuracy.py

# Start app and test queries
streamlit run app.py
```
