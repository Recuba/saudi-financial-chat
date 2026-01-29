"""Tests for copy functionality."""

import pytest


def test_format_response_for_copy_text():
    """Test formatting text response for clipboard."""
    from components.chat import format_response_for_copy

    response_data = {
        "type": "text",
        "data": "The average revenue is SAR 1.5 billion",
        "code": "df['revenue'].mean()",
    }

    result = format_response_for_copy(response_data)

    assert "average revenue" in result.lower()
    assert isinstance(result, str)


def test_format_response_for_copy_dataframe():
    """Test formatting dataframe response for clipboard."""
    import pandas as pd
    from components.chat import format_response_for_copy

    df = pd.DataFrame({"company": ["A", "B"], "revenue": [100, 200]})
    response_data = {
        "type": "dataframe",
        "data": df,
        "code": "df.head()",
    }

    result = format_response_for_copy(response_data)

    assert "company" in result
    assert "revenue" in result


def test_format_response_for_copy_handles_none():
    """Test that None data is handled gracefully."""
    from components.chat import format_response_for_copy

    response_data = {
        "type": "text",
        "data": None,
        "code": "",
    }

    result = format_response_for_copy(response_data)

    assert result == ""


def test_format_response_for_copy_chart():
    """Test that chart responses return appropriate message."""
    from components.chat import format_response_for_copy

    response_data = {
        "type": "chart",
        "data": "/path/to/chart.png",
        "code": "df.plot()",
    }

    result = format_response_for_copy(response_data)

    assert "cannot copy" in result.lower()
    assert "chart" in result.lower()
