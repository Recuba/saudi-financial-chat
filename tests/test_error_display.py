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


def test_format_api_error_returns_dict():
    """Test that format_api_error always returns a dictionary."""
    from components.error_display import format_api_error

    result = format_api_error("Any error message")

    assert isinstance(result, dict)
    assert "type" in result
    assert "title" in result


def test_format_api_error_has_required_keys():
    """Test that formatted errors have all required keys."""
    from components.error_display import format_api_error

    result = format_api_error("Test error")

    required_keys = ["type", "title", "original_message", "steps"]
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"


def test_get_suggested_queries_for_generic_error():
    """Test suggested queries for generic errors."""
    from components.error_display import get_suggested_queries

    suggestions = get_suggested_queries("generic")

    assert isinstance(suggestions, list)


def test_get_suggested_queries_for_data_error():
    """Test suggested queries for data errors."""
    from components.error_display import get_suggested_queries

    suggestions = get_suggested_queries("data")

    assert isinstance(suggestions, list)


def test_format_api_error_with_connection_error():
    """Test that connection errors are properly formatted."""
    from components.error_display import format_api_error

    error_msg = "Failed to connect to OpenRouter API"
    result = format_api_error(error_msg)

    assert result["type"] in ["timeout", "generic"]


def test_error_steps_are_actionable():
    """Test that error steps are actionable strings."""
    from components.error_display import format_api_error

    result = format_api_error("API key invalid")

    for step in result["steps"]:
        assert isinstance(step, str)
        assert len(step) > 0


def test_format_error_with_context_returns_dict():
    """Test that format_error_with_context returns a dictionary."""
    from components.error_display import format_error_with_context

    result = format_error_with_context("Error message", "User query")

    assert isinstance(result, dict)


def test_format_api_error_with_empty_message():
    """Test handling of empty error message."""
    from components.error_display import format_api_error

    result = format_api_error("")

    assert result["type"] == "generic"
    assert result["title"] is not None
