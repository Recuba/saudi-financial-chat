"""Tests for data loader utility with tasi_optimized views."""

import pytest
import pandas as pd
from pathlib import Path


def test_load_tasi_data_returns_dict():
    """Test that load_tasi_data returns a dictionary with all 7 views."""
    from utils.data_loader import load_tasi_data

    result = load_tasi_data()

    assert isinstance(result, dict)
    assert len(result) == 7
    assert "tasi_financials" in result
    assert "latest_financials" in result
    assert "latest_annual" in result
    assert "ticker_index" in result
    assert "company_annual_timeseries" in result
    assert "sector_benchmarks_latest" in result
    assert "top_bottom_performers" in result


def test_load_tasi_data_returns_dataframes():
    """Test that all returned values are DataFrames."""
    from utils.data_loader import load_tasi_data

    result = load_tasi_data()

    for key, value in result.items():
        assert isinstance(value, pd.DataFrame), f"{key} is not a DataFrame"


def test_get_view_returns_correct_data():
    """Test that get_view returns the same data as load_tasi_data for that view."""
    from utils.data_loader import get_view, load_tasi_data

    all_data = load_tasi_data()

    for name in ["tasi_financials", "latest_financials", "ticker_index"]:
        result = get_view(name)
        assert result.equals(all_data[name]), f"get_view('{name}') mismatch"


def test_get_view_invalid_name():
    """Test that get_view raises error for invalid name."""
    from utils.data_loader import get_view

    with pytest.raises(ValueError) as exc_info:
        get_view("invalid_view_name")

    assert "invalid" in str(exc_info.value).lower()


def test_view_names_constant():
    """Test that VIEW_NAMES contains all 7 view names."""
    from utils.data_loader import VIEW_NAMES

    assert len(VIEW_NAMES) == 7
    assert "tasi_financials" in VIEW_NAMES
    assert "latest_financials" in VIEW_NAMES
    assert "latest_annual" in VIEW_NAMES
    assert "ticker_index" in VIEW_NAMES
    assert "company_annual_timeseries" in VIEW_NAMES
    assert "sector_benchmarks_latest" in VIEW_NAMES
    assert "top_bottom_performers" in VIEW_NAMES


def test_tasi_financials_has_expected_columns():
    """Test that tasi_financials has key columns."""
    from utils.data_loader import get_view

    df = get_view("tasi_financials")

    # Key columns per metadata.json
    assert "ticker" in df.columns
    assert "company_name" in df.columns
    assert "fiscal_year" in df.columns
    assert "revenue" in df.columns
    assert "net_profit" in df.columns


def test_latest_financials_row_count():
    """Test that latest_financials has one row per company (302)."""
    from utils.data_loader import get_view

    df = get_view("latest_financials")

    # Per metadata.json: 302 unique tickers
    assert len(df) == 302


def test_ticker_index_has_required_columns():
    """Test that ticker_index has required columns."""
    from utils.data_loader import get_view

    df = get_view("ticker_index")

    assert "ticker" in df.columns
    assert "company_name" in df.columns
    assert "sector" in df.columns


def test_get_view_info_returns_stats():
    """Test that get_view_info returns dataset statistics."""
    from utils.data_loader import get_view_info

    info = get_view_info()

    assert "total_companies" in info
    assert "total_records" in info
    assert "views_available" in info
    assert info["total_companies"] == 302
    assert info["total_records"] == 4748
    assert info["views_available"] == 7


def test_get_data_path_returns_path():
    """Test that get_data_path returns a Path object."""
    from utils.data_loader import get_data_path

    path = get_data_path()

    assert isinstance(path, Path)
    assert "data" in str(path)


def test_company_annual_timeseries_has_yoy_columns():
    """Test that company_annual_timeseries has YoY growth columns."""
    from utils.data_loader import get_view

    df = get_view("company_annual_timeseries")

    # Should have YoY columns per metadata
    yoy_columns = [col for col in df.columns if "_yoy" in col.lower()]
    assert len(yoy_columns) > 0, "Expected YoY columns in company_annual_timeseries"


def test_sector_benchmarks_latest_has_sectors():
    """Test that sector_benchmarks_latest contains sector data."""
    from utils.data_loader import get_view

    df = get_view("sector_benchmarks_latest")

    assert "sector" in df.columns
    # Per metadata: 6 sectors
    assert len(df) == 6


def test_top_bottom_performers_has_ranking_columns():
    """Test that top_bottom_performers has ranking columns."""
    from utils.data_loader import get_view

    df = get_view("top_bottom_performers")

    # Should have metric and ranking info
    assert "ticker" in df.columns
    assert len(df) > 0


# =============================================================================
# Backward compatibility tests for deprecated functions
# =============================================================================


def test_deprecated_load_data_still_works():
    """Test that deprecated load_data function still returns data."""
    from utils.data_loader import load_data

    result = load_data()

    assert isinstance(result, dict)
    assert "filings" in result
    assert "facts" in result
    assert "ratios" in result
    assert "analytics" in result


def test_deprecated_get_dataset_still_works():
    """Test that deprecated get_dataset function still returns data."""
    from utils.data_loader import get_dataset

    result = get_dataset("analytics")

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_deprecated_get_dataset_info_still_works():
    """Test that deprecated get_dataset_info still returns stats."""
    from utils.data_loader import get_dataset_info

    info = get_dataset_info()

    assert "companies" in info
    assert "periods" in info
    assert isinstance(info["companies"], int)
