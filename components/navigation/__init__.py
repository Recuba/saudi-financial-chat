"""
Navigation Components Package
==============================
Provides navigation components for the Saudi Financial Chat application,
including main navigation menu and layout components.

Components:
- MainNav: Primary navigation using streamlit-option-menu
- Layout: Antd-based layout components (tabs, cards, etc.)
"""

from typing import List, Optional, Dict, Any

# Import main navigation components with fallback handling
try:
    from .main_nav import (
        render_main_nav,
        render_sidebar_nav,
        render_horizontal_nav,
        NavItem,
        NAV_ICONS,
    )
    MAIN_NAV_AVAILABLE = True
except ImportError as e:
    MAIN_NAV_AVAILABLE = False
    _main_nav_error = str(e)

    # Provide stub implementations
    class NavItem:
        """Stub NavItem when main_nav not available."""
        def __init__(self, *args, **kwargs):
            pass

    NAV_ICONS = {}

    def render_main_nav(*args, **kwargs) -> Optional[str]:
        """Stub render_main_nav."""
        return None

    def render_sidebar_nav(*args, **kwargs) -> Optional[str]:
        """Stub render_sidebar_nav."""
        return None

    def render_horizontal_nav(*args, **kwargs) -> Optional[str]:
        """Stub render_horizontal_nav."""
        return None


# Import layout components with fallback handling
try:
    from .layout import (
        render_tabs,
        render_metric_card,
        render_metric_row,
        render_card,
        render_segmented_control,
        render_steps,
        render_alert,
        render_divider,
        render_empty_state,
        inject_layout_css,
        TabItem,
        MetricConfig,
        AlertType,
        CardSize,
        StepItem,
    )
    LAYOUT_AVAILABLE = True
except ImportError as e:
    LAYOUT_AVAILABLE = False
    _layout_error = str(e)

    # Provide stub implementations
    class TabItem:
        """Stub TabItem when layout not available."""
        def __init__(self, *args, **kwargs):
            pass

    class MetricConfig:
        """Stub MetricConfig when layout not available."""
        def __init__(self, *args, **kwargs):
            pass

    def render_tabs(*args, **kwargs) -> Optional[str]:
        """Stub render_tabs."""
        return None

    def render_metric_card(*args, **kwargs) -> None:
        """Stub render_metric_card."""
        pass

    def render_metric_row(*args, **kwargs) -> None:
        """Stub render_metric_row."""
        pass

    def render_card(*args, **kwargs) -> None:
        """Stub render_card."""
        pass

    def render_segmented_control(*args, **kwargs) -> Optional[str]:
        """Stub render_segmented_control."""
        return None

    def render_steps(*args, **kwargs) -> None:
        """Stub render_steps."""
        pass

    def render_alert(*args, **kwargs) -> None:
        """Stub render_alert."""
        pass


def check_dependencies() -> Dict[str, bool]:
    """
    Check availability of navigation component dependencies.

    Returns:
        Dict mapping component names to availability status.
    """
    return {
        "main_nav": MAIN_NAV_AVAILABLE,
        "layout": LAYOUT_AVAILABLE,
        "streamlit_option_menu": _check_option_menu(),
        "streamlit_antd_components": _check_antd(),
    }


def _check_option_menu() -> bool:
    """Check if streamlit-option-menu is installed."""
    try:
        import streamlit_option_menu
        return True
    except ImportError:
        return False


def _check_antd() -> bool:
    """Check if streamlit-antd-components is installed."""
    try:
        import streamlit_antd_components
        return True
    except ImportError:
        return False


def get_missing_dependencies() -> List[str]:
    """
    Get list of missing optional dependencies.

    Returns:
        List of pip package names that need to be installed.
    """
    missing = []

    if not _check_option_menu():
        missing.append("streamlit-option-menu")

    if not _check_antd():
        missing.append("streamlit-antd-components")

    return missing


def show_dependency_warning() -> None:
    """
    Display a warning about missing dependencies.

    Shows installation instructions for any missing packages.
    """
    import streamlit as st

    missing = get_missing_dependencies()

    if missing:
        st.warning(
            f"Some navigation components require additional packages. "
            f"Install with: `pip install {' '.join(missing)}`"
        )


__all__ = [
    # Main navigation
    "render_main_nav",
    "render_sidebar_nav",
    "render_horizontal_nav",
    "NavItem",
    "NAV_ICONS",
    "MAIN_NAV_AVAILABLE",
    # Layout
    "render_tabs",
    "render_metric_card",
    "render_metric_row",
    "render_card",
    "render_segmented_control",
    "render_steps",
    "render_alert",
    "render_divider",
    "render_empty_state",
    "inject_layout_css",
    "TabItem",
    "MetricConfig",
    "AlertType",
    "CardSize",
    "StepItem",
    "LAYOUT_AVAILABLE",
    # Utilities
    "check_dependencies",
    "get_missing_dependencies",
    "show_dependency_warning",
]
