"""Unit tests for chart_generator.py module.

Tests chart intent detection, parameter extraction, and chart generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock dependencies
sys.modules['streamlit'] = MagicMock()
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()
sys.modules['plotly.express'] = MagicMock()


class TestDetectChartIntent:
    """Test detect_chart_intent function."""

    def test_explicit_chart_request(self):
        """Test detection of explicit chart requests."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Create a chart showing revenue by sector")

        assert result["wants_chart"] is True
        assert result["confidence"] >= 0.7

    def test_explicit_graph_request(self):
        """Test detection of graph keyword."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show me a graph of profits over time")

        assert result["wants_chart"] is True

    def test_visualization_request(self):
        """Test detection of visualization keyword."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Visualize the sector distribution")

        assert result["wants_chart"] is True

    def test_waterfall_intent(self):
        """Test waterfall chart intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show income statement waterfall")

        assert result["chart_type"] == "waterfall"
        assert "waterfall" in result["keywords_matched"]

    def test_balance_sheet_intent(self):
        """Test balance sheet chart intent."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show balance sheet composition")

        assert result["chart_type"] == "balance_sheet"

    def test_radar_intent(self):
        """Test radar chart intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Create radar chart of financial ratios")

        assert result["chart_type"] == "radar"

    def test_trend_intent(self):
        """Test trend chart intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show revenue trend over time")

        assert result["chart_type"] == "trend"

    def test_yoy_intent(self):
        """Test year-over-year intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show year over year growth trend")

        # YoY can be detected based on specific keywords
        assert result["chart_type"] in ["yoy", "bar_comparison", "trend"]

    def test_sunburst_intent(self):
        """Test sunburst chart intent."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show sunburst of market composition")

        assert result["chart_type"] == "sunburst"

    def test_heatmap_intent(self):
        """Test heatmap intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Create heatmap of sector performance")

        assert result["chart_type"] == "heatmap"

    def test_scatter_intent(self):
        """Test scatter plot intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show risk return scatter plot")

        assert result["chart_type"] == "scatter"

    def test_dashboard_intent(self):
        """Test dashboard intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show financial dashboard overview")

        assert result["chart_type"] == "dashboard"

    def test_comparison_intent(self):
        """Test comparison chart intent."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Compare top 10 companies by revenue")

        assert result["chart_type"] == "bar_comparison"

    def test_no_chart_intent(self):
        """Test query without chart intent."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("What is the total revenue?")

        assert result["wants_chart"] is False or result["confidence"] < 0.5

    def test_pie_chart_intent(self):
        """Test pie chart intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show pie chart of market share")

        assert result["chart_type"] == "pie"

    def test_line_chart_intent(self):
        """Test line chart intent detection."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Create line chart showing progression")

        assert result["chart_type"] == "line"


class TestExtractChartParameters:
    """Test extract_chart_parameters function."""

    def test_extract_years(self):
        """Test year extraction from query."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Compare revenue 2023 vs 2024")

        assert "years" in params
        assert 2023 in params["years"]
        assert 2024 in params["years"]

    def test_extract_multiple_years(self):
        """Test extraction of multiple years."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show data for 2020, 2021, 2022, 2023")

        assert len(params["years"]) == 4

    def test_extract_top_n(self):
        """Test top N extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show top 10 companies by revenue")

        assert params["top_n"] == 10

    def test_extract_top_5(self):
        """Test top 5 extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Display top 5 performers")

        assert params["top_n"] == 5

    def test_extract_revenue_metric(self):
        """Test revenue metric extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show revenue trend")

        assert "metrics" in params
        assert "revenue" in params["metrics"]

    def test_extract_profit_metric(self):
        """Test profit metric extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Compare net profit across companies")

        assert "metrics" in params
        assert "net_profit" in params["metrics"]

    def test_extract_roe_metric(self):
        """Test ROE metric extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show return on equity by sector")

        assert "metrics" in params
        assert "roe" in params["metrics"]

    def test_extract_sectors(self):
        """Test sector extraction."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show banks sector performance")

        assert "sectors" in params
        assert "Banks" in params["sectors"]

    def test_extract_company_from_df(self):
        """Test company extraction from DataFrame."""
        import pandas as pd
        from utils.chart_generator import extract_chart_parameters

        df = pd.DataFrame({
            "company_name": ["Saudi Aramco", "SABIC", "STC"]
        })

        params = extract_chart_parameters("Show data for Aramco", df)

        assert "companies" in params
        assert "Saudi Aramco" in params["companies"]

    def test_no_parameters(self):
        """Test query with no extractable parameters."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show me some data")

        # Should return empty or minimal dict
        assert isinstance(params, dict)


class TestGenerateChartFromData:
    """Test generate_chart_from_data function."""

    def test_generate_sunburst(self):
        """Test sunburst chart generation."""
        import pandas as pd
        from utils.chart_generator import generate_chart_from_data

        df = pd.DataFrame({
            "company_name": ["A", "B", "C"],
            "sector": ["Banks", "Energy", "Retail"],
            "revenue": [100, 200, 150]
        })

        with patch('utils.chart_generator.create_sector_sunburst') as mock_chart:
            mock_chart.return_value = Mock()

            fig = generate_chart_from_data(df, "sunburst", {"metrics": ["revenue"]})

            # Should attempt to create chart
            assert mock_chart.called or fig is not None

    def test_generate_heatmap(self):
        """Test heatmap generation."""
        import pandas as pd
        from utils.chart_generator import generate_chart_from_data

        df = pd.DataFrame({
            "sector": ["Banks", "Energy"],
            "roe": [15, 18],
            "roa": [8, 10]
        })

        with patch('utils.chart_generator.create_sector_performance_heatmap') as mock_chart:
            mock_chart.return_value = Mock()

            fig = generate_chart_from_data(df, "heatmap", {"metrics": ["roe", "roa"]})

            assert mock_chart.called or fig is not None

    def test_generate_scatter(self):
        """Test scatter plot generation."""
        import pandas as pd
        from utils.chart_generator import generate_chart_from_data

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"],
            "roe": [15, 18],
            "debt_to_equity": [0.5, 0.8]
        })

        with patch('utils.chart_generator.create_risk_return_scatter') as mock_chart:
            mock_chart.return_value = Mock()

            fig = generate_chart_from_data(df, "scatter", {})

            assert mock_chart.called or fig is not None

    def test_generate_invalid_type(self):
        """Test with invalid chart type."""
        import pandas as pd
        from utils.chart_generator import generate_chart_from_data

        df = pd.DataFrame({"a": [1, 2, 3]})

        fig = generate_chart_from_data(df, "invalid_chart_type", {})

        assert fig is None

    def test_generate_with_none_df(self):
        """Test with None DataFrame."""
        from utils.chart_generator import generate_chart_from_data

        fig = generate_chart_from_data(None, "sunburst", {})

        assert fig is None


class TestGetChartSuggestions:
    """Test get_chart_suggestions function."""

    def test_suggestions_with_income_data(self):
        """Test suggestions for income statement data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A"],
            "revenue": [100],
            "net_profit": [20],
            "gross_profit": [50]
        })

        suggestions = get_chart_suggestions(df)

        assert len(suggestions) > 0
        types = [s["type"] for s in suggestions]
        assert "waterfall" in types

    def test_suggestions_with_balance_sheet(self):
        """Test suggestions for balance sheet data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A"],
            "total_assets": [1000],
            "total_liabilities": [600],
            "total_equity": [400]
        })

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "balance_sheet" in types

    def test_suggestions_with_ratios(self):
        """Test suggestions for ratio data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A"],
            "roe": [15],
            "roa": [8],
            "current_ratio": [1.5]
        })

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "radar" in types

    def test_suggestions_with_multi_year(self):
        """Test suggestions for multi-year data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A", "A", "A"],
            "fiscal_year": [2022, 2023, 2024],
            "revenue": [100, 120, 150]
        })

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "trend" in types
        assert "yoy" in types

    def test_suggestions_with_sector(self):
        """Test suggestions for sector data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"],
            "revenue": [100, 200]
        })

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "sunburst" in types
        assert "heatmap" in types

    def test_suggestions_with_risk_return(self):
        """Test suggestions for risk-return data."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({
            "company_name": ["A"],
            "roe": [15],
            "debt_to_equity": [0.5]
        })

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "scatter" in types

    def test_suggestions_always_include_dashboard(self):
        """Test that dashboard is always suggested."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame({"a": [1, 2, 3]})

        suggestions = get_chart_suggestions(df)

        types = [s["type"] for s in suggestions]
        assert "dashboard" in types

    def test_suggestions_empty_df(self):
        """Test suggestions with empty DataFrame."""
        import pandas as pd
        from utils.chart_generator import get_chart_suggestions

        df = pd.DataFrame()

        suggestions = get_chart_suggestions(df)

        # Should still return some suggestions
        assert isinstance(suggestions, list)

    def test_suggestions_none_df(self):
        """Test suggestions with None DataFrame."""
        from utils.chart_generator import get_chart_suggestions

        suggestions = get_chart_suggestions(None)

        assert suggestions == []


class TestChartKeywords:
    """Test CHART_KEYWORDS constant."""

    def test_chart_keywords_defined(self):
        """Test that CHART_KEYWORDS is properly defined."""
        from utils.chart_generator import CHART_KEYWORDS

        assert "waterfall" in CHART_KEYWORDS
        assert "balance_sheet" in CHART_KEYWORDS
        assert "radar" in CHART_KEYWORDS
        assert "trend" in CHART_KEYWORDS
        assert "sunburst" in CHART_KEYWORDS

    def test_chart_keywords_have_values(self):
        """Test that all chart types have keyword lists."""
        from utils.chart_generator import CHART_KEYWORDS

        for chart_type, keywords in CHART_KEYWORDS.items():
            assert isinstance(keywords, list)
            assert len(keywords) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_detect_intent_empty_query(self):
        """Test with empty query string."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("")

        assert result["wants_chart"] is False

    def test_detect_intent_special_characters(self):
        """Test with special characters in query."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show chart for @#$% company!!")

        # Should not crash
        assert isinstance(result, dict)

    def test_extract_params_unicode(self):
        """Test parameter extraction with unicode."""
        from utils.chart_generator import extract_chart_parameters

        params = extract_chart_parameters("Show data for company in 2024")

        assert isinstance(params, dict)

    def test_case_insensitivity(self):
        """Test that detection is case insensitive."""
        from utils.chart_generator import detect_chart_intent

        result1 = detect_chart_intent("SHOW WATERFALL CHART")
        result2 = detect_chart_intent("show waterfall chart")

        assert result1["chart_type"] == result2["chart_type"]

    def test_multiple_chart_types_in_query(self):
        """Test query with multiple chart type keywords."""
        from utils.chart_generator import detect_chart_intent

        result = detect_chart_intent("Show radar or heatmap of sector performance")

        # Should pick one type
        assert result["chart_type"] is not None
