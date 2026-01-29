"""Styling modules for Ra'd AI.

This package provides:
- Design tokens (colors, spacing, typography) in variables.py
- CSS generator functions in css.py
"""

from .variables import (
    # Gold colors
    GOLD_PRIMARY,
    GOLD_LIGHT,
    GOLD_DARK,
    GOLD_GRADIENT,
    # Background colors
    BG_DARK,
    BG_CARD,
    BG_CARD_HOVER,
    BG_INPUT,
    # Text colors
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    # Accent colors
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_YELLOW,
    ACCENT_BLUE,
    # Status colors
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_ERROR,
    STATUS_INFO,
    # Typography
    FONT_SIZE_XS,
    FONT_SIZE_SM,
    FONT_SIZE_BASE,
    FONT_SIZE_LG,
    FONT_SIZE_XL,
    FONT_SIZE_2XL,
    # Spacing
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_2XL,
    # Border radius
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    # Shadows
    SHADOW_GOLD,
    SHADOW_CARD,
    SHADOW_FOCUS,
    # Transitions
    TRANSITION_FAST,
    TRANSITION_DEFAULT,
)

from .css import get_base_css, get_error_css

__all__ = [
    # CSS generator functions
    "get_base_css",
    "get_error_css",
    # Gold colors
    "GOLD_PRIMARY",
    "GOLD_LIGHT",
    "GOLD_DARK",
    "GOLD_GRADIENT",
    # Background colors
    "BG_DARK",
    "BG_CARD",
    "BG_CARD_HOVER",
    "BG_INPUT",
    # Text colors
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "TEXT_MUTED",
    # Accent colors
    "ACCENT_GREEN",
    "ACCENT_RED",
    "ACCENT_YELLOW",
    "ACCENT_BLUE",
    # Status colors
    "STATUS_SUCCESS",
    "STATUS_WARNING",
    "STATUS_ERROR",
    "STATUS_INFO",
    # Typography
    "FONT_SIZE_XS",
    "FONT_SIZE_SM",
    "FONT_SIZE_BASE",
    "FONT_SIZE_LG",
    "FONT_SIZE_XL",
    "FONT_SIZE_2XL",
    # Spacing
    "SPACING_XS",
    "SPACING_SM",
    "SPACING_MD",
    "SPACING_LG",
    "SPACING_XL",
    "SPACING_2XL",
    # Border radius
    "RADIUS_SM",
    "RADIUS_MD",
    "RADIUS_LG",
    # Shadows
    "SHADOW_GOLD",
    "SHADOW_CARD",
    "SHADOW_FOCUS",
    # Transitions
    "TRANSITION_FAST",
    "TRANSITION_DEFAULT",
]
