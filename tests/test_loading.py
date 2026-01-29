"""Tests for loading indicator component."""

import pytest


def test_get_skeleton_css_returns_string():
    """Test that skeleton CSS is generated."""
    from components.loading import get_skeleton_css

    css = get_skeleton_css()

    assert isinstance(css, str)
    assert "skeleton" in css.lower()
    assert "@keyframes" in css


def test_loading_messages_exist():
    """Test that loading messages are defined."""
    from components.loading import LOADING_MESSAGES

    assert isinstance(LOADING_MESSAGES, list)
    assert len(LOADING_MESSAGES) >= 3


def test_get_random_loading_message_returns_string():
    """Test that random loading message returns a string."""
    from components.loading import get_random_loading_message

    message = get_random_loading_message()

    assert isinstance(message, str)
    assert len(message) > 0


def test_get_random_loading_message_from_list():
    """Test that random message comes from LOADING_MESSAGES list."""
    from components.loading import get_random_loading_message, LOADING_MESSAGES

    # Test multiple times to check randomness
    for _ in range(10):
        message = get_random_loading_message()
        assert message in LOADING_MESSAGES


def test_skeleton_css_contains_animations():
    """Test that skeleton CSS contains keyframes animation."""
    from components.loading import get_skeleton_css

    css = get_skeleton_css()

    assert "@keyframes" in css
    assert "skeleton-pulse" in css


def test_skeleton_css_contains_classes():
    """Test that skeleton CSS contains expected classes."""
    from components.loading import get_skeleton_css

    css = get_skeleton_css()

    assert ".skeleton" in css
    assert ".skeleton-text" in css
    assert ".skeleton-chart" in css
    assert ".skeleton-table" in css


def test_loading_messages_are_non_empty():
    """Test that all loading messages are non-empty strings."""
    from components.loading import LOADING_MESSAGES

    for message in LOADING_MESSAGES:
        assert isinstance(message, str)
        assert len(message) > 0


def test_loading_messages_have_variety():
    """Test that loading messages have sufficient variety."""
    from components.loading import LOADING_MESSAGES

    # Should have at least 5 different messages
    assert len(set(LOADING_MESSAGES)) >= 5


def test_skeleton_css_has_style_tags():
    """Test that skeleton CSS is wrapped in style tags."""
    from components.loading import get_skeleton_css

    css = get_skeleton_css()

    assert "<style>" in css
    assert "</style>" in css


def test_get_random_loading_message_returns_different_values():
    """Test that random loading message returns different values over time."""
    from components.loading import get_random_loading_message

    # Get multiple messages - with 6 messages, getting the same one 20 times is very unlikely
    messages = [get_random_loading_message() for _ in range(20)]
    unique_messages = set(messages)

    # Should have at least 2 different messages in 20 attempts
    assert len(unique_messages) >= 2
