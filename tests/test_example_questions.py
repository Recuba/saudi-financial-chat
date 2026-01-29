"""Tests for example questions component."""

import pytest


def test_example_questions_exist():
    """Test that example questions are defined."""
    from components.example_questions import EXAMPLE_QUESTIONS

    assert isinstance(EXAMPLE_QUESTIONS, dict)
    assert len(EXAMPLE_QUESTIONS) > 0


def test_example_questions_have_required_fields():
    """Test that each example has required fields."""
    from components.example_questions import EXAMPLE_QUESTIONS

    for category, questions in EXAMPLE_QUESTIONS.items():
        for q in questions:
            assert "label" in q
            assert "query" in q
            assert "icon" in q


def test_example_categories_include_popular():
    """Test that Popular category exists with examples."""
    from components.example_questions import EXAMPLE_QUESTIONS

    assert "Popular" in EXAMPLE_QUESTIONS
    assert len(EXAMPLE_QUESTIONS["Popular"]) >= 3


def test_get_example_by_category():
    """Test getting examples by category."""
    from components.example_questions import get_examples_by_category

    popular = get_examples_by_category("Popular")

    assert isinstance(popular, list)
    assert len(popular) > 0
