"""Tests for LLM configuration utility."""

import pytest


def test_validate_api_key_with_valid_key():
    """Test that valid API keys pass validation."""
    from utils.llm_config import validate_api_key

    # Valid key with proper format and length
    valid_key = "sk-or-v1-abcd1234567890abcd1234567890"
    result = validate_api_key(valid_key)

    assert result["valid"] is True
    assert result["error"] is None
    assert "warnings" in result


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
    assert "missing" in result["error"].lower()


def test_validate_api_key_too_short():
    """Test that short keys fail validation."""
    from utils.llm_config import validate_api_key

    result = validate_api_key("sk-or-v1-short")

    assert result["valid"] is False
    assert "short" in result["error"].lower()


def test_validate_api_key_with_wrong_format_returns_warning():
    """Test that keys with wrong format pass but return warnings."""
    from utils.llm_config import validate_api_key

    # Key without proper prefix but long enough
    key = "wrong-format-but-long-enough-to-pass-validation"
    result = validate_api_key(key)

    assert result["valid"] is True
    assert len(result.get("warnings", [])) > 0
    assert "pattern" in result["warnings"][0].lower()


def test_get_llm_config_status_returns_dict():
    """Test that get_llm_config_status returns configuration status."""
    from utils.llm_config import get_llm_config_status

    result = get_llm_config_status()

    assert isinstance(result, dict)
    assert "configured" in result
    assert "model" in result
    assert "warnings" in result
    assert "fetch_error" in result


def test_hash_api_key():
    """Test that API key hashing works correctly."""
    from utils.llm_config import _hash_api_key

    key = "sk-or-v1-test-key-12345"
    hash1 = _hash_api_key(key)
    hash2 = _hash_api_key(key)

    # Same input should produce same hash
    assert hash1 == hash2
    # Hash should not contain the original key
    assert key not in hash1
    # Hash should be 16 chars
    assert len(hash1) == 16


def test_default_model_constant():
    """Test that default model constant is set."""
    from utils.llm_config import DEFAULT_MODEL, MODEL_DISPLAY_NAME

    assert DEFAULT_MODEL is not None
    assert "openrouter" in DEFAULT_MODEL
    assert MODEL_DISPLAY_NAME is not None


def test_get_selected_model_returns_default():
    """Test that get_selected_model returns default when not set."""
    from utils.llm_config import get_selected_model, DEFAULT_MODEL

    # Note: This will use DEFAULT_MODEL since session_state won't be set in tests
    result = get_selected_model()
    assert result == DEFAULT_MODEL


def test_default_fallback_models_exist():
    """Test that default fallback models are defined."""
    from utils.llm_config import DEFAULT_FALLBACK_MODELS

    assert len(DEFAULT_FALLBACK_MODELS) > 0
    for model in DEFAULT_FALLBACK_MODELS:
        assert "id" in model
        assert "name" in model
