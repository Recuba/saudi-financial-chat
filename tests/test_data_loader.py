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
