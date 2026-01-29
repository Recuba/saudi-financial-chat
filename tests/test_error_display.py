"""Tests for error display component."""

import pytest


def test_format_api_error_with_auth_message():
    """Test that authentication errors get user-friendly formatting."""
    from components.error_display import format_api_error

    error_msg = "Authentication failed: invalid API key"
    result = format_api_error(error_msg)

    assert result["type"] == "auth"
    assert "api key" in result["title"].lower()
    assert len(result["steps"]) > 0
    assert "settings" in result["action_label"].lower() or "check" in result["action_label"].lower()


def test_format_api_error_with_rate_limit():
    """Test that rate limit errors get appropriate formatting."""
    from components.error_display import format_api_error

    error_msg = "Rate limit exceeded"
    result = format_api_error(error_msg)

    assert result["type"] == "rate_limit"
    assert "rate" in result["title"].lower() or "limit" in result["title"].lower()


def test_format_api_error_with_generic_error():
    """Test that unknown errors get generic formatting."""
    from components.error_display import format_api_error

    error_msg = "Something unexpected happened"
    result = format_api_error(error_msg)

    assert result["type"] == "generic"
    assert result["title"] is not None


def test_format_api_error_includes_original_message():
    """Test that original error message is preserved."""
    from components.error_display import format_api_error

    error_msg = "Connection timeout after 30s"
    result = format_api_error(error_msg)

    assert error_msg in result["original_message"]


def test_format_api_error_with_timeout():
    """Test that timeout errors get appropriate formatting."""
    from components.error_display import format_api_error

    error_msg = "Connection timeout after 30s"
    result = format_api_error(error_msg)

    assert result["type"] == "timeout"
    assert "connection" in result["title"].lower() or "timeout" in result["title"].lower()


def test_format_api_error_with_data_error():
    """Test that data errors get appropriate formatting."""
    from components.error_display import format_api_error

    error_msg = "Column 'revenue' not found in dataframe"
    result = format_api_error(error_msg)

    assert result["type"] == "data"
    assert "data" in result["title"].lower() or "query" in result["title"].lower()


def test_format_api_error_with_model_error():
    """Test that model/LLM errors get appropriate formatting."""
    from components.error_display import format_api_error

    error_msg = "Gemini model returned empty response"
    result = format_api_error(error_msg)

    assert result["type"] == "model"
    assert "model" in result["title"].lower() or "ai" in result["title"].lower()


def test_format_api_error_with_response_format_error():
    """Test that response format errors get helpful suggestions."""
    from components.error_display import format_api_error

    error_msg = "result must be in the format of dictionary"

    result = format_api_error(error_msg)

    assert result["type"] == "response_format"
    assert "rephras" in result["steps"][0].lower()


def test_error_includes_suggested_queries():
    """Test that errors include query suggestions when applicable."""
    from components.error_display import get_suggested_queries

    error_type = "response_format"

    suggestions = get_suggested_queries(error_type)

    assert isinstance(suggestions, list)
    assert len(suggestions) >= 2


def test_format_error_with_query_context():
    """Test formatting error with original query context."""
    from components.error_display import format_error_with_context

    error_msg = "No data found"
    query = "What is the revenue for NonExistent Company?"

    result = format_error_with_context(error_msg, query)

    assert "query" in result or "NonExistent" in result.get("steps", [""])[0]
