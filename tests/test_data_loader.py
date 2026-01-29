"""Tests for data loader utility."""

import pytest
import pandas as pd
from pathlib import Path


def test_load_data_returns_dict():
    """Test that load_data returns a dictionary of dataframes."""
    from utils.data_loader import load_data

    result = load_data()

    assert isinstance(result, dict)
    assert "filings" in result
    assert "facts" in result
    assert "ratios" in result
    assert "analytics" in result


def test_load_data_returns_dataframes():
    """Test that all returned values are DataFrames."""
    from utils.data_loader import load_data

    result = load_data()

    for key, value in result.items():
        assert isinstance(value, pd.DataFrame), f"{key} is not a DataFrame"


def test_get_dataset_returns_correct_data():
    """Test that get_dataset returns the correct dataset."""
    from utils.data_loader import get_dataset, load_data

    all_data = load_data()

    for name in ["filings", "facts", "ratios", "analytics"]:
        result = get_dataset(name)
        assert result.equals(all_data[name])


def test_get_dataset_info_returns_stats():
    """Test that get_dataset_info returns dataset statistics."""
    from utils.data_loader import get_dataset_info

    info = get_dataset_info()

    assert "companies" in info
    assert "periods" in info
    assert "metrics" in info
    assert "ratios" in info
    assert all(isinstance(v, int) for v in info.values())


def test_get_data_path_returns_path():
    """Test that get_data_path returns a Path object."""
    from utils.data_loader import get_data_path

    path = get_data_path()

    assert isinstance(path, Path)
    assert "data" in str(path)


def test_get_dataset_invalid_name():
    """Test that get_dataset raises error for invalid name."""
    from utils.data_loader import get_dataset

    with pytest.raises(ValueError) as exc_info:
        get_dataset("invalid_name")

    assert "invalid" in str(exc_info.value).lower()


def test_get_column_info_returns_dict():
    """Test that get_column_info returns column information."""
    from utils.data_loader import get_column_info

    info = get_column_info("analytics")

    assert "columns" in info
    assert "dtypes" in info
    assert isinstance(info["columns"], list)
    assert isinstance(info["dtypes"], dict)


def test_get_column_info_facts_has_metrics():
    """Test that facts dataset includes metrics info."""
    from utils.data_loader import get_column_info

    info = get_column_info("facts")

    assert "metrics" in info
    assert isinstance(info["metrics"], list)


def test_get_column_info_ratios_has_ratio_names():
    """Test that ratios dataset includes ratio names."""
    from utils.data_loader import get_column_info

    info = get_column_info("ratios")

    assert "ratio_names" in info
    assert isinstance(info["ratio_names"], list)


def test_dataset_display_names_defined():
    """Test that dataset display names are defined."""
    from utils.data_loader import DATASET_DISPLAY_NAMES

    assert "analytics" in DATASET_DISPLAY_NAMES
    assert "filings" in DATASET_DISPLAY_NAMES
    assert "facts" in DATASET_DISPLAY_NAMES
    assert "ratios" in DATASET_DISPLAY_NAMES


def test_get_dataset_display_name():
    """Test getting display name for dataset."""
    from utils.data_loader import get_dataset_display_name

    name = get_dataset_display_name("analytics")

    assert "Analytics" in name or "analytics" in name.lower()


def test_get_dataset_display_name_unknown():
    """Test getting display name for unknown dataset."""
    from utils.data_loader import get_dataset_display_name

    name = get_dataset_display_name("unknown")

    assert name == "unknown"


def test_analytics_dataset_has_expected_columns():
    """Test that analytics dataset has key columns."""
    from utils.data_loader import get_dataset

    df = get_dataset("analytics")

    # Should have company info and financial metrics
    assert len(df.columns) > 0


def test_filings_dataset_has_company_name():
    """Test that filings dataset has company_name column."""
    from utils.data_loader import get_dataset

    df = get_dataset("filings")

    assert "company_name" in df.columns


def test_facts_dataset_has_metric_column():
    """Test that facts dataset has metric column."""
    from utils.data_loader import get_dataset

    df = get_dataset("facts")

    assert "metric" in df.columns


def test_ratios_dataset_has_ratio_column():
    """Test that ratios dataset has ratio column."""
    from utils.data_loader import get_dataset

    df = get_dataset("ratios")

    assert "ratio" in df.columns
