"""Tests for LLM configuration utility."""

import pytest


def test_validate_api_key_with_valid_key():
    """Test that valid API keys pass validation."""
    from utils.llm_config import validate_api_key

    valid_key = "sk-or-v1-abcd1234567890"
    result = validate_api_key(valid_key)

    assert result["valid"] is True
    assert result["error"] is None


def test_validate_api_key_with_empty_key():
    """Test that empty keys fail validation."""
    from utils.llm_config import validate_api_key

    result = validate_api_key("")

    assert result["valid"] is False
    assert "empty" in result["error"].lower() or "missing" in result["error"].lower()


def test_validate_api_key_with_none():
    """Test that None keys fail validation."""
    from utils.llm_config import validate_api_key

    result = validate_api_key(None)

    assert result["valid"] is False


def test_get_llm_config_status_returns_dict():
    """Test that get_llm_config_status returns configuration status."""
    from utils.llm_config import get_llm_config_status

    result = get_llm_config_status()

    assert isinstance(result, dict)
    assert "configured" in result
    assert "model" in result
