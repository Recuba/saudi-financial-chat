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
