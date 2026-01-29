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
        # Fill NaN scale factors with 1 to avoid propagating NaN
        scale = result[scale_column].fillna(1)
        result[col] = result[col] * scale

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

    # Check against module constants first
    if col_lower in [c.lower() for c in CURRENCY_COLUMNS]:
        return 'currency'

    if col_lower in [c.lower() for c in RATIO_COLUMNS]:
        # Some ratios are percentages (stored as decimals)
        if col_lower in ['roe', 'roa', 'gross_margin', 'net_margin', 'operating_margin']:
            return 'percentage'
        return 'ratio'

    # Fallback keyword matching for unlisted columns
    if any(kw in col_lower for kw in ['revenue', 'profit', 'asset', 'equity', 'liability', 'cash', 'expense', 'sar']):
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
        for col in result.columns:
            col_type = get_column_type(col)

            if col_type == 'currency':
                if currency_column in result.columns:
                    # Format with per-row currency
                    result[col] = result.apply(
                        lambda row, c=col: format_currency_value(
                            row[c],
                            'SAR' if 'Riyal' in str(row.get(currency_column, '')) else
                            'USD' if 'Dollar' in str(row.get(currency_column, '')) else 'SAR'
                        ),
                        axis=1
                    )
                else:
                    result[col] = result[col].apply(
                        lambda x: format_currency_value(x, 'SAR')
                    )
            elif col_type == 'percentage':
                result[col] = result[col].apply(format_percentage)
            elif col_type == 'ratio':
                result[col] = result[col].apply(format_ratio)

    return result


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
            format_dict[col] = lambda x, c=col: format_sar_abbreviated(x) if pd.notna(x) else '-'
        elif col_type == 'percentage':
            format_dict[col] = lambda x, c=col: format_percentage(x) if pd.notna(x) else '-'
        elif col_type == 'ratio':
            format_dict[col] = lambda x, c=col: format_ratio(x) if pd.notna(x) else '-'

    # Apply formatting
    return df.style.format(format_dict, na_rep='-')
