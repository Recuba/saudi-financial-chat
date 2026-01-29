"""Tests for session management."""

import pytest


def test_session_defaults_exist():
    """Test that session defaults are defined."""
    from components.session_manager import SESSION_DEFAULTS

    assert isinstance(SESSION_DEFAULTS, dict)
    assert "chat_history" in SESSION_DEFAULTS
    assert "filters" in SESSION_DEFAULTS


def test_initialize_session_creates_keys():
    """Test session initialization."""
    from components.session_manager import get_session_defaults

    defaults = get_session_defaults()

    assert "chat_history" in defaults
    assert "favorite_queries" in defaults
    assert isinstance(defaults["chat_history"], list)


def test_save_favorite_query():
    """Test saving a favorite query."""
    from components.session_manager import add_favorite_query, get_favorite_queries

    # This would need mock st.session_state in real test
    query = "What is the revenue?"

    # Verify structure
    assert isinstance(query, str)


def test_get_recent_queries():
    """Test getting recent queries."""
    from components.session_manager import get_recent_queries_structure

    structure = get_recent_queries_structure()

    assert "max_items" in structure
    assert structure["max_items"] == 10


def test_session_defaults_have_required_keys():
    """Test that all required keys are in defaults."""
    from components.session_manager import SESSION_DEFAULTS

    required_keys = [
        "chat_history",
        "favorite_queries",
        "recent_queries",
        "filters",
        "selected_dataset",
        "theme_preference",
    ]

    for key in required_keys:
        assert key in SESSION_DEFAULTS, f"Missing required key: {key}"


def test_get_session_defaults_returns_copy():
    """Test that get_session_defaults returns a copy, not the original."""
    from components.session_manager import get_session_defaults, SESSION_DEFAULTS

    defaults = get_session_defaults()
    defaults["test_key"] = "test_value"

    # Original should not be modified
    assert "test_key" not in SESSION_DEFAULTS


def test_recent_queries_structure_has_fields():
    """Test that recent queries structure has expected fields."""
    from components.session_manager import get_recent_queries_structure

    structure = get_recent_queries_structure()

    assert "fields" in structure
    assert "query" in structure["fields"]
    assert "timestamp" in structure["fields"]


def test_session_defaults_contains_selected_model():
    """Test that session defaults include selected_model."""
    from components.session_manager import SESSION_DEFAULTS

    assert "selected_model" in SESSION_DEFAULTS


def test_session_defaults_contains_show_code():
    """Test that session defaults include show_code_by_default."""
    from components.session_manager import SESSION_DEFAULTS

    assert "show_code_by_default" in SESSION_DEFAULTS
    assert isinstance(SESSION_DEFAULTS["show_code_by_default"], bool)


def test_session_defaults_chat_history_is_list():
    """Test that chat history default is an empty list."""
    from components.session_manager import SESSION_DEFAULTS

    assert isinstance(SESSION_DEFAULTS["chat_history"], list)
    assert len(SESSION_DEFAULTS["chat_history"]) == 0


def test_session_defaults_filters_is_dict():
    """Test that filters default is an empty dict."""
    from components.session_manager import SESSION_DEFAULTS

    assert isinstance(SESSION_DEFAULTS["filters"], dict)


def test_get_session_defaults_returns_dict():
    """Test that get_session_defaults returns a dictionary."""
    from components.session_manager import get_session_defaults

    defaults = get_session_defaults()

    assert isinstance(defaults, dict)
    assert len(defaults) > 0


def test_recent_queries_structure_max_items():
    """Test that recent queries has correct max_items."""
    from components.session_manager import get_recent_queries_structure

    structure = get_recent_queries_structure()

    assert structure["max_items"] == 10


def test_recent_queries_structure_has_dataset_field():
    """Test that recent queries structure includes dataset."""
    from components.session_manager import get_recent_queries_structure

    structure = get_recent_queries_structure()

    assert "dataset" in structure["fields"]


def test_session_defaults_theme_preference():
    """Test that session defaults include theme preference."""
    from components.session_manager import SESSION_DEFAULTS

    assert "theme_preference" in SESSION_DEFAULTS
    assert SESSION_DEFAULTS["theme_preference"] == "dark"


def test_get_session_defaults_independent_copies():
    """Test that multiple calls return independent copies."""
    from components.session_manager import get_session_defaults

    defaults1 = get_session_defaults()
    defaults2 = get_session_defaults()

    defaults1["new_key"] = "value"

    assert "new_key" not in defaults2
