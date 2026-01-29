# tests/test_integration.py
"""Integration tests for the full data pipeline."""

import pandas as pd
import pytest
from pathlib import Path


def test_parquet_files_exist():
    """All required parquet files should exist."""
    data_dir = Path(__file__).parent.parent / "data"

    required_files = [
        "analytics_view.parquet",
        "facts_numeric.parquet",
        "filings.parquet",
        "ratios.parquet"
    ]

    for f in required_files:
        assert (data_dir / f).exists(), f"Missing file: {f}"


def test_analytics_view_has_required_columns():
    """Analytics view should have required columns."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "analytics_view.parquet")

    required_columns = [
        'company_name', 'fiscal_year', 'revenue', 'net_profit',
        'total_assets', 'roe', 'current_ratio'
    ]

    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"


def test_no_scientific_notation_in_formatted():
    """Formatted values should not contain scientific notation."""
    from utils.data_processing import format_sar_abbreviated

    test_values = [1e12, 1e9, 1e6, 1e3, 100]

    for val in test_values:
        formatted = format_sar_abbreviated(val)
        assert 'e+' not in formatted.lower(), f"Scientific notation found in {formatted}"


def test_ratios_have_expected_structure():
    """Ratios file should have expected structure."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "ratios.parquet")

    required_columns = ['filing_id', 'ratio', 'value']
    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"


def test_format_dataframe_preserves_row_count():
    """Formatting should not change row count."""
    from utils.data_processing import format_dataframe_for_display

    df = pd.DataFrame({
        'revenue': [1e9, 2e9, 3e9],
        'roe': [0.1, 0.2, 0.3],
        'company': ['A', 'B', 'C']
    })

    formatted = format_dataframe_for_display(df, normalize=False, format_values=True)

    assert len(formatted) == len(df), "Formatting changed row count"


def test_format_dataframe_formats_currency():
    """Currency columns should be formatted with SAR prefix."""
    from utils.data_processing import format_dataframe_for_display

    df = pd.DataFrame({
        'revenue': [1_500_000_000],
        'company': ['Test Co']
    })

    formatted = format_dataframe_for_display(df, normalize=False, format_values=True)

    # Revenue should contain SAR
    assert 'SAR' in str(formatted['revenue'].iloc[0])
