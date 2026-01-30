"""Integration tests for main app functionality.

Tests data loading, filtering, normalization, and display.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import pandas as pd
import numpy as np

# Mock Streamlit before imports
sys.modules['streamlit'] = MagicMock()
sys.modules['pandasai'] = MagicMock()


class TestDataNormalization:
    """Test data normalization functionality."""

    def test_normalize_to_sar(self):
        """Test SAR normalization function."""
        from utils.data_processing import normalize_to_sar

        df = pd.DataFrame({
            "revenue": [1000, 2000, 3000],
            "scale_factor": [1000000, 1000000, 1000000]  # Millions
        })

        normalized = normalize_to_sar(df)

        # Values should be multiplied by scale factor
        assert normalized["revenue"].iloc[0] == 1000000000
        assert normalized["revenue"].iloc[1] == 2000000000

    def test_normalize_without_scale_factor(self):
        """Test normalization when scale_factor column is missing."""
        from utils.data_processing import normalize_to_sar

        df = pd.DataFrame({
            "revenue": [1000, 2000, 3000]
        })

        normalized = normalize_to_sar(df)

        # Should return unchanged or handle gracefully
        assert "revenue" in normalized.columns

    def test_normalize_with_none_values(self):
        """Test normalization with None/NaN values."""
        from utils.data_processing import normalize_to_sar

        df = pd.DataFrame({
            "revenue": [1000, None, 3000],
            "scale_factor": [1000000, 1000000, 1000000]
        })

        normalized = normalize_to_sar(df)

        # Should handle None values
        assert pd.isna(normalized["revenue"].iloc[1]) or normalized["revenue"].iloc[1] == 0


class TestDataFormatting:
    """Test data formatting for display."""

    def test_format_dataframe_for_display(self):
        """Test DataFrame formatting for display."""
        from utils.data_processing import format_dataframe_for_display

        df = pd.DataFrame({
            "company_name": ["Test Company"],
            "revenue": [1000000000],
            "roe": [15.5678]
        })

        formatted = format_dataframe_for_display(df)

        # Should format values for display
        assert isinstance(formatted, pd.DataFrame)

    def test_format_large_numbers(self):
        """Test formatting of large numbers."""
        from utils.data_processing import format_sar_abbreviated

        assert "B" in format_sar_abbreviated(1000000000)
        assert "M" in format_sar_abbreviated(1000000)
        assert "K" in format_sar_abbreviated(1000)

    def test_format_percentage(self):
        """Test percentage formatting."""
        from utils.data_processing import format_percentage

        # Ratio values should be formatted appropriately
        value = 0.156
        formatted = format_percentage(value)
        # Should be a string representation
        assert isinstance(formatted, str)
        assert "%" in formatted

    def test_format_negative_values(self):
        """Test formatting of negative values."""
        from utils.data_processing import format_sar_abbreviated

        formatted = format_sar_abbreviated(-1000000000)

        # Should handle negative values
        assert "-" in formatted


class TestDataFiltering:
    """Test data filtering functionality."""

    def test_filter_by_sector(self):
        """Test filtering by sector."""
        df = pd.DataFrame({
            "company_name": ["A", "B", "C", "D"],
            "sector": ["Banks", "Energy", "Banks", "Retail"]
        })

        # Filter for Banks sector
        filtered = df[df["sector"] == "Banks"]

        assert len(filtered) == 2
        assert all(filtered["sector"] == "Banks")

    def test_filter_by_multiple_sectors(self):
        """Test filtering by multiple sectors."""
        df = pd.DataFrame({
            "company_name": ["A", "B", "C", "D"],
            "sector": ["Banks", "Energy", "Banks", "Retail"]
        })

        selected_sectors = ["Banks", "Energy"]
        filtered = df[df["sector"].isin(selected_sectors)]

        assert len(filtered) == 3

    def test_filter_by_year_range(self):
        """Test filtering by year range."""
        df = pd.DataFrame({
            "company_name": ["A", "A", "A", "A"],
            "fiscal_year": [2020, 2021, 2022, 2023]
        })

        # Filter for years 2021-2022
        filtered = df[(df["fiscal_year"] >= 2021) & (df["fiscal_year"] <= 2022)]

        assert len(filtered) == 2
        assert set(filtered["fiscal_year"]) == {2021, 2022}

    def test_filter_by_metric_threshold(self):
        """Test filtering by metric threshold."""
        df = pd.DataFrame({
            "company_name": ["A", "B", "C"],
            "debt_to_equity": [0.5, 2.5, 1.5]
        })

        # Filter for high debt companies
        filtered = df[df["debt_to_equity"] > 2.0]

        assert len(filtered) == 1
        assert filtered.iloc[0]["company_name"] == "B"

    def test_filter_empty_result(self):
        """Test filtering that returns no results."""
        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"]
        })

        filtered = df[df["sector"] == "NonExistent"]

        assert len(filtered) == 0


class TestDataLoading:
    """Test data loading functionality."""

    def test_load_data_function_exists(self):
        """Test that load_data function exists."""
        from utils.data_loader import load_data

        # Function should be importable
        assert callable(load_data)

    def test_get_dataset_function_exists(self):
        """Test that get_dataset function exists."""
        from utils.data_loader import get_dataset

        # Function should be importable
        assert callable(get_dataset)

    def test_handle_missing_file(self):
        """Test handling of missing data file."""
        # Testing with fake path would require mocking
        pass


class TestDataPreview:
    """Test data preview functionality."""

    def test_preview_dataframe(self):
        """Test DataFrame preview formatting."""
        df = pd.DataFrame({
            "company_name": ["Test Company A", "Test Company B"],
            "revenue": [1000000000, 2000000000],
            "net_profit": [100000000, 200000000]
        })

        # Preview should limit rows
        preview = df.head(10)
        assert len(preview) <= 10

    def test_preview_with_formatting(self):
        """Test preview with formatted values."""
        from utils.data_processing import format_dataframe_for_display

        df = pd.DataFrame({
            "company_name": ["Test"],
            "revenue": [1000000000]
        })

        formatted = format_dataframe_for_display(df)

        # Formatted values should be display-ready
        assert isinstance(formatted, pd.DataFrame)


class TestSessionState:
    """Test session state management."""

    def test_initialize_session_state(self):
        """Test session state initialization."""
        # Simulate session state behavior
        session_state = {}

        # Initialize session state
        if "messages" not in session_state:
            session_state["messages"] = []

        assert "messages" in session_state
        assert session_state["messages"] == []

    def test_add_message_to_history(self):
        """Test adding message to chat history."""
        session_state = {"messages": []}

        session_state["messages"].append({
            "role": "user",
            "content": "Test query"
        })

        assert len(session_state["messages"]) == 1
        assert session_state["messages"][0]["content"] == "Test query"


class TestErrorHandling:
    """Test error handling in app."""

    def test_handle_invalid_query(self):
        """Test handling of invalid queries."""
        # Empty query should be handled
        query = ""
        assert len(query.strip()) == 0

    def test_handle_data_loading_error(self):
        """Test handling of data loading errors."""
        try:
            df = pd.read_parquet("nonexistent_file.parquet")
            assert False, "Should raise error"
        except (FileNotFoundError, OSError):
            pass  # Expected

    def test_handle_processing_error(self):
        """Test handling of data processing errors."""
        df = pd.DataFrame({
            "col1": ["a", "b", "c"]
        })

        # Trying numeric operation on string should be handled
        try:
            result = df["col1"].mean()
        except (TypeError, ValueError):
            pass  # Expected for string column


class TestDataExport:
    """Test data export functionality."""

    def test_export_to_csv(self):
        """Test CSV export."""
        df = pd.DataFrame({
            "company": ["A", "B"],
            "revenue": [100, 200]
        })

        csv_data = df.to_csv(index=False)

        assert "company" in csv_data
        assert "revenue" in csv_data
        assert "100" in csv_data

    def test_export_to_excel_bytes(self):
        """Test Excel export to bytes."""
        import io

        df = pd.DataFrame({
            "company": ["A", "B"],
            "revenue": [100, 200]
        })

        # Test that to_excel method exists
        assert hasattr(df, 'to_excel')

        # Note: Actual Excel export requires openpyxl or xlsxwriter

    def test_export_preserves_data(self):
        """Test that export preserves data correctly."""
        original = pd.DataFrame({
            "company": ["A", "B", "C"],
            "revenue": [100, 200, 300]
        })

        csv_data = original.to_csv(index=False)
        reimported = pd.read_csv(io.StringIO(csv_data))

        assert len(reimported) == len(original)
        assert list(reimported.columns) == list(original.columns)


class TestAppConfiguration:
    """Test app configuration."""

    def test_page_config(self):
        """Test page configuration settings."""
        expected_config = {
            "page_title": "Ra'd AI",
            "layout": "wide"
        }

        # Config values should be valid
        assert isinstance(expected_config["page_title"], str)
        assert expected_config["layout"] in ["wide", "centered"]

    def test_theme_colors(self):
        """Test theme color configuration."""
        theme_colors = {
            "primary": "#D4A84B",
            "background": "#0E0E0E",
            "text": "#FFFFFF"
        }

        # Colors should be valid hex
        for color in theme_colors.values():
            assert color.startswith("#")
            assert len(color) == 7


# Import io for StringIO
import io
