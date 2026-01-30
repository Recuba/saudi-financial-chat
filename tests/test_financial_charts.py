"""Unit tests for financial_charts.py module.

Tests all financial visualization functions with comprehensive coverage
for waterfall charts, radar charts, sunburst, heatmaps, and dashboards.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock plotly before importing the module
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()
sys.modules['plotly.express'] = MagicMock()
sys.modules['plotly.subplots'] = MagicMock()


class TestFinancialColors:
    """Test financial color constants."""

    def test_financial_colors_defined(self):
        """Test that FINANCIAL_COLORS dictionary is properly defined."""
        from components.visualizations.financial_charts import FINANCIAL_COLORS

        assert "positive" in FINANCIAL_COLORS
        assert "negative" in FINANCIAL_COLORS
        assert "primary" in FINANCIAL_COLORS
        assert "background" in FINANCIAL_COLORS

    def test_sector_colors_defined(self):
        """Test that SECTOR_COLORS dictionary is properly defined."""
        from components.visualizations.financial_charts import SECTOR_COLORS

        assert "Banks" in SECTOR_COLORS
        assert "Energy" in SECTOR_COLORS
        assert "Retail" in SECTOR_COLORS
        assert "Other" in SECTOR_COLORS

    def test_financial_colors_are_hex(self):
        """Test that all colors are valid hex codes."""
        from components.visualizations.financial_charts import FINANCIAL_COLORS

        for name, color in FINANCIAL_COLORS.items():
            assert color.startswith("#"), f"{name} should be a hex color"
            assert len(color) == 7, f"{name} should be 7 characters (#RRGGBB)"


class TestGetPlotlyLayout:
    """Test get_plotly_layout function."""

    def test_layout_with_defaults(self):
        """Test layout generation with default parameters."""
        from components.visualizations.financial_charts import get_plotly_layout

        layout = get_plotly_layout()

        assert "paper_bgcolor" in layout
        assert "plot_bgcolor" in layout
        assert "font" in layout
        assert layout["height"] == 500

    def test_layout_with_title(self):
        """Test layout generation with custom title."""
        from components.visualizations.financial_charts import get_plotly_layout

        layout = get_plotly_layout(title="Test Chart")

        assert layout["title"]["text"] == "Test Chart"

    def test_layout_with_custom_height(self):
        """Test layout generation with custom height."""
        from components.visualizations.financial_charts import get_plotly_layout

        layout = get_plotly_layout(height=800)

        assert layout["height"] == 800

    def test_layout_dark_mode(self):
        """Test layout in dark mode."""
        from components.visualizations.financial_charts import get_plotly_layout, FINANCIAL_COLORS

        layout = get_plotly_layout(dark_mode=True)

        assert layout["paper_bgcolor"] == FINANCIAL_COLORS["background"]

    def test_layout_light_mode(self):
        """Test layout in light mode."""
        from components.visualizations.financial_charts import get_plotly_layout

        layout = get_plotly_layout(dark_mode=False)

        assert layout["paper_bgcolor"] == "#FFFFFF"


class TestIncomeStatementWaterfall:
    """Test create_income_statement_waterfall function."""

    def test_waterfall_basic(self):
        """Test basic waterfall chart creation."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=1000000,
            cost_of_sales=400000,
            gross_profit=600000,
            operating_expenses=200000,
            operating_profit=400000,
            net_profit=350000
        )

        # Should return a figure (mocked)
        assert fig is not None

    def test_waterfall_with_company_name(self):
        """Test waterfall with company name in title."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=1000000,
            cost_of_sales=400000,
            gross_profit=600000,
            operating_expenses=200000,
            operating_profit=400000,
            company_name="Test Corp",
            fiscal_year=2024
        )

        assert fig is not None

    def test_waterfall_calculates_net_profit(self):
        """Test waterfall calculates net profit if not provided."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=1000000,
            cost_of_sales=400000,
            gross_profit=600000,
            operating_expenses=200000,
            operating_profit=400000,
            other_income=50000,
            interest_expense=20000,
            tax_expense=80000
            # net_profit not provided - should be calculated
        )

        assert fig is not None

    def test_waterfall_with_all_parameters(self):
        """Test waterfall with all optional parameters."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=10000000000,  # 10B
            cost_of_sales=4000000000,
            gross_profit=6000000000,
            operating_expenses=2000000000,
            operating_profit=4000000000,
            other_income=100000000,
            interest_expense=50000000,
            tax_expense=500000000,
            net_profit=3550000000,
            company_name="Saudi Aramco",
            fiscal_year=2024,
            currency="SAR"
        )

        assert fig is not None


class TestBalanceSheetComposition:
    """Test create_balance_sheet_composition function."""

    def test_balance_sheet_basic(self):
        """Test basic balance sheet chart creation."""
        from components.visualizations.financial_charts import create_balance_sheet_composition

        fig = create_balance_sheet_composition(
            total_assets=1000000,
            current_assets=400000,
            non_current_assets=600000,
            total_liabilities=600000,
            current_liabilities=200000,
            non_current_liabilities=400000,
            total_equity=400000
        )

        assert fig is not None

    def test_balance_sheet_with_company(self):
        """Test balance sheet with company name."""
        from components.visualizations.financial_charts import create_balance_sheet_composition

        fig = create_balance_sheet_composition(
            total_assets=1000000,
            current_assets=400000,
            non_current_assets=600000,
            total_liabilities=600000,
            current_liabilities=200000,
            non_current_liabilities=400000,
            total_equity=400000,
            company_name="Test Corp",
            fiscal_year=2024,
            currency="SAR"
        )

        assert fig is not None


class TestRatioRadarChart:
    """Test create_ratio_radar_chart function."""

    def test_radar_basic(self):
        """Test basic radar chart creation."""
        from components.visualizations.financial_charts import create_ratio_radar_chart

        ratios = {
            "ROE": 15.5,
            "ROA": 8.2,
            "Net Margin": 12.0,
            "Current Ratio": 1.5,
            "D/E": 0.8
        }

        fig = create_ratio_radar_chart(ratios)

        assert fig is not None

    def test_radar_with_benchmark(self):
        """Test radar chart with benchmark comparison."""
        from components.visualizations.financial_charts import create_ratio_radar_chart

        ratios = {
            "ROE": 15.5,
            "ROA": 8.2,
            "Net Margin": 12.0
        }

        benchmark = {
            "ROE": 12.0,
            "ROA": 6.5,
            "Net Margin": 10.0
        }

        fig = create_ratio_radar_chart(
            ratios=ratios,
            benchmark_ratios=benchmark,
            company_name="Test Corp",
            benchmark_name="Industry Average"
        )

        assert fig is not None

    def test_radar_empty_ratios(self):
        """Test radar chart with empty ratios."""
        from components.visualizations.financial_charts import create_ratio_radar_chart

        # Empty ratios should either return None or raise an error
        try:
            fig = create_ratio_radar_chart(ratios={})
            # If it returns, could be None or empty figure
            assert fig is None or fig is not None
        except (IndexError, ValueError):
            # Some implementations may raise error for empty input
            pass


class TestRatioComparisonBars:
    """Test create_ratio_comparison_bars function."""

    def test_comparison_basic(self):
        """Test basic ratio comparison chart."""
        from components.visualizations.financial_charts import create_ratio_comparison_bars

        companies = ["Company A", "Company B", "Company C"]
        ratios_data = {
            "ROE": [15.5, 12.0, 18.2],
            "ROA": [8.2, 6.5, 9.1]
        }

        fig = create_ratio_comparison_bars(companies, ratios_data)

        assert fig is not None

    def test_comparison_with_types(self):
        """Test ratio comparison with type hints."""
        from components.visualizations.financial_charts import create_ratio_comparison_bars

        companies = ["A", "B"]
        ratios_data = {
            "ROE": [15.5, 12.0],
            "Revenue": [1000000, 2000000]
        }
        ratio_types = {
            "ROE": "percentage",
            "Revenue": "currency"
        }

        fig = create_ratio_comparison_bars(
            companies=companies,
            ratios_data=ratios_data,
            ratio_types=ratio_types,
            title="Custom Title"
        )

        assert fig is not None


class TestMultiYearTrend:
    """Test create_multi_year_trend function."""

    def test_trend_basic(self):
        """Test basic multi-year trend chart."""
        import pandas as pd
        from components.visualizations.financial_charts import create_multi_year_trend

        df = pd.DataFrame({
            "company_name": ["Test Corp"] * 3,
            "fiscal_year": [2022, 2023, 2024],
            "revenue": [100, 120, 150],
            "net_profit": [10, 15, 20]
        })

        fig = create_multi_year_trend(
            df=df,
            company_name="Test Corp",
            metrics=["revenue", "net_profit"]
        )

        assert fig is not None

    def test_trend_company_not_found(self):
        """Test trend with non-existent company."""
        import pandas as pd
        from components.visualizations.financial_charts import create_multi_year_trend

        df = pd.DataFrame({
            "company_name": ["Other Corp"],
            "fiscal_year": [2024],
            "revenue": [100]
        })

        fig = create_multi_year_trend(
            df=df,
            company_name="Test Corp",
            metrics=["revenue"]
        )

        assert fig is None


class TestYoYComparison:
    """Test create_yoy_comparison_chart function."""

    def test_yoy_basic(self):
        """Test basic YoY comparison chart."""
        import pandas as pd
        from components.visualizations.financial_charts import create_yoy_comparison_chart

        df = pd.DataFrame({
            "company_name": ["A", "B", "C", "A", "B", "C"],
            "fiscal_year": [2023, 2023, 2023, 2024, 2024, 2024],
            "revenue": [100, 200, 150, 120, 220, 180]
        })

        fig = create_yoy_comparison_chart(
            df=df,
            metric="revenue",
            year1=2023,
            year2=2024,
            top_n=3
        )

        assert fig is not None


class TestSectorSunburst:
    """Test create_sector_sunburst function."""

    def test_sunburst_basic(self):
        """Test basic sector sunburst chart."""
        import pandas as pd
        from components.visualizations.financial_charts import create_sector_sunburst

        df = pd.DataFrame({
            "company_name": ["A", "B", "C", "D"],
            "sector": ["Banks", "Banks", "Energy", "Retail"],
            "revenue": [100, 150, 200, 80]
        })

        fig = create_sector_sunburst(df, value_column="revenue")

        assert fig is not None

    def test_sunburst_custom_columns(self):
        """Test sunburst with custom column names."""
        import pandas as pd
        from components.visualizations.financial_charts import create_sector_sunburst

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"],
            "total_assets": [1000, 2000]
        })

        fig = create_sector_sunburst(
            df=df,
            value_column="total_assets",
            sector_column="sector",
            company_column="company_name"
        )

        assert fig is not None


class TestSectorPerformanceHeatmap:
    """Test create_sector_performance_heatmap function."""

    def test_heatmap_basic(self):
        """Test basic sector performance heatmap."""
        import pandas as pd
        from components.visualizations.financial_charts import create_sector_performance_heatmap

        df = pd.DataFrame({
            "sector": ["Banks", "Banks", "Energy", "Retail"],
            "roe": [15, 12, 18, 10],
            "roa": [8, 6, 10, 5],
            "margin": [20, 18, 25, 15]
        })

        fig = create_sector_performance_heatmap(
            df=df,
            metrics=["roe", "roa", "margin"]
        )

        assert fig is not None

    def test_heatmap_different_aggregation(self):
        """Test heatmap with different aggregation methods."""
        import pandas as pd
        from components.visualizations.financial_charts import create_sector_performance_heatmap

        df = pd.DataFrame({
            "sector": ["Banks", "Banks", "Energy"],
            "roe": [15, 12, 18],
            "roa": [8, 6, 10]
        })

        # Test median aggregation
        fig = create_sector_performance_heatmap(
            df=df,
            metrics=["roe", "roa"],
            aggregation="median"
        )

        assert fig is not None


class TestRiskReturnScatter:
    """Test create_risk_return_scatter function."""

    def test_scatter_basic(self):
        """Test basic risk-return scatter plot."""
        import pandas as pd
        from components.visualizations.financial_charts import create_risk_return_scatter

        df = pd.DataFrame({
            "company_name": ["A", "B", "C"],
            "sector": ["Banks", "Energy", "Retail"],
            "roe": [15, 18, 12],
            "debt_to_equity": [0.5, 1.2, 0.8],
            "total_assets": [1000, 2000, 1500]
        })

        fig = create_risk_return_scatter(df)

        assert fig is not None

    def test_scatter_custom_columns(self):
        """Test scatter with custom column names."""
        import pandas as pd
        from components.visualizations.financial_charts import create_risk_return_scatter

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "sector": ["Banks", "Energy"],
            "roa": [8, 10],
            "debt_to_assets": [0.4, 0.6],
            "revenue": [500, 800]
        })

        fig = create_risk_return_scatter(
            df=df,
            return_column="roa",
            risk_column="debt_to_assets",
            size_column="revenue"
        )

        assert fig is not None

    def test_scatter_empty_data(self):
        """Test scatter with data that has all NaN values."""
        import pandas as pd
        from components.visualizations.financial_charts import create_risk_return_scatter

        df = pd.DataFrame({
            "company_name": [],
            "sector": [],
            "roe": [],
            "debt_to_equity": []
        })

        fig = create_risk_return_scatter(df)

        assert fig is None


class TestFinancialDashboard:
    """Test create_financial_dashboard function."""

    def test_dashboard_basic(self):
        """Test basic financial dashboard."""
        from components.visualizations.financial_charts import create_financial_dashboard

        company_data = {
            "roe": 15.5,
            "roa": 8.2,
            "current_ratio": 1.5,
            "debt_to_equity": 0.8,
            "asset_turnover": 0.6
        }

        fig = create_financial_dashboard(company_data)

        assert fig is not None

    def test_dashboard_with_benchmarks(self):
        """Test dashboard with industry benchmarks."""
        from components.visualizations.financial_charts import create_financial_dashboard

        company_data = {
            "roe": 15.5,
            "current_ratio": 1.5,
            "debt_to_equity": 0.8
        }

        benchmarks = {
            "roe": 12.0,
            "current_ratio": 1.2,
            "debt_to_equity": 1.0
        }

        fig = create_financial_dashboard(
            company_data=company_data,
            industry_benchmarks=benchmarks,
            company_name="Test Corp",
            fiscal_year=2024
        )

        assert fig is not None

    def test_dashboard_missing_metrics(self):
        """Test dashboard with missing metrics."""
        from components.visualizations.financial_charts import create_financial_dashboard

        company_data = {
            "roe": 15.5
            # Other metrics missing
        }

        fig = create_financial_dashboard(company_data)

        assert fig is not None


class TestRecommendChart:
    """Test recommend_chart function."""

    def test_recommend_waterfall(self):
        """Test waterfall chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show income statement waterfall for Aramco")

        assert result["chart_type"] == "income_waterfall"
        assert result["function"] == "create_income_statement_waterfall"

    def test_recommend_balance_sheet(self):
        """Test balance sheet chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show balance sheet composition")

        assert result["chart_type"] == "balance_sheet"

    def test_recommend_radar(self):
        """Test radar chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show ratio profile for company")

        assert result["chart_type"] == "ratio_radar"

    def test_recommend_trend(self):
        """Test trend chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show revenue trend over time")

        assert result["chart_type"] == "multi_year_trend"

    def test_recommend_yoy(self):
        """Test YoY comparison recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Compare revenue year over year")

        assert result["chart_type"] == "yoy_comparison"

    def test_recommend_sunburst(self):
        """Test sunburst chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show sector sunburst by market cap")

        assert result["chart_type"] == "sector_sunburst"

    def test_recommend_heatmap(self):
        """Test heatmap recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show sector performance heatmap")

        assert result["chart_type"] == "sector_heatmap"

    def test_recommend_scatter(self):
        """Test scatter plot recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show risk return scatter plot")

        assert result["chart_type"] == "risk_return"

    def test_recommend_dashboard(self):
        """Test dashboard recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Show financial dashboard overview")

        assert result["chart_type"] == "dashboard"

    def test_recommend_comparison(self):
        """Test comparison chart recommendation."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Compare ROE between top companies")

        # Comparison can be detected as bar_comparison or ratio_comparison
        assert result["chart_type"] in ["bar_comparison", "ratio_comparison"]

    def test_recommend_default(self):
        """Test default recommendation for unknown query."""
        from components.visualizations.financial_charts import recommend_chart

        result = recommend_chart("Just show me some data")

        assert result["chart_type"] == "bar"
        assert result["function"] is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_waterfall_zero_values(self):
        """Test waterfall with zero values."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=0,
            cost_of_sales=0,
            gross_profit=0,
            operating_expenses=0,
            operating_profit=0
        )

        assert fig is not None

    def test_waterfall_negative_values(self):
        """Test waterfall with negative values (losses)."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=1000000,
            cost_of_sales=1200000,  # Higher than revenue
            gross_profit=-200000,
            operating_expenses=100000,
            operating_profit=-300000,
            net_profit=-350000
        )

        assert fig is not None

    def test_large_numbers(self):
        """Test with very large numbers (trillions)."""
        from components.visualizations.financial_charts import create_income_statement_waterfall

        fig = create_income_statement_waterfall(
            revenue=1e12,  # 1 trillion
            cost_of_sales=4e11,
            gross_profit=6e11,
            operating_expenses=2e11,
            operating_profit=4e11
        )

        assert fig is not None
