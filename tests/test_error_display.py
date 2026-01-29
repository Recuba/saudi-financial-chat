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
