"""Integration tests for chat component with charts.

Tests the integration between chat responses and chart generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import pandas as pd

# Mock Streamlit and visualization dependencies before imports
sys.modules['streamlit'] = MagicMock()
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()
sys.modules['plotly.express'] = MagicMock()
sys.modules['streamlit_echarts'] = MagicMock()
sys.modules['streamlit_plotly_events'] = MagicMock()


class TestChatChartIntegration:
    """Test integration between chat and chart generation."""

    def test_detect_chart_intent_from_chat_query(self):
        """Test that chart intent is detected from chat queries."""
        from utils.chart_generator import detect_chart_intent

        # Simulate chat queries that should trigger charts
        queries = [
            ("Show revenue chart for top companies", True),
            ("Create a visualization of sector distribution", True),
            ("What is the total revenue?", False),
            ("Display pie chart of market share", True),
        ]

        for query, expected_wants_chart in queries:
            result = detect_chart_intent(query)
            if expected_wants_chart:
                assert result["wants_chart"] is True or result["confidence"] >= 0.5
            else:
                assert result["wants_chart"] is False or result["confidence"] < 0.5

    def test_chart_generation_from_query_result(self):
        """Test chart generation from query result DataFrame."""
        from utils.chart_generator import generate_chart_from_data, detect_chart_intent

        # Create sample DataFrame result
        df = pd.DataFrame({
            "company_name": ["Company A", "Company B", "Company C"],
            "sector": ["Banks", "Energy", "Retail"],
            "revenue": [1000000, 2000000, 1500000],
            "net_profit": [100000, 200000, 150000]
        })

        # Detect intent
        intent = detect_chart_intent("Show sunburst chart of revenue by sector")
        assert intent["chart_type"] == "sunburst"

        # Generate chart (mocked)
        with patch('utils.chart_generator.create_sector_sunburst') as mock_chart:
            mock_chart.return_value = Mock()
            fig = generate_chart_from_data(df, intent["chart_type"], {"metrics": ["revenue"]})
            # Chart function should be called or return valid figure
            assert mock_chart.called or fig is not None

    def test_chart_suggestions_for_financial_data(self):
        """Test that appropriate chart suggestions are made for financial data."""
        from utils.chart_generator import get_chart_suggestions

        # Income statement data
        income_df = pd.DataFrame({
            "company_name": ["A"],
            "revenue": [1000000],
            "gross_profit": [400000],
            "net_profit": [200000]
        })

        suggestions = get_chart_suggestions(income_df)
        types = [s["type"] for s in suggestions]
        assert "waterfall" in types

        # Multi-year data
        trend_df = pd.DataFrame({
            "company_name": ["A", "A", "A"],
            "fiscal_year": [2022, 2023, 2024],
            "revenue": [800000, 900000, 1000000]
        })

        suggestions = get_chart_suggestions(trend_df)
        types = [s["type"] for s in suggestions]
        assert "trend" in types
        assert "yoy" in types

    def test_parameter_extraction_from_query(self):
        """Test that parameters are correctly extracted from queries."""
        from utils.chart_generator import extract_chart_parameters

        # Test year extraction
        params = extract_chart_parameters("Compare revenue 2023 vs 2024")
        assert 2023 in params.get("years", [])
        assert 2024 in params.get("years", [])

        # Test top N extraction
        params = extract_chart_parameters("Show top 10 companies")
        assert params.get("top_n") == 10

        # Test metric extraction
        params = extract_chart_parameters("Show ROE by sector")
        assert "roe" in params.get("metrics", [])


class TestChatResponseFormatting:
    """Test chat response formatting for different response types."""

    def test_dataframe_response_detection(self):
        """Test detection of DataFrame responses."""
        # DataFrame should be detected as dataframe type
        df = pd.DataFrame({"a": [1, 2, 3]})

        # Simulate response type detection logic
        response_type = "dataframe" if isinstance(df, pd.DataFrame) else "text"
        assert response_type == "dataframe"

    def test_chart_response_handling(self):
        """Test handling of chart type responses."""
        # Mock chart figure
        mock_fig = Mock()
        mock_fig.data = [Mock()]

        # Chart responses should be identified
        response_type = "chart" if hasattr(mock_fig, 'data') else "unknown"
        assert response_type == "chart"

    def test_text_response_formatting(self):
        """Test text response formatting."""
        response = "The total revenue is SAR 1,000,000"

        # Text responses should remain as text
        response_type = "text" if isinstance(response, str) else "other"
        assert response_type == "text"


class TestChartTabIntegration:
    """Test the Charts tab functionality in chat responses."""

    def test_quick_chart_buttons_configuration(self):
        """Test that quick chart buttons are properly configured."""
        # Expected quick chart options
        expected_charts = ["bar", "pie", "line", "sunburst", "heatmap"]

        # Verify chart types are valid
        from utils.chart_generator import CHART_KEYWORDS
        for chart_type in expected_charts:
            # Each type should either be in keywords or be a basic type
            assert chart_type in CHART_KEYWORDS or chart_type in ["bar", "pie", "line"]

    def test_advanced_chart_suggestions(self):
        """Test advanced chart suggestions based on data."""
        from utils.chart_generator import get_chart_suggestions

        # Financial statement data
        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"],
            "revenue": [1000, 2000],
            "total_assets": [5000, 8000],
            "total_liabilities": [3000, 5000],
            "roe": [15.5, 18.2]
        })

        suggestions = get_chart_suggestions(df)

        # Should suggest multiple chart types
        assert len(suggestions) >= 3

        # Each suggestion should have required fields
        for suggestion in suggestions:
            assert "type" in suggestion
            assert "description" in suggestion


class TestChartErrorHandling:
    """Test error handling in chart generation."""

    def test_invalid_chart_type_handling(self):
        """Test handling of invalid chart types."""
        from utils.chart_generator import generate_chart_from_data

        df = pd.DataFrame({"a": [1, 2, 3]})

        # Invalid chart type should return None
        result = generate_chart_from_data(df, "nonexistent_chart", {})
        assert result is None

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        from utils.chart_generator import generate_chart_from_data, get_chart_suggestions

        empty_df = pd.DataFrame()

        # Should handle gracefully
        suggestions = get_chart_suggestions(empty_df)
        assert isinstance(suggestions, list)

    def test_none_dataframe_handling(self):
        """Test handling of None DataFrame."""
        from utils.chart_generator import generate_chart_from_data, get_chart_suggestions

        # None DataFrame should be handled
        result = generate_chart_from_data(None, "sunburst", {})
        assert result is None

        suggestions = get_chart_suggestions(None)
        assert suggestions == []

    def test_missing_columns_handling(self):
        """Test handling when expected columns are missing."""
        from utils.chart_generator import generate_chart_from_data

        # DataFrame without required columns
        df = pd.DataFrame({"random_col": [1, 2, 3]})

        # Should handle gracefully without crashing
        with patch('utils.chart_generator.create_sector_sunburst') as mock_chart:
            mock_chart.return_value = None
            result = generate_chart_from_data(df, "sunburst", {})
            # Should not crash, may return None


class TestExportFunctionality:
    """Test data export functionality from chat."""

    def test_csv_export_format(self):
        """Test CSV export formatting."""
        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "revenue": [1000000, 2000000]
        })

        # Convert to CSV
        csv_data = df.to_csv(index=False)

        # Verify CSV format
        assert "company_name" in csv_data
        assert "revenue" in csv_data
        assert "1000000" in csv_data

    def test_excel_export_compatibility(self):
        """Test Excel export compatibility."""
        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "revenue": [1000000, 2000000]
        })

        # Test that to_excel method exists
        assert hasattr(df, 'to_excel')


class TestChatHistoryWithCharts:
    """Test chat history handling with chart responses."""

    def test_chart_in_history(self):
        """Test that chart responses can be stored in history."""
        # Simulate chat history entry
        history_entry = {
            "query": "Show sunburst chart",
            "response_type": "chart",
            "chart_type": "sunburst",
            "timestamp": "2024-01-01 12:00:00"
        }

        # History entry should be serializable
        import json
        serialized = json.dumps(history_entry)
        deserialized = json.loads(serialized)

        assert deserialized["response_type"] == "chart"
        assert deserialized["chart_type"] == "sunburst"

    def test_dataframe_in_history(self):
        """Test that DataFrame metadata can be stored in history."""
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4, 5, 6]
        })

        # Store metadata, not the full DataFrame
        history_entry = {
            "query": "Show data",
            "response_type": "dataframe",
            "row_count": len(df),
            "columns": list(df.columns)
        }

        import json
        serialized = json.dumps(history_entry)
        deserialized = json.loads(serialized)

        assert deserialized["row_count"] == 3
        assert "a" in deserialized["columns"]
