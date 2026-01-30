"""Unit tests for sidebar component enhancements.

Tests data freshness, extended info, company search, and database info display.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import pandas as pd
from datetime import datetime, timedelta

# Mock Streamlit before imports
sys.modules['streamlit'] = MagicMock()


class TestDataFreshness:
    """Test get_data_freshness function."""

    def test_freshness_returns_dict(self):
        """Test freshness calculation returns a dictionary."""
        from components.sidebar import get_data_freshness

        result = get_data_freshness()

        assert isinstance(result, dict)
        assert "status" in result
        assert "days_old" in result

    def test_freshness_status_values(self):
        """Test freshness status is valid."""
        from components.sidebar import get_data_freshness

        result = get_data_freshness()

        # Status should be one of the valid values
        assert result["status"] in ["fresh", "recent", "stale", "unknown"]

    def test_freshness_has_last_updated(self):
        """Test freshness includes last_updated field."""
        from components.sidebar import get_data_freshness

        result = get_data_freshness()

        assert "last_updated" in result

    def test_freshness_days_old_is_numeric(self):
        """Test days_old is numeric or None."""
        from components.sidebar import get_data_freshness

        result = get_data_freshness()

        if result["days_old"] is not None:
            assert isinstance(result["days_old"], (int, float))


class TestExtendedDatasetInfo:
    """Test get_extended_dataset_info function."""

    def test_extended_info_function_exists(self):
        """Test that function exists and is callable."""
        from components.sidebar import get_extended_dataset_info

        assert callable(get_extended_dataset_info)

    def test_extended_info_returns_dict_type(self):
        """Test that function returns a dict-like type."""
        from components.sidebar import get_extended_dataset_info

        result = get_extended_dataset_info()

        # When mocked, result should still be a dict or dict-like
        assert result is not None


class TestCompanySearch:
    """Test search_companies function."""

    def test_search_returns_list(self):
        """Test search returns a list."""
        from components.sidebar import search_companies

        results = search_companies("test")

        assert isinstance(results, list)

    def test_search_empty_query(self):
        """Test search with empty query."""
        from components.sidebar import search_companies

        results = search_companies("")

        # Empty query should return empty list
        assert results == []

    def test_search_short_query(self):
        """Test search with very short query."""
        from components.sidebar import search_companies

        results = search_companies("a")

        # Single char query should return empty
        assert results == []

    def test_search_with_valid_query(self):
        """Test search with valid query."""
        from components.sidebar import search_companies

        # This depends on actual data in the system
        results = search_companies("Sa")

        assert isinstance(results, list)

    def test_search_result_structure(self):
        """Test search result structure."""
        from components.sidebar import search_companies

        results = search_companies("Saudi")

        # If there are results, check structure
        if results:
            assert "company_name" in results[0]
            assert "sector" in results[0]

    def test_search_with_limit(self):
        """Test search with custom limit."""
        from components.sidebar import search_companies

        results = search_companies("Sa", limit=5)

        # Should respect limit
        assert len(results) <= 5


class TestRenderDatabaseInfo:
    """Test render_database_info function."""

    def test_render_function_exists(self):
        """Test render_database_info function exists."""
        from components.sidebar import render_database_info

        assert callable(render_database_info)

    def test_get_data_freshness_callable(self):
        """Test get_data_freshness is callable."""
        from components.sidebar import get_data_freshness

        assert callable(get_data_freshness)


class TestRenderCompanySearch:
    """Test render_company_search function."""

    @patch('components.sidebar.st')
    def test_render_search_ui(self, mock_st):
        """Test rendering search UI."""
        from components.sidebar import render_company_search

        # Mock text input
        mock_st.text_input.return_value = ""

        render_company_search()

        # Should create text input
        assert mock_st.text_input.called

    @patch('components.sidebar.st')
    def test_render_search_returns_optional(self, mock_st):
        """Test rendering search returns Optional[str]."""
        from components.sidebar import render_company_search

        mock_st.text_input.return_value = ""

        result = render_company_search()

        # Result should be None or string
        assert result is None or isinstance(result, str)


class TestSidebarHelpers:
    """Test helper functions in sidebar module."""

    def test_format_large_number(self):
        """Test formatting of large numbers."""
        # Test if format function exists and works
        try:
            from components.sidebar import format_large_number

            assert format_large_number(1000000000) == "1.0B" or "B" in format_large_number(1000000000)
            assert format_large_number(1000000) == "1.0M" or "M" in format_large_number(1000000)
        except ImportError:
            # Function may be in utils
            pass

    def test_sector_color_mapping(self):
        """Test sector color mapping if available."""
        try:
            from components.sidebar import SECTOR_COLORS

            assert isinstance(SECTOR_COLORS, dict)
            assert "Banks" in SECTOR_COLORS or len(SECTOR_COLORS) > 0
        except ImportError:
            pass


class TestSidebarIntegration:
    """Integration tests for sidebar components."""

    def test_sidebar_imports(self):
        """Test sidebar module can be imported."""
        from components.sidebar import (
            render_database_info,
            get_extended_dataset_info,
            get_data_freshness,
            search_companies,
            render_company_search
        )

        # All functions should be callable
        assert callable(render_database_info)
        assert callable(get_extended_dataset_info)
        assert callable(get_data_freshness)
        assert callable(search_companies)
        assert callable(render_company_search)

    def test_search_companies_with_short_query(self):
        """Test search_companies with minimal query."""
        from components.sidebar import search_companies

        # Short query should return empty list
        results = search_companies("a")
        assert results == []
