"""Integration tests for Ra'd AI application."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_all_modules_import():
    """Test that all modules can be imported without errors."""
    from styles.css import get_base_css, get_error_css
    from styles.variables import GOLD_PRIMARY, BG_DARK
    from utils.data_loader import load_data, get_dataset_info
    from utils.llm_config import validate_api_key, get_llm_config_status
    from components.error_display import format_api_error
    from components.sidebar import render_database_info
    from components.example_questions import EXAMPLE_QUESTIONS
    from components.chat import format_response

    assert get_base_css is not None
    assert GOLD_PRIMARY == "#D4A84B"
    assert load_data is not None


def test_css_generation():
    """Test that CSS is generated correctly."""
    from styles.css import get_base_css, get_error_css

    base_css = get_base_css()
    error_css = get_error_css()

    assert "<style>" in base_css
    assert "</style>" in base_css
    assert "--gold-primary" in base_css
    assert "error-banner" in error_css


def test_data_loader_returns_valid_data():
    """Test that data loader returns valid DataFrames."""
    from utils.data_loader import load_data

    data = load_data()

    assert len(data) == 4
    assert all(len(df) > 0 for df in data.values())


def test_example_questions_have_required_fields():
    """Test that all example questions have required fields."""
    from components.example_questions import EXAMPLE_QUESTIONS

    for category, questions in EXAMPLE_QUESTIONS.items():
        for q in questions:
            assert "label" in q, f"Missing label in {category}"
            assert "query" in q, f"Missing query in {category}"
            assert "icon" in q, f"Missing icon in {category}"


def test_error_formatting_covers_common_errors():
    """Test that error formatting handles common error types."""
    from components.error_display import format_api_error

    test_cases = [
        ("Authentication failed", "auth"),
        ("Rate limit exceeded", "rate_limit"),
        ("Connection timeout", "timeout"),
        ("Column 'xyz' not found", "data"),
        ("Random error message", "generic"),
    ]

    for error_msg, expected_type in test_cases:
        result = format_api_error(error_msg)
        assert result["type"] == expected_type, f"Expected {expected_type} for '{error_msg}'"


def test_dataset_display_names_complete():
    """Test that all datasets have display names."""
    from utils.data_loader import DATASET_DISPLAY_NAMES, load_data

    data = load_data()

    for dataset_key in data.keys():
        assert dataset_key in DATASET_DISPLAY_NAMES, f"Missing display name for {dataset_key}"


def test_llm_config_validation():
    """Test LLM configuration validation logic."""
    from utils.llm_config import validate_api_key

    # Invalid cases
    assert validate_api_key(None)["valid"] is False
    assert validate_api_key("")["valid"] is False
    assert validate_api_key("   ")["valid"] is False
    assert validate_api_key("short")["valid"] is False

    # Valid case
    assert validate_api_key("sk-or-valid-key-12345")["valid"] is True
