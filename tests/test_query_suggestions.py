"""Tests for query suggestions component."""

import pytest


def test_get_suggestions_returns_list():
    """Test that suggestions returns a list."""
    from components.query_suggestions import get_suggestions

    suggestions = get_suggestions("revenue", limit=5)

    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5


def test_get_suggestions_matches_input():
    """Test that suggestions match input text."""
    from components.query_suggestions import get_suggestions

    suggestions = get_suggestions("top 10")

    assert all("top" in s.lower() for s in suggestions)


def test_common_queries_exist():
    """Test that common queries are defined."""
    from components.query_suggestions import COMMON_QUERIES

    assert isinstance(COMMON_QUERIES, list)
    assert len(COMMON_QUERIES) >= 10


def test_get_column_based_suggestions():
    """Test suggestions based on column names."""
    from components.query_suggestions import get_column_suggestions

    columns = ["revenue", "net_profit", "company_name"]

    suggestions = get_column_suggestions(columns, "What is the")

    assert isinstance(suggestions, list)


def test_get_suggestions_empty_query():
    """Test suggestions with empty query returns common queries."""
    from components.query_suggestions import get_suggestions, COMMON_QUERIES

    suggestions = get_suggestions("", limit=5)

    assert isinstance(suggestions, list)
    assert len(suggestions) == 5
    # Should return first 5 common queries for empty input
    assert suggestions == COMMON_QUERIES[:5]


def test_get_suggestions_short_query():
    """Test suggestions with very short query returns common queries."""
    from components.query_suggestions import get_suggestions, COMMON_QUERIES

    suggestions = get_suggestions("a", limit=3)

    assert len(suggestions) == 3
    assert suggestions == COMMON_QUERIES[:3]


def test_get_suggestions_keyword_matching():
    """Test that suggestions match multiple keywords."""
    from components.query_suggestions import get_suggestions

    suggestions = get_suggestions("sector revenue")

    # Should match queries containing both "sector" and "revenue"
    assert isinstance(suggestions, list)
    for s in suggestions:
        assert "sector" in s.lower() or "revenue" in s.lower()


def test_query_templates_exist():
    """Test that query templates are defined."""
    from components.query_suggestions import QUERY_TEMPLATES

    assert isinstance(QUERY_TEMPLATES, dict)
    assert "top" in QUERY_TEMPLATES
    assert "average" in QUERY_TEMPLATES
    assert "compare" in QUERY_TEMPLATES


def test_get_column_suggestions_returns_list():
    """Test column suggestions returns a list."""
    from components.query_suggestions import get_column_suggestions

    columns = ["total_revenue", "net_profit_margin", "company_name", "sector"]

    suggestions = get_column_suggestions(columns, "")

    assert isinstance(suggestions, list)


def test_get_column_suggestions_metric_columns():
    """Test column suggestions focuses on metric columns."""
    from components.query_suggestions import get_column_suggestions

    columns = ["revenue", "profit", "name", "date"]

    suggestions = get_column_suggestions(columns, "")

    # Should generate suggestions for metric columns
    assert any("revenue" in s.lower() for s in suggestions)
    assert any("profit" in s.lower() for s in suggestions)


def test_get_suggestions_limit_respected():
    """Test that limit parameter is respected."""
    from components.query_suggestions import get_suggestions

    suggestions_3 = get_suggestions("company", limit=3)
    suggestions_10 = get_suggestions("company", limit=10)

    assert len(suggestions_3) <= 3
    assert len(suggestions_10) <= 10


def test_get_suggestions_no_duplicates():
    """Test that suggestions don't contain duplicates."""
    from components.query_suggestions import get_suggestions

    suggestions = get_suggestions("top", limit=10)

    # No duplicates
    assert len(suggestions) == len(set(suggestions))
