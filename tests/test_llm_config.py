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


def test_validate_api_key_with_short_key():
    """Test that short keys fail validation."""
    from utils.llm_config import validate_api_key

    result = validate_api_key("short")

    assert result["valid"] is False
    assert "short" in result["error"].lower()


def test_validate_api_key_with_whitespace():
    """Test that whitespace-only keys fail validation."""
    from utils.llm_config import validate_api_key

    result = validate_api_key("   ")

    assert result["valid"] is False


def test_default_model_defined():
    """Test that default model is defined."""
    from utils.llm_config import DEFAULT_MODEL, MODEL_DISPLAY_NAME

    assert DEFAULT_MODEL is not None
    assert isinstance(DEFAULT_MODEL, str)
    assert len(DEFAULT_MODEL) > 0
    assert MODEL_DISPLAY_NAME is not None


def test_openrouter_url_defined():
    """Test that OpenRouter URL is defined."""
    from utils.llm_config import OPENROUTER_MODELS_URL

    assert OPENROUTER_MODELS_URL is not None
    assert "openrouter" in OPENROUTER_MODELS_URL.lower()


def test_get_llm_config_status_has_required_keys():
    """Test that config status has all required keys."""
    from utils.llm_config import get_llm_config_status

    result = get_llm_config_status()

    assert "configured" in result
    assert "model" in result
    assert "model_display" in result
    assert "has_key" in result


def test_check_llm_ready():
    """Test checking if LLM is ready."""
    from utils.llm_config import check_llm_ready

    result = check_llm_ready()

    assert isinstance(result, bool)


def test_validate_api_key_strips_whitespace():
    """Test that API key validation strips whitespace."""
    from utils.llm_config import validate_api_key

    # Key with whitespace that's valid when stripped
    result = validate_api_key("  sk-or-v1-abcd1234567890  ")

    assert result["valid"] is True
