"""Tests for data preview component."""

import pytest
import pandas as pd


def test_get_preview_columns_returns_list():
    """Test that preview columns returns a list."""
    from components.data_preview import get_preview_columns

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "revenue": [100, 200],
        "sector": ["Tech", "Finance"],
        "metric": ["X", "Y"],
    })

    result = get_preview_columns(df, max_cols=3)

    assert isinstance(result, list)
    assert len(result) <= 3


def test_get_preview_columns_prioritizes_key_columns():
    """Test that key columns are prioritized."""
    from components.data_preview import get_preview_columns, KEY_COLUMNS

    df = pd.DataFrame({
        "company_name": ["A"],
        "xyz": [1],
        "revenue": [100],
        "abc": [2],
    })

    result = get_preview_columns(df, max_cols=2)

    # Should include company_name as it's a key column
    assert "company_name" in result


def test_format_preview_dataframe():
    """Test that preview dataframe is formatted correctly."""
    from components.data_preview import format_preview_dataframe

    df = pd.DataFrame({
        "company_name": ["Company A", "Company B"],
        "revenue": [1000000, 2000000],
    })

    result = format_preview_dataframe(df, max_rows=1)

    assert len(result) == 1
