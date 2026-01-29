"""
Saudi Financial Chat Components Package
========================================
A comprehensive UI component library for the Saudi Financial Chat application.

This package provides reusable, themed components for building financial
analytics dashboards with Streamlit, featuring:

- Navigation: Option menu and antd-based layout components
- Tables: AG-Grid, ITables, and metric cards
- Chat: Message rendering, code display, and feedback
- Filters: Dynamic filters, tree selectors, and date pickers
- Visualizations: ECharts, Plotly, sparklines, and relationship graphs
- Advanced: PyGWalker, data profiling, cookies, and authentication

Theme Colors:
    - Gold: #D4A84B, #E8C872, #B8860B
    - Background: #0E0E0E, #1A1A1A
    - Positive: #4CAF50, Negative: #F44336
"""

from typing import Dict, List

# ============================================================================
# Tables Components
# ============================================================================
from .tables import (
    # Financial Grid (AG-Grid)
    FinancialGrid,
    create_financial_grid,
    AGGRID_AVAILABLE,
    # Interactive Table (ITables)
    InteractiveTable,
    create_interactive_table,
    ITABLES_AVAILABLE,
    # Metrics
    MetricCard,
    MetricConfig,
    MetricsRow,
    format_number_abbreviated,
    format_sar_currency,
    calculate_delta_percentage,
    create_financial_metrics,
    create_company_metrics_summary,
    STREAMLIT_EXTRAS_AVAILABLE,
)

# ============================================================================
# Navigation Components
# ============================================================================
from .navigation import (
    # Main navigation
    render_main_nav,
    render_sidebar_nav,
    render_horizontal_nav,
    NavItem,
    NAV_ICONS,
    MAIN_NAV_AVAILABLE,
    # Layout (antd-based)
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
    AlertType,
    CardSize,
    StepItem,
    LAYOUT_AVAILABLE,
)

# ============================================================================
# Chat Components (Enhanced)
# ============================================================================
from .chat_enhanced import (
    # Messages
    ChatMessage,
    render_message,
    render_chat_history as render_enhanced_chat_history,
    add_message_to_history,
    clear_chat_history as clear_enhanced_chat_history,
    get_chat_history as get_enhanced_chat_history,
    # Code Display
    CodeDisplay,
    render_code,
    detect_language,
    copy_code_button,
    # Feedback
    FeedbackRecord,
    FeedbackWidget,
    render_star_rating,
    get_feedback_history,
    save_feedback,
)

# ============================================================================
# Chat Components (Core - used by app.py)
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

# ============================================================================
# Filter Components
# ============================================================================
from .filters import (
    # Dynamic Filters
    DynamicFilterManager,
    extract_filter_options,
    apply_filters,
    render_filter_summary,
    render_dynamic_filters,
    clear_all_filters,
    # Tree Selector
    TreeSelectorManager,
    build_tree_structure,
    extract_selected_values,
    render_tree_selector,
    render_cascading_selectors,
    # Date Picker
    DatePickerManager,
    fiscal_year_to_date_range,
    get_date_presets,
    render_date_range_picker,
    render_fiscal_year_selector,
    render_quick_date_presets,
)

# ============================================================================
# Visualization Components
# ============================================================================
from .visualizations import (
    # ECharts
    create_candlestick_chart,
    create_sector_treemap,
    create_correlation_heatmap,
    get_echarts_theme,
    EChartsTheme,
    # Plotly Interactive
    create_interactive_scatter,
    create_selectable_bar_chart,
    create_company_comparison_chart,
    extract_click_data,
    PlotlyClickHandler,
    # Sparklines
    create_sparkline,
    create_metric_with_sparkline,
    detect_trend,
    TrendDirection,
    # Relationship Graphs
    create_company_node,
    create_relationship_edge,
    build_ownership_graph,
    render_relationship_graph,
    RelationshipType,
    SECTOR_COLORS,
    THEME_COLORS,
)

# ============================================================================
# Advanced Features
# ============================================================================
from .advanced import (
    # Visual Explorer (PyGWalker)
    render_visual_explorer,
    prepare_data_for_explorer,
    PYGWALKER_AVAILABLE,
    # Data Profiler
    render_data_profiler,
    get_quick_stats,
    check_data_quality,
    generate_profile_report,
    YDATA_PROFILING_AVAILABLE,
    # User Preferences (Cookies)
    get_preferences,
    save_preferences,
    render_preferences_panel,
    DEFAULT_PREFERENCES,
    COOKIES_AVAILABLE,
    # Authentication
    check_authentication,
    render_login_form,
    render_logout_button,
    require_auth,
    AUTH_AVAILABLE,
)


# ============================================================================
# Package Utilities
# ============================================================================

def check_all_dependencies() -> Dict[str, bool]:
    """
    Check availability of all optional dependencies.

    Returns:
        Dict mapping component/package names to availability status.
    """
    return {
        # Tables
        "aggrid": AGGRID_AVAILABLE,
        "itables": ITABLES_AVAILABLE,
        "streamlit_extras": STREAMLIT_EXTRAS_AVAILABLE,
        # Navigation
        "option_menu": MAIN_NAV_AVAILABLE,
        "antd_components": LAYOUT_AVAILABLE,
        # Advanced
        "pygwalker": PYGWALKER_AVAILABLE,
        "ydata_profiling": YDATA_PROFILING_AVAILABLE,
        "cookies": COOKIES_AVAILABLE,
        "authenticator": AUTH_AVAILABLE,
    }


def get_missing_dependencies() -> List[str]:
    """
    Get list of missing optional dependencies with pip install commands.

    Returns:
        List of pip package names that could be installed.
    """
    package_map = {
        "aggrid": "streamlit-aggrid",
        "itables": "itables",
        "streamlit_extras": "streamlit-extras",
        "option_menu": "streamlit-option-menu",
        "antd_components": "streamlit-antd-components",
        "pygwalker": "pygwalker",
        "ydata_profiling": "ydata-profiling",
        "cookies": "streamlit-cookies-controller",
        "authenticator": "streamlit-authenticator",
    }

    status = check_all_dependencies()
    return [package_map[key] for key, available in status.items() if not available]


def show_dependency_status() -> None:
    """
    Display dependency status in Streamlit.

    Shows which optional packages are installed and provides
    installation commands for missing ones.
    """
    import streamlit as st

    status = check_all_dependencies()
    missing = get_missing_dependencies()

    with st.expander("📦 Component Dependencies", expanded=False):
        cols = st.columns(3)
        items = list(status.items())

        for i, (name, available) in enumerate(items):
            with cols[i % 3]:
                icon = "✅" if available else "❌"
                st.write(f"{icon} {name.replace('_', ' ').title()}")

        if missing:
            st.divider()
            st.code(f"pip install {' '.join(missing)}", language="bash")


# ============================================================================
# Package Metadata
# ============================================================================

__version__ = "1.0.0"
__author__ = "Saudi Financial Chat Team"

__all__ = [
    # ---- Tables ----
    "FinancialGrid",
    "create_financial_grid",
    "AGGRID_AVAILABLE",
    "InteractiveTable",
    "create_interactive_table",
    "ITABLES_AVAILABLE",
    "MetricCard",
    "MetricConfig",
    "MetricsRow",
    "format_number_abbreviated",
    "format_sar_currency",
    "calculate_delta_percentage",
    "create_financial_metrics",
    "create_company_metrics_summary",
    "STREAMLIT_EXTRAS_AVAILABLE",
    # ---- Navigation ----
    "render_main_nav",
    "render_sidebar_nav",
    "render_horizontal_nav",
    "NavItem",
    "NAV_ICONS",
    "MAIN_NAV_AVAILABLE",
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
    "AlertType",
    "CardSize",
    "StepItem",
    "LAYOUT_AVAILABLE",
    # ---- Chat ----
    "ChatMessage",
    "render_message",
    "render_chat_history",
    "add_message_to_history",
    "clear_chat_history",
    "get_chat_history",
    "CodeDisplay",
    "render_code",
    "detect_language",
    "copy_code_button",
    "FeedbackRecord",
    "FeedbackWidget",
    "render_star_rating",
    "get_feedback_history",
    "save_feedback",
    # ---- Filters ----
    "DynamicFilterManager",
    "extract_filter_options",
    "apply_filters",
    "render_filter_summary",
    "render_dynamic_filters",
    "clear_all_filters",
    "TreeSelectorManager",
    "build_tree_structure",
    "extract_selected_values",
    "render_tree_selector",
    "render_cascading_selectors",
    "DatePickerManager",
    "fiscal_year_to_date_range",
    "get_date_presets",
    "render_date_range_picker",
    "render_fiscal_year_selector",
    "render_quick_date_presets",
    # ---- Visualizations ----
    "create_candlestick_chart",
    "create_sector_treemap",
    "create_correlation_heatmap",
    "get_echarts_theme",
    "EChartsTheme",
    "create_interactive_scatter",
    "create_selectable_bar_chart",
    "create_company_comparison_chart",
    "extract_click_data",
    "PlotlyClickHandler",
    "create_sparkline",
    "create_metric_with_sparkline",
    "detect_trend",
    "TrendDirection",
    "create_company_node",
    "create_relationship_edge",
    "build_ownership_graph",
    "render_relationship_graph",
    "RelationshipType",
    "SECTOR_COLORS",
    "THEME_COLORS",
    # ---- Advanced ----
    "render_visual_explorer",
    "prepare_data_for_explorer",
    "PYGWALKER_AVAILABLE",
    "render_data_profiler",
    "get_quick_stats",
    "check_data_quality",
    "generate_profile_report",
    "YDATA_PROFILING_AVAILABLE",
    "get_preferences",
    "save_preferences",
    "render_preferences_panel",
    "DEFAULT_PREFERENCES",
    "COOKIES_AVAILABLE",
    "check_authentication",
    "render_login_form",
    "render_logout_button",
    "require_auth",
    "AUTH_AVAILABLE",
    # ---- Utilities ----
    "check_all_dependencies",
    "get_missing_dependencies",
    "show_dependency_status",
]
