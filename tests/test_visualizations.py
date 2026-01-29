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
