"""Tests for advanced filters component."""

import pytest
import pandas as pd


def test_get_available_sectors():
    """Test getting unique sectors from data."""
    from components.filters.advanced_filters import get_available_sectors

    df = pd.DataFrame({
        "sector": ["Tech", "Finance", "Tech", "Healthcare"]
    })

    sectors = get_available_sectors(df)

    assert isinstance(sectors, list)
    assert len(sectors) == 3
    assert "Tech" in sectors


def test_get_year_range():
    """Test getting year range from data."""
    from components.filters.advanced_filters import get_year_range

    df = pd.DataFrame({
        "fiscal_year": [2020, 2021, 2022, 2023]
    })

    min_year, max_year = get_year_range(df)

    assert min_year == 2020
    assert max_year == 2023


def test_apply_filters():
    """Test applying filters to dataframe."""
    from components.filters.advanced_filters import apply_filters

    df = pd.DataFrame({
        "sector": ["Tech", "Finance", "Tech"],
        "fiscal_year": [2022, 2022, 2023],
        "company_name": ["A", "B", "C"]
    })

    filters = {
        "sectors": ["Tech"],
        "years": [2022, 2023],
    }

    filtered = apply_filters(df, filters)

    assert len(filtered) == 2
    assert all(filtered["sector"] == "Tech")
