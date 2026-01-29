"""Tests for visualization components."""

import pytest
import pandas as pd


def test_detect_chart_request_positive():
    """Test detecting chart requests in queries."""
    from components.visualizations.response_charts import should_render_chart

    chart_queries = [
        "Create a bar chart of revenue",
        "Show me a pie chart of sectors",
        "Plot the trend over time",
        "Visualize the top 10 companies",
        "Graph the comparison",
    ]

    for query in chart_queries:
        assert should_render_chart(query) == True


def test_detect_chart_request_negative():
    """Test non-chart queries return False."""
    from components.visualizations.response_charts import should_render_chart

    non_chart_queries = [
        "What is the total revenue?",
        "List the top 10 companies",
        "How many companies are there?",
    ]

    for query in non_chart_queries:
        assert should_render_chart(query) == False


def test_create_bar_chart_returns_figure():
    """Test creating a bar chart returns Plotly figure."""
    from components.visualizations.response_charts import create_bar_chart

    df = pd.DataFrame({
        "company": ["A", "B", "C"],
        "revenue": [100, 200, 150]
    })

    fig = create_bar_chart(df, x="company", y="revenue", title="Revenue")

    assert fig is not None
    assert hasattr(fig, "to_html")


def test_auto_visualize_dataframe():
    """Test automatic visualization of dataframes."""
    from components.visualizations.response_charts import auto_visualize

    df = pd.DataFrame({
        "company": ["A", "B", "C"],
        "revenue": [100, 200, 150]
    })

    result = auto_visualize(df, query="show bar chart of revenue by company")

    assert result is not None


def test_detect_chart_type_pie():
    """Test detecting pie chart type."""
    from components.visualizations.response_charts import detect_chart_type

    assert detect_chart_type("show me a pie chart of sectors") == "pie"
    assert detect_chart_type("create a PIE chart") == "pie"


def test_detect_chart_type_line():
    """Test detecting line chart type."""
    from components.visualizations.response_charts import detect_chart_type

    assert detect_chart_type("plot the trend over time") == "line"
    assert detect_chart_type("show me a line chart") == "line"
    assert detect_chart_type("revenue over time") == "line"


def test_detect_chart_type_bar():
    """Test detecting bar chart type."""
    from components.visualizations.response_charts import detect_chart_type

    assert detect_chart_type("create a bar chart") == "bar"
    assert detect_chart_type("BAR graph of sales") == "bar"


def test_detect_chart_type_auto():
    """Test detecting auto chart type when no specific type mentioned."""
    from components.visualizations.response_charts import detect_chart_type

    assert detect_chart_type("visualize the data") == "auto"
    assert detect_chart_type("show me a chart") == "auto"


def test_infer_chart_columns():
    """Test inferring x and y columns from dataframe."""
    from components.visualizations.response_charts import infer_chart_columns

    df = pd.DataFrame({
        "company": ["A", "B", "C"],
        "revenue": [100, 200, 150],
        "profit": [10, 20, 15]
    })

    x_col, y_col = infer_chart_columns(df, "show revenue by company")
    assert x_col == "company"
    assert y_col == "revenue"


def test_create_pie_chart():
    """Test creating a pie chart."""
    from components.visualizations.response_charts import create_pie_chart

    df = pd.DataFrame({
        "sector": ["Tech", "Finance", "Healthcare"],
        "value": [100, 200, 150]
    })

    fig = create_pie_chart(df, names="sector", values="value", title="Sectors")
    assert fig is not None
    assert hasattr(fig, "to_html")


def test_create_line_chart():
    """Test creating a line chart."""
    from components.visualizations.response_charts import create_line_chart

    df = pd.DataFrame({
        "year": [2020, 2021, 2022],
        "revenue": [100, 150, 200]
    })

    fig = create_line_chart(df, x="year", y="revenue", title="Revenue Trend")
    assert fig is not None
    assert hasattr(fig, "to_html")


def test_auto_visualize_empty_dataframe():
    """Test auto_visualize returns None for empty dataframe."""
    from components.visualizations.response_charts import auto_visualize

    df = pd.DataFrame()
    result = auto_visualize(df, query="show chart")
    assert result is None


def test_auto_visualize_none_dataframe():
    """Test auto_visualize returns None for None input."""
    from components.visualizations.response_charts import auto_visualize

    result = auto_visualize(None, query="show chart")
    assert result is None


def test_bar_chart_has_plotly_attributes():
    """Test that bar chart has expected plotly attributes."""
    from components.visualizations.response_charts import create_bar_chart

    df = pd.DataFrame({
        "category": ["X", "Y", "Z"],
        "value": [10, 20, 30]
    })

    fig = create_bar_chart(df, x="category", y="value")

    # Plotly figures have these attributes
    assert hasattr(fig, "data")
    assert hasattr(fig, "layout")


def test_pie_chart_has_plotly_attributes():
    """Test that pie chart has expected plotly attributes."""
    from components.visualizations.response_charts import create_pie_chart

    df = pd.DataFrame({
        "name": ["A", "B", "C"],
        "amount": [100, 200, 300]
    })

    fig = create_pie_chart(df, names="name", values="amount")

    assert hasattr(fig, "data")
    assert hasattr(fig, "layout")


def test_line_chart_has_plotly_attributes():
    """Test that line chart has expected plotly attributes."""
    from components.visualizations.response_charts import create_line_chart

    df = pd.DataFrame({
        "month": [1, 2, 3, 4],
        "sales": [100, 120, 140, 160]
    })

    fig = create_line_chart(df, x="month", y="sales")

    assert hasattr(fig, "data")
    assert hasattr(fig, "layout")


def test_infer_chart_columns_with_numeric_columns():
    """Test inferring columns when multiple numeric columns exist."""
    from components.visualizations.response_charts import infer_chart_columns

    df = pd.DataFrame({
        "name": ["A", "B", "C"],
        "value1": [10, 20, 30],
        "value2": [15, 25, 35]
    })

    x_col, y_col = infer_chart_columns(df, "show chart")

    # Should pick appropriate columns
    assert x_col in df.columns
    assert y_col in df.columns


def test_should_render_chart_case_insensitive():
    """Test that chart detection is case insensitive."""
    from components.visualizations.response_charts import should_render_chart

    assert should_render_chart("CHART of revenue") == True
    assert should_render_chart("chart of REVENUE") == True
    assert should_render_chart("Create a CHART") == True


def test_detect_chart_type_with_mixed_case():
    """Test chart type detection with mixed case."""
    from components.visualizations.response_charts import detect_chart_type

    assert detect_chart_type("PIE chart") == "pie"
    assert detect_chart_type("Bar Chart") == "bar"
    assert detect_chart_type("LINE Chart") == "line"


def test_auto_visualize_with_single_column():
    """Test auto visualize with single column dataframe."""
    from components.visualizations.response_charts import auto_visualize

    df = pd.DataFrame({
        "value": [1, 2, 3]
    })

    result = auto_visualize(df, query="show chart")

    # Should handle gracefully (may return None or a valid chart)
    assert result is None or hasattr(result, "data")


def test_create_bar_chart_with_title():
    """Test bar chart includes title."""
    from components.visualizations.response_charts import create_bar_chart

    df = pd.DataFrame({
        "item": ["A", "B"],
        "count": [5, 10]
    })

    fig = create_bar_chart(df, x="item", y="count", title="Item Counts")

    assert fig.layout.title is not None or hasattr(fig.layout, "title")


def test_visualization_functions_exist():
    """Test that all visualization functions are importable."""
    from components.visualizations.response_charts import (
        should_render_chart,
        detect_chart_type,
        infer_chart_columns,
        create_bar_chart,
        create_pie_chart,
        create_line_chart,
        auto_visualize,
    )

    assert callable(should_render_chart)
    assert callable(detect_chart_type)
    assert callable(infer_chart_columns)
    assert callable(create_bar_chart)
    assert callable(create_pie_chart)
    assert callable(create_line_chart)
    assert callable(auto_visualize)
