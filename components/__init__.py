"""
Saudi Financial Chat Components Package
========================================
A UI component library for the Saudi Financial Chat application.

Core components (always available):
- chat: Chat input, response handling
- sidebar: Sidebar with database info and controls
- example_questions: Example question cards
- error_display: Error formatting and display

Enhanced components (optional, require additional packages):
- tables: AG-Grid, ITables, metric cards
- navigation: Option menu, antd layout
- filters: Dynamic filters, tree selectors
- visualizations: ECharts, Plotly, sparklines
- advanced: PyGWalker, data profiling, auth
"""

from typing import Dict, List

# ============================================================================
# Core Components (always available - used by app.py)
# ============================================================================
from .chat import (
    format_response,
    render_chat_input,
    render_user_message,
    render_ai_response,
    process_query,
    render_chat_with_response,
    initialize_chat_history,
    add_to_chat_history,
    get_chat_history,
    clear_chat_history,
    render_chat_history,
    render_clear_history_button,
)

from .sidebar import (
    render_sidebar,
    render_database_info,
    render_column_reference,
    render_view_info,
    render_llm_status,
)

from .example_questions import (
    render_example_questions,
    render_example_questions_minimal,
    EXAMPLE_QUESTIONS,
)

from .error_display import (
    format_api_error,
    render_error_banner,
    render_api_key_setup_guide,
)

from .status_indicator import (
    render_loading_state,
    render_status_badge,
    render_dependency_status,
    check_optional_dependencies,
)

from .session_manager import (
    SESSION_DEFAULTS,
    initialize_session,
    get_session_defaults,
    get_session_value,
    set_session_value,
    add_favorite_query,
    remove_favorite_query,
    get_favorite_queries,
    add_recent_query,
    get_recent_queries,
    clear_recent_queries,
    render_favorites_section,
    render_recent_queries_section,
    save_filter_state,
    get_filter_state,
    set_selected_dataset,
    get_selected_dataset,
)


# ============================================================================
# Enhanced Components (lazy loading - only import when accessed)
# ============================================================================

# Flags for optional dependencies
TABLES_AVAILABLE = False
NAVIGATION_AVAILABLE = False
FILTERS_AVAILABLE = False
VISUALIZATIONS_AVAILABLE = False
ADVANCED_AVAILABLE = False
CHAT_ENHANCED_AVAILABLE = False

def _try_import_tables():
    """Lazily import tables components."""
    global TABLES_AVAILABLE
    try:
        from .tables import (
            FinancialGrid, create_financial_grid, AGGRID_AVAILABLE,
            InteractiveTable, create_interactive_table, ITABLES_AVAILABLE,
            MetricCard, MetricConfig, MetricsRow,
            format_number_abbreviated, format_sar_currency,
            calculate_delta_percentage, create_financial_metrics,
            create_company_metrics_summary, STREAMLIT_EXTRAS_AVAILABLE,
        )
        TABLES_AVAILABLE = True
        return True
    except ImportError:
        return False

def _try_import_navigation():
    """Lazily import navigation components."""
    global NAVIGATION_AVAILABLE
    try:
        from .navigation import (
            render_main_nav, render_sidebar_nav, render_horizontal_nav,
            NavItem, NAV_ICONS, MAIN_NAV_AVAILABLE,
            render_tabs, render_metric_card, render_metric_row,
            render_card, render_segmented_control, render_steps,
            render_alert, render_divider, render_empty_state,
            inject_layout_css, TabItem, AlertType, CardSize,
            StepItem, LAYOUT_AVAILABLE,
        )
        NAVIGATION_AVAILABLE = True
        return True
    except ImportError:
        return False

def _try_import_enhanced():
    """Lazily import all enhanced components."""
    _try_import_tables()
    _try_import_navigation()


# ============================================================================
# Package Metadata
# ============================================================================

__version__ = "1.0.0"
__author__ = "Saudi Financial Chat Team"

__all__ = [
    # Core - Chat
    "format_response",
    "render_chat_input",
    "render_user_message",
    "render_ai_response",
    "process_query",
    "render_chat_with_response",
    "initialize_chat_history",
    "add_to_chat_history",
    "get_chat_history",
    "clear_chat_history",
    "render_chat_history",
    "render_clear_history_button",
    # Core - Sidebar
    "render_sidebar",
    "render_database_info",
    "render_column_reference",
    "render_view_info",
    "render_llm_status",
    # Core - Example questions
    "render_example_questions",
    "render_example_questions_minimal",
    "EXAMPLE_QUESTIONS",
    # Core - Error display
    "format_api_error",
    "render_error_banner",
    "render_api_key_setup_guide",
    # Core - Status
    "render_loading_state",
    "render_status_badge",
    "render_dependency_status",
    "check_optional_dependencies",
    # Core - Session management
    "SESSION_DEFAULTS",
    "initialize_session",
    "get_session_defaults",
    "get_session_value",
    "set_session_value",
    "add_favorite_query",
    "remove_favorite_query",
    "get_favorite_queries",
    "add_recent_query",
    "get_recent_queries",
    "clear_recent_queries",
    "render_favorites_section",
    "render_recent_queries_section",
    "save_filter_state",
    "get_filter_state",
    "set_selected_dataset",
    "get_selected_dataset",
]
