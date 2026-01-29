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
