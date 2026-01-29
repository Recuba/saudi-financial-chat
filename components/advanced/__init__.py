"""
Advanced Features Components for Saudi Financial Chat.

This package provides optional advanced features including:
- PyGWalker visual data explorer
- Data profiling with ydata-profiling
- Cookie-based user preferences
- Authentication with streamlit-authenticator

All components gracefully handle missing optional dependencies.
"""

from typing import TYPE_CHECKING

# Import components with availability flags
from components.advanced.visual_explorer import (
    render_visual_explorer,
    prepare_data_for_explorer,
    PYGWALKER_AVAILABLE,
)

from components.advanced.data_profiler import (
    render_data_profiler,
    get_quick_stats,
    check_data_quality,
    generate_profile_report,
    YDATA_PROFILING_AVAILABLE,
)

from components.advanced.user_preferences import (
    get_preferences,
    save_preferences,
    render_preferences_panel,
    DEFAULT_PREFERENCES,
    COOKIES_AVAILABLE,
)

from components.advanced.auth import (
    check_authentication,
    render_login_form,
    render_logout_button,
    require_auth,
    AUTH_AVAILABLE,
)

__all__ = [
    # Visual Explorer
    "render_visual_explorer",
    "prepare_data_for_explorer",
    "PYGWALKER_AVAILABLE",
    # Data Profiler
    "render_data_profiler",
    "get_quick_stats",
    "check_data_quality",
    "generate_profile_report",
    "YDATA_PROFILING_AVAILABLE",
    # User Preferences
    "get_preferences",
    "save_preferences",
    "render_preferences_panel",
    "DEFAULT_PREFERENCES",
    "COOKIES_AVAILABLE",
    # Authentication
    "check_authentication",
    "render_login_form",
    "render_logout_button",
    "require_auth",
    "AUTH_AVAILABLE",
]

__version__ = "1.0.0"
