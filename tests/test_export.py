"""Tests for export functionality."""

import pytest
import pandas as pd


def test_export_dataframe_to_csv():
    """Test exporting dataframe to CSV string."""
    from components.export import export_to_csv

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    csv_str = export_to_csv(df)

    assert isinstance(csv_str, str)
    assert "a,b" in csv_str
    assert "1,3" in csv_str


def test_export_response_to_text():
    """Test exporting response to plain text."""
    from components.export import export_response_to_text

    response_data = {
        "type": "text",
        "data": "The answer is 42",
        "code": "df.sum()",
    }

    text = export_response_to_text(response_data)

    assert "The answer is 42" in text


def test_generate_export_filename():
    """Test generating export filename with timestamp."""
    from components.export import generate_export_filename

    filename = generate_export_filename("query_result", "csv")

    assert filename.endswith(".csv")
    assert "query_result" in filename


def test_export_chat_history():
    """Test exporting chat history to markdown."""
    from components.export import export_chat_history_to_markdown

    history = [
        {"role": "user", "content": "What is revenue?"},
        {"role": "assistant", "content": "Revenue is...", "response_data": {"type": "text", "data": "100"}},
    ]

    md = export_chat_history_to_markdown(history)

    assert "What is revenue?" in md
    assert isinstance(md, str)


def test_export_dataframe_response_to_text():
    """Test exporting a dataframe response to text."""
    from components.export import export_response_to_text

    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    response_data = {
        "type": "dataframe",
        "data": df,
        "code": "df.head()",
    }

    text = export_response_to_text(response_data)

    assert "col1" in text
    assert "col2" in text
    assert "dataframe" in text.lower()


def test_export_chart_response_to_text():
    """Test exporting a chart response to text."""
    from components.export import export_response_to_text

    response_data = {
        "type": "chart",
        "data": "/path/to/chart.png",
        "code": "df.plot()",
    }

    text = export_response_to_text(response_data)

    assert "chart" in text.lower()


def test_export_empty_history():
    """Test exporting empty chat history."""
    from components.export import export_chat_history_to_markdown

    history = []

    md = export_chat_history_to_markdown(history)

    assert "Ra'd AI" in md
    assert isinstance(md, str)


def test_generate_filename_format():
    """Test that filename has correct timestamp format."""
    from components.export import generate_export_filename
    import re

    filename = generate_export_filename("test", "txt")

    # Should match pattern: test_YYYYMMDD_HHMMSS.txt
    pattern = r"test_\d{8}_\d{6}\.txt"
    assert re.match(pattern, filename)


def test_export_to_csv_with_special_characters():
    """Test CSV export handles special characters."""
    from components.export import export_to_csv

    df = pd.DataFrame({"name": ["Test, Inc.", "Company \"X\""], "value": [100, 200]})

    csv_str = export_to_csv(df)

    assert isinstance(csv_str, str)
    assert "name" in csv_str


def test_export_response_without_code():
    """Test exporting response without code."""
    from components.export import export_response_to_text

    response_data = {
        "type": "text",
        "data": "Simple answer",
    }

    text = export_response_to_text(response_data)

    assert "Simple answer" in text
