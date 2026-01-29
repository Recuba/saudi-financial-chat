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
