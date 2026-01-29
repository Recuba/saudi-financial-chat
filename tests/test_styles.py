"""Tests for styles module."""

import pytest


def test_get_base_css_returns_string():
    """Test that base CSS returns valid string."""
    from styles.css import get_base_css

    css = get_base_css()

    assert isinstance(css, str)
    assert "<style>" in css
    assert "</style>" in css


def test_get_error_css_returns_string():
    """Test that error CSS returns valid string."""
    from styles.css import get_error_css

    css = get_error_css()

    assert isinstance(css, str)
    assert "error" in css.lower()


def test_css_variables_exist():
    """Test that CSS variables are defined."""
    from styles.variables import (
        GOLD_PRIMARY,
        BG_DARK,
        TEXT_PRIMARY,
    )

    assert GOLD_PRIMARY.startswith("#")
    assert BG_DARK.startswith("#")
    assert TEXT_PRIMARY.startswith("#")


def test_css_contains_theme_variables():
    """Test that CSS includes theme variables."""
    from styles.css import get_base_css

    css = get_base_css()

    assert "--gold-primary" in css
    assert "--bg-dark" in css
    assert "--text-primary" in css


def test_gold_color_palette():
    """Test gold color palette variables."""
    from styles.variables import (
        GOLD_PRIMARY,
        GOLD_LIGHT,
        GOLD_DARK,
        GOLD_GRADIENT,
    )

    assert GOLD_PRIMARY.startswith("#")
    assert GOLD_LIGHT.startswith("#")
    assert GOLD_DARK.startswith("#")
    assert "linear-gradient" in GOLD_GRADIENT


def test_background_colors():
    """Test background color variables."""
    from styles.variables import (
        BG_DARK,
        BG_CARD,
        BG_CARD_HOVER,
        BG_INPUT,
    )

    assert BG_DARK.startswith("#")
    assert BG_CARD.startswith("#")
    assert BG_CARD_HOVER.startswith("#")
    assert BG_INPUT.startswith("#")


def test_text_colors():
    """Test text color variables."""
    from styles.variables import (
        TEXT_PRIMARY,
        TEXT_SECONDARY,
        TEXT_MUTED,
    )

    assert TEXT_PRIMARY.startswith("#")
    assert TEXT_SECONDARY.startswith("#")
    assert TEXT_MUTED.startswith("#")


def test_accent_colors():
    """Test accent color variables."""
    from styles.variables import (
        ACCENT_GREEN,
        ACCENT_RED,
        ACCENT_YELLOW,
        ACCENT_BLUE,
    )

    assert ACCENT_GREEN.startswith("#")
    assert ACCENT_RED.startswith("#")
    assert ACCENT_YELLOW.startswith("#")
    assert ACCENT_BLUE.startswith("#")


def test_status_colors():
    """Test status color variables."""
    from styles.variables import (
        STATUS_SUCCESS,
        STATUS_WARNING,
        STATUS_ERROR,
        STATUS_INFO,
    )

    assert STATUS_SUCCESS.startswith("#")
    assert STATUS_WARNING.startswith("#")
    assert STATUS_ERROR.startswith("#")
    assert STATUS_INFO.startswith("#")


def test_typography_scale():
    """Test typography scale variables."""
    from styles.variables import (
        FONT_SIZE_XS,
        FONT_SIZE_SM,
        FONT_SIZE_BASE,
        FONT_SIZE_LG,
        FONT_SIZE_XL,
        FONT_SIZE_2XL,
    )

    assert FONT_SIZE_XS.endswith("px")
    assert FONT_SIZE_SM.endswith("px")
    assert FONT_SIZE_BASE.endswith("px")
    assert FONT_SIZE_LG.endswith("px")
    assert FONT_SIZE_XL.endswith("px")
    assert FONT_SIZE_2XL.endswith("px")


def test_spacing_scale():
    """Test spacing scale variables."""
    from styles.variables import (
        SPACING_XS,
        SPACING_SM,
        SPACING_MD,
        SPACING_LG,
        SPACING_XL,
        SPACING_2XL,
    )

    assert SPACING_XS.endswith("px")
    assert SPACING_SM.endswith("px")
    assert SPACING_MD.endswith("px")
    assert SPACING_LG.endswith("px")
    assert SPACING_XL.endswith("px")
    assert SPACING_2XL.endswith("px")


def test_border_radius():
    """Test border radius variables."""
    from styles.variables import (
        RADIUS_SM,
        RADIUS_MD,
        RADIUS_LG,
    )

    assert RADIUS_SM.endswith("px")
    assert RADIUS_MD.endswith("px")
    assert RADIUS_LG.endswith("px")


def test_shadows():
    """Test shadow variables."""
    from styles.variables import (
        SHADOW_GOLD,
        SHADOW_CARD,
        SHADOW_FOCUS,
    )

    assert "rgba" in SHADOW_GOLD
    assert "rgba" in SHADOW_CARD
    assert "rgba" in SHADOW_FOCUS


def test_transitions():
    """Test transition variables."""
    from styles.variables import (
        TRANSITION_FAST,
        TRANSITION_DEFAULT,
    )

    assert "ease" in TRANSITION_FAST
    assert "ease" in TRANSITION_DEFAULT


def test_base_css_contains_font_import():
    """Test that base CSS imports Google Fonts."""
    from styles.css import get_base_css

    css = get_base_css()

    assert "@import url" in css
    assert "fonts.googleapis.com" in css


def test_base_css_contains_animations():
    """Test that base CSS contains animations."""
    from styles.css import get_base_css

    css = get_base_css()

    assert "@keyframes" in css
    assert "pulse-gold" in css or "spin" in css


def test_base_css_contains_scrollbar_styles():
    """Test that base CSS contains scrollbar styling."""
    from styles.css import get_base_css

    css = get_base_css()

    assert "scrollbar" in css


def test_error_css_contains_error_banner():
    """Test that error CSS contains error banner styles."""
    from styles.css import get_error_css

    css = get_error_css()

    assert "error-banner" in css


def test_error_css_contains_alert_styles():
    """Test that error CSS contains alert styles."""
    from styles.css import get_error_css

    css = get_error_css()

    assert "alert" in css.lower()
    assert "dismissible" in css.lower() or "dismiss" in css.lower()


def test_styles_module_exports():
    """Test that styles module exports correctly."""
    from styles import css, variables

    assert hasattr(css, "get_base_css")
    assert hasattr(css, "get_error_css")
    assert hasattr(variables, "GOLD_PRIMARY")


def test_styles_init():
    """Test that styles __init__ imports work."""
    from styles import get_base_css, get_error_css

    assert callable(get_base_css)
    assert callable(get_error_css)
