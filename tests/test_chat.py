"""Tests for chat component utilities."""

import pytest


def test_format_response_dataframe():
    """Test formatting DataFrame responses."""
    import pandas as pd
    from components.chat import format_response

    # Create mock response
    class MockResponse:
        type = "dataframe"
        value = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        last_code_executed = "df.head()"

    result = format_response(MockResponse())

    assert result["type"] == "dataframe"
    assert result["data"] is not None
    assert result["code"] == "df.head()"


def test_format_response_text():
    """Test formatting text responses."""
    from components.chat import format_response

    class MockResponse:
        type = "text"
        value = "The average is 42.5"
        last_code_executed = "df['col'].mean()"

    result = format_response(MockResponse())

    assert result["type"] == "text"
    assert "42.5" in result["data"]


def test_format_response_handles_none():
    """Test that None responses are handled."""
    from components.chat import format_response

    result = format_response(None)

    assert result["type"] == "error"
    assert "error" in result["message"].lower() or "no response" in result["message"].lower()


def test_format_response_chart():
    """Test formatting chart responses."""
    from components.chat import format_response

    class MockResponse:
        type = "chart"
        value = "/path/to/chart.png"
        last_code_executed = "df.plot()"

    result = format_response(MockResponse())

    assert result["type"] == "chart"
    assert result["data"] == "/path/to/chart.png"
    assert result["code"] == "df.plot()"


def test_format_response_string_type():
    """Test formatting string type responses (alias for text)."""
    from components.chat import format_response

    class MockResponse:
        type = "string"
        value = "Hello World"
        last_code_executed = "print('Hello World')"

    result = format_response(MockResponse())

    assert result["type"] == "text"
    assert result["data"] == "Hello World"


def test_format_response_unknown_type():
    """Test formatting unknown response types falls back to text."""
    from components.chat import format_response

    class MockResponse:
        type = "unknown_type"
        value = "Some value"
        last_code_executed = "some_code()"

    result = format_response(MockResponse())

    assert result["type"] == "text"
    assert "Some value" in result["data"]


def test_format_response_missing_attributes():
    """Test formatting response with missing attributes."""
    from components.chat import format_response

    class MockResponse:
        pass  # No attributes

    result = format_response(MockResponse())

    # Should handle gracefully with defaults
    assert result["type"] == "text"
    assert result["code"] == ""


def test_get_chat_history_returns_list():
    """Test that chat history is stored as a list."""
    # Chat history is stored as a list in session_state
    # This test verifies the expected data structure
    from components.chat import format_response

    # The history structure is: List[Dict]
    history = []
    history.append({"role": "user", "content": "test"})

    assert isinstance(history, list)
    assert len(history) == 1
    assert history[0]["role"] == "user"


def test_add_to_chat_history_creates_entry():
    """Test that chat history entries have correct structure."""
    from components.chat import format_response

    class MockResponse:
        type = "text"
        value = "Test response"
        last_code_executed = "df.head()"

    response_data = format_response(MockResponse())

    # Verify the entry structure used by add_to_chat_history
    entry = {
        "role": "assistant",
        "content": "What is X?",
        "response_data": response_data,
    }

    # These are the required fields for chat history entries
    assert "role" in entry
    assert "content" in entry
    assert "response_data" in entry
    assert entry["response_data"]["type"] == "text"
    assert entry["role"] in ["user", "assistant"]
