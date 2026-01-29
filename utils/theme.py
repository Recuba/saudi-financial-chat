"""
Theme Detection and Chart Color Utilities
==========================================
Provides theme detection using streamlit-theme and color palette utilities
for consistent chart styling across the Saudi Financial Chat application.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import streamlit as st

# Try to import streamlit-theme for theme detection
try:
    from streamlit_theme import st_theme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


@dataclass(frozen=True)
class ThemeColors:
    """Immutable container for theme color values."""
    gold_primary: str = "#D4A84B"
    gold_light: str = "#E8C872"
    gold_dark: str = "#B8860B"
    bg_dark: str = "#0E0E0E"
    bg_card: str = "#1A1A1A"
    bg_card_hover: str = "#252525"
    bg_input: str = "#2A2A2A"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#B0B0B0"
    text_muted: str = "#707070"
    accent_green: str = "#4CAF50"
    accent_red: str = "#F44336"
    accent_blue: str = "#2196F3"
    accent_purple: str = "#9C27B0"
    accent_orange: str = "#FF9800"
    accent_cyan: str = "#00BCD4"


# Default theme colors instance
COLORS = ThemeColors()


def detect_theme() -> Dict[str, Any]:
    """
    Detect the current Streamlit theme settings.

    Uses streamlit-theme package if available, otherwise falls back to
    default dark theme values based on the app configuration.

    Returns:
        Dict containing theme properties:
        - base: "dark" or "light"
        - primaryColor: Primary accent color
        - backgroundColor: Main background color
        - secondaryBackgroundColor: Secondary/card background
        - textColor: Primary text color
    """
    if THEME_AVAILABLE:
        try:
            theme = st_theme()
            if theme is not None:
                return {
                    "base": theme.get("base", "dark"),
                    "primaryColor": theme.get("primaryColor", COLORS.gold_primary),
                    "backgroundColor": theme.get("backgroundColor", COLORS.bg_dark),
                    "secondaryBackgroundColor": theme.get("secondaryBackgroundColor", COLORS.bg_card),
                    "textColor": theme.get("textColor", COLORS.text_primary),
                }
        except Exception:
            pass

    # Fallback to default dark theme
    return {
        "base": "dark",
        "primaryColor": COLORS.gold_primary,
        "backgroundColor": COLORS.bg_dark,
        "secondaryBackgroundColor": COLORS.bg_card,
        "textColor": COLORS.text_primary,
    }


def is_dark_theme() -> bool:
    """
    Check if the current theme is dark.

    Returns:
        True if dark theme is active, False otherwise.
    """
    theme = detect_theme()
    return theme.get("base", "dark") == "dark"


def get_chart_colors(n_colors: int = 10) -> List[str]:
    """
    Get a list of chart-friendly colors matching the app theme.

    The color palette starts with gold (brand color) and includes
    complementary colors that work well on dark backgrounds.

    Args:
        n_colors: Number of colors to return (max 10, will cycle if more needed).

    Returns:
        List of hex color strings.
    """
    palette = [
        COLORS.gold_primary,      # Gold (primary brand)
        COLORS.accent_blue,       # Blue
        COLORS.accent_green,      # Green
        COLORS.accent_orange,     # Orange
        COLORS.accent_purple,     # Purple
        COLORS.accent_cyan,       # Cyan
        COLORS.accent_red,        # Red
        COLORS.gold_light,        # Light gold
        COLORS.text_secondary,    # Gray
        COLORS.gold_dark,         # Dark gold
    ]

    # Cycle colors if more than available are requested
    if n_colors <= len(palette):
        return palette[:n_colors]

    result = []
    for i in range(n_colors):
        result.append(palette[i % len(palette)])
    return result


def get_plotly_template() -> Dict[str, Any]:
    """
    Get a Plotly template configuration matching the app theme.

    Returns a template dict that can be used with plotly.io.templates
    or passed directly to figure layout.

    Returns:
        Dict containing Plotly layout configuration.
    """
    is_dark = is_dark_theme()

    if is_dark:
        return {
            "layout": {
                "paper_bgcolor": COLORS.bg_dark,
                "plot_bgcolor": COLORS.bg_card,
                "font": {
                    "color": COLORS.text_primary,
                    "family": "Tajawal, sans-serif",
                },
                "title": {
                    "font": {
                        "color": COLORS.gold_primary,
                        "size": 18,
                    }
                },
                "xaxis": {
                    "gridcolor": COLORS.bg_card_hover,
                    "linecolor": COLORS.text_muted,
                    "tickcolor": COLORS.text_muted,
                    "title": {"font": {"color": COLORS.text_secondary}},
                    "tickfont": {"color": COLORS.text_secondary},
                },
                "yaxis": {
                    "gridcolor": COLORS.bg_card_hover,
                    "linecolor": COLORS.text_muted,
                    "tickcolor": COLORS.text_muted,
                    "title": {"font": {"color": COLORS.text_secondary}},
                    "tickfont": {"color": COLORS.text_secondary},
                },
                "legend": {
                    "bgcolor": "rgba(26, 26, 26, 0.8)",
                    "bordercolor": COLORS.gold_dark,
                    "font": {"color": COLORS.text_primary},
                },
                "colorway": get_chart_colors(10),
            }
        }
    else:
        # Light theme fallback
        return {
            "layout": {
                "paper_bgcolor": "#FFFFFF",
                "plot_bgcolor": "#F5F5F5",
                "font": {
                    "color": "#333333",
                    "family": "Tajawal, sans-serif",
                },
                "title": {
                    "font": {
                        "color": COLORS.gold_dark,
                        "size": 18,
                    }
                },
                "colorway": get_chart_colors(10),
            }
        }


def get_altair_theme() -> Dict[str, Any]:
    """
    Get an Altair theme configuration matching the app theme.

    Returns:
        Dict containing Altair theme configuration.
    """
    is_dark = is_dark_theme()

    if is_dark:
        return {
            "config": {
                "background": COLORS.bg_dark,
                "view": {
                    "fill": COLORS.bg_card,
                    "stroke": COLORS.bg_card_hover,
                },
                "title": {
                    "color": COLORS.gold_primary,
                    "font": "Tajawal, sans-serif",
                    "fontSize": 16,
                },
                "axis": {
                    "domainColor": COLORS.text_muted,
                    "gridColor": COLORS.bg_card_hover,
                    "labelColor": COLORS.text_secondary,
                    "tickColor": COLORS.text_muted,
                    "titleColor": COLORS.text_secondary,
                },
                "legend": {
                    "labelColor": COLORS.text_primary,
                    "titleColor": COLORS.gold_light,
                },
                "range": {
                    "category": get_chart_colors(10),
                },
            }
        }
    else:
        return {
            "config": {
                "background": "#FFFFFF",
                "range": {
                    "category": get_chart_colors(10),
                },
            }
        }


def get_matplotlib_style() -> Dict[str, Any]:
    """
    Get matplotlib rcParams matching the app theme.

    Can be applied using: plt.rcParams.update(get_matplotlib_style())

    Returns:
        Dict of matplotlib rcParams.
    """
    is_dark = is_dark_theme()

    if is_dark:
        return {
            "figure.facecolor": COLORS.bg_dark,
            "axes.facecolor": COLORS.bg_card,
            "axes.edgecolor": COLORS.text_muted,
            "axes.labelcolor": COLORS.text_secondary,
            "axes.titlecolor": COLORS.gold_primary,
            "text.color": COLORS.text_primary,
            "xtick.color": COLORS.text_secondary,
            "ytick.color": COLORS.text_secondary,
            "grid.color": COLORS.bg_card_hover,
            "legend.facecolor": COLORS.bg_card,
            "legend.edgecolor": COLORS.gold_dark,
            "axes.prop_cycle": f"cycler('color', {get_chart_colors(10)})",
        }
    else:
        return {
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#F5F5F5",
            "axes.prop_cycle": f"cycler('color', {get_chart_colors(10)})",
        }


def apply_chart_theme_css() -> None:
    """
    Inject CSS to style chart containers in the Streamlit app.

    This adds custom styling for chart wrappers and ensures
    consistent appearance across different chart libraries.
    """
    css = f"""
    <style>
    /* Chart Container Styling */
    .stPlotlyChart, .stAltairChart, .stPyplot {{
        background: {COLORS.bg_card} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid rgba(212, 168, 75, 0.2) !important;
    }}

    .stPlotlyChart:hover, .stAltairChart:hover, .stPyplot:hover {{
        border-color: {COLORS.gold_primary} !important;
        box-shadow: 0 4px 20px rgba(212, 168, 75, 0.15) !important;
    }}

    /* Vega-Lite (Altair) specific */
    .vega-embed {{
        background: transparent !important;
    }}

    .vega-embed .vega-actions a {{
        color: {COLORS.gold_light} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def color_scale(
    value: float,
    min_val: float = 0.0,
    max_val: float = 1.0,
    low_color: Optional[str] = None,
    high_color: Optional[str] = None,
) -> str:
    """
    Generate a color on a gradient scale based on a value.

    Useful for conditional formatting in tables or heatmaps.

    Args:
        value: The value to map to a color.
        min_val: Minimum value of the scale.
        max_val: Maximum value of the scale.
        low_color: Color for low values (default: accent_red).
        high_color: Color for high values (default: accent_green).

    Returns:
        Hex color string.
    """
    low_color = low_color or COLORS.accent_red
    high_color = high_color or COLORS.accent_green

    # Normalize value to 0-1 range
    if max_val == min_val:
        ratio = 0.5
    else:
        ratio = max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    # Parse colors
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    low_rgb = hex_to_rgb(low_color)
    high_rgb = hex_to_rgb(high_color)

    # Interpolate
    result_rgb = tuple(
        int(low_rgb[i] + ratio * (high_rgb[i] - low_rgb[i]))
        for i in range(3)
    )

    return rgb_to_hex(result_rgb)


def get_status_color(status: str) -> str:
    """
    Get a color for a status indicator.

    Args:
        status: Status string (e.g., "positive", "negative", "neutral").

    Returns:
        Hex color string.
    """
    status_map = {
        "positive": COLORS.accent_green,
        "negative": COLORS.accent_red,
        "neutral": COLORS.text_muted,
        "warning": COLORS.accent_orange,
        "info": COLORS.accent_blue,
        "success": COLORS.accent_green,
        "error": COLORS.accent_red,
        "gold": COLORS.gold_primary,
    }
    return status_map.get(status.lower(), COLORS.text_muted)
