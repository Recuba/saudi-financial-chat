"""Tests for sidebar component."""

import pytest


def test_sidebar_css_prevents_truncation():
    """Test that CSS includes truncation prevention rules."""
    from styles.css import get_base_css

    css = get_base_css()

    # Verify truncation prevention CSS rules are present
    assert "white-space: nowrap" in css
    assert "overflow: visible" in css
    assert "text-overflow: clip" in css


def test_get_dataset_info_keys():
    """Test that dataset info has expected keys."""
    from utils.data_loader import get_dataset_info

    info = get_dataset_info()

    assert "companies" in info
    assert "periods" in info
    assert "metrics" in info
    assert "ratios" in info


def test_database_info_can_be_collapsed():
    """Test that database info section supports collapse."""
    from components.sidebar import render_database_info
    import inspect

    source = inspect.getsource(render_database_info)

    # Function should use expander for collapsible behavior
    assert "expander" in source.lower()


def test_dataset_descriptions_exist():
    """Test that all datasets have descriptions."""
    from components.sidebar import DATASET_DESCRIPTIONS
    from utils.data_loader import DATASET_DISPLAY_NAMES

    for dataset_key in DATASET_DISPLAY_NAMES.keys():
        assert dataset_key in DATASET_DESCRIPTIONS
        assert len(DATASET_DESCRIPTIONS[dataset_key]) > 10


def test_get_dataset_quick_stats():
    """Test getting quick stats for a dataset."""
    from components.sidebar import get_dataset_quick_stats

    stats = get_dataset_quick_stats("analytics")

    assert "rows" in stats
    assert "columns" in stats
    assert isinstance(stats["rows"], int)
    assert isinstance(stats["columns"], int)
