"""Tests for comparison mode component."""

import pytest
import pandas as pd


def test_compare_companies():
    """Test comparing two companies for a specific year."""
    from components.comparison_mode import compare_entities

    df = pd.DataFrame({
        "company_name": ["A", "A", "B", "B"],
        "fiscal_year": [2023, 2022, 2023, 2022],
        "revenue": [100, 90, 200, 180],
    })

    # Compare for specific year to get one row per company
    result = compare_entities(
        df,
        entity_col="company_name",
        entities=["A", "B"],
        metrics=["revenue"],
        year=2023
    )

    assert result is not None
    assert len(result) == 2  # One row per company for year 2023


def test_get_comparison_metrics():
    """Test getting available metrics for comparison."""
    from components.comparison_mode import get_comparison_metrics

    df = pd.DataFrame({
        "company_name": ["A"],
        "revenue": [100],
        "net_profit": [10],
        "sector": ["Tech"],
    })

    metrics = get_comparison_metrics(df)

    assert "revenue" in metrics
    assert "net_profit" in metrics
    assert "sector" not in metrics  # Non-numeric excluded


def test_format_comparison_table():
    """Test formatting comparison results."""
    from components.comparison_mode import format_comparison_table

    data = {
        "Company A": {"revenue": 100, "profit": 10},
        "Company B": {"revenue": 200, "profit": 20},
    }

    table = format_comparison_table(data)

    assert "Company A" in table.columns or "Company A" in table.index


def test_compare_entities_with_year_filter():
    """Test comparing entities with year filter."""
    from components.comparison_mode import compare_entities

    df = pd.DataFrame({
        "company_name": ["A", "A", "B", "B"],
        "fiscal_year": [2023, 2022, 2023, 2022],
        "revenue": [100, 90, 200, 180],
    })

    result = compare_entities(
        df,
        entity_col="company_name",
        entities=["A", "B"],
        metrics=["revenue"],
        year=2023
    )

    assert result is not None
    # Should only have 2023 data
    assert all(result["fiscal_year"] == 2023)


def test_get_comparison_metrics_excludes_ids():
    """Test that ID columns are excluded from comparison metrics."""
    from components.comparison_mode import get_comparison_metrics

    df = pd.DataFrame({
        "id": [1, 2],
        "filing_id": [101, 102],
        "fiscal_year": [2023, 2022],
        "revenue": [100, 200],
    })

    metrics = get_comparison_metrics(df)

    assert "id" not in metrics
    assert "filing_id" not in metrics
    assert "fiscal_year" not in metrics
    assert "revenue" in metrics


def test_compare_entities_multiple_metrics():
    """Test comparing entities with multiple metrics."""
    from components.comparison_mode import compare_entities

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "revenue": [100, 200],
        "profit": [10, 20],
        "assets": [500, 800],
    })

    result = compare_entities(
        df,
        entity_col="company_name",
        entities=["A", "B"],
        metrics=["revenue", "profit"]
    )

    assert "revenue" in result.columns
    assert "profit" in result.columns
    assert "assets" not in result.columns  # Not selected


def test_create_comparison_chart():
    """Test creating a comparison bar chart."""
    from components.comparison_mode import create_comparison_chart

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "revenue": [100, 200],
    })

    fig = create_comparison_chart(
        df,
        entity_col="company_name",
        metric="revenue",
        title="Revenue Comparison"
    )

    assert fig is not None
    # Check it's a plotly figure
    assert hasattr(fig, "update_layout")


def test_create_comparison_chart_default_title():
    """Test creating comparison chart with default title."""
    from components.comparison_mode import create_comparison_chart

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "net_profit": [10, 20],
    })

    fig = create_comparison_chart(
        df,
        entity_col="company_name",
        metric="net_profit"
    )

    assert fig is not None


def test_format_metric_value_billions():
    """Test formatting values in billions."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value(5_000_000_000)

    assert "B" in result
    assert "5" in result


def test_format_metric_value_millions():
    """Test formatting values in millions."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value(5_000_000)

    assert "M" in result
    assert "5" in result


def test_format_metric_value_thousands():
    """Test formatting values in thousands."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value(5_000)

    assert "K" in result
    assert "5" in result


def test_format_metric_value_small():
    """Test formatting small values."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value(42.5)

    assert "42.50" in result


def test_format_metric_value_na():
    """Test formatting NA/null values."""
    from components.comparison_mode import _format_metric_value
    import math

    result = _format_metric_value(float('nan'))

    assert result == "N/A"


def test_format_metric_value_string():
    """Test formatting string values."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value("test")

    assert result == "test"


def test_format_metric_value_negative():
    """Test formatting negative values."""
    from components.comparison_mode import _format_metric_value

    result = _format_metric_value(-5_000_000)

    assert "M" in result
    assert "-" in result


def test_compare_entities_without_year():
    """Test comparing entities without year filter."""
    from components.comparison_mode import compare_entities

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "revenue": [100, 200],
    })

    result = compare_entities(
        df,
        entity_col="company_name",
        entities=["A", "B"],
        metrics=["revenue"]
    )

    assert len(result) == 2


def test_get_comparison_metrics_empty_dataframe():
    """Test getting metrics from empty numeric columns."""
    from components.comparison_mode import get_comparison_metrics

    df = pd.DataFrame({
        "company_name": ["A", "B"],
        "sector": ["Tech", "Finance"],
    })

    metrics = get_comparison_metrics(df)

    assert isinstance(metrics, list)
    assert len(metrics) == 0
