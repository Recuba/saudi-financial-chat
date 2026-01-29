"""
Visualization Suite for Saudi Financial Chat Application.

This package provides comprehensive charting and visualization components
using ECharts, Plotly, Plost, and Agraph for financial data visualization.

Theme Colors:
    - Gold: #D4A84B, #E8C872, #B8860B
    - Background: #0E0E0E, #1A1A1A
    - Positive: #4CAF50, Negative: #F44336
"""

from typing import TYPE_CHECKING

# Lazy imports to handle optional dependencies gracefully
__all__ = [
    # ECharts components
    "create_candlestick_chart",
    "create_sector_treemap",
    "create_correlation_heatmap",
    "get_echarts_theme",
    "EChartsTheme",
    # Plotly interactive components
    "create_interactive_scatter",
    "create_selectable_bar_chart",
    "create_company_comparison_chart",
    "extract_click_data",
    "PlotlyClickHandler",
    # Sparklines
    "create_sparkline",
    "create_metric_with_sparkline",
    "detect_trend",
    "TrendDirection",
    # Relationship graphs
    "create_company_node",
    "create_relationship_edge",
    "build_ownership_graph",
    "render_relationship_graph",
    "RelationshipType",
    "SECTOR_COLORS",
]

# Theme constants available without imports
THEME_COLORS = {
    "gold_primary": "#D4A84B",
    "gold_light": "#E8C872",
    "gold_dark": "#B8860B",
    "background_dark": "#0E0E0E",
    "background_light": "#1A1A1A",
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#9E9E9E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0B0",
}

# ECharts imports
try:
    from .echarts_charts import (
        create_candlestick_chart,
        create_sector_treemap,
        create_correlation_heatmap,
        get_echarts_theme,
        EChartsTheme,
    )
except ImportError as e:
    import warnings
    warnings.warn(f"ECharts components unavailable: {e}. Install streamlit-echarts.")

    def create_candlestick_chart(*args, **kwargs):
        raise ImportError("streamlit-echarts required for candlestick charts")

    def create_sector_treemap(*args, **kwargs):
        raise ImportError("streamlit-echarts required for treemaps")

    def create_correlation_heatmap(*args, **kwargs):
        raise ImportError("streamlit-echarts required for heatmaps")

    def get_echarts_theme(*args, **kwargs):
        return {}

    class EChartsTheme:
        DARK = "dark"
        LIGHT = "light"

# Plotly imports
try:
    from .plotly_interactive import (
        create_interactive_scatter,
        create_selectable_bar_chart,
        create_company_comparison_chart,
        extract_click_data,
        PlotlyClickHandler,
    )
except ImportError as e:
    import warnings
    warnings.warn(f"Plotly components unavailable: {e}. Install streamlit-plotly-events.")

    def create_interactive_scatter(*args, **kwargs):
        raise ImportError("streamlit-plotly-events required for interactive scatter")

    def create_selectable_bar_chart(*args, **kwargs):
        raise ImportError("streamlit-plotly-events required for bar charts")

    def create_company_comparison_chart(*args, **kwargs):
        raise ImportError("streamlit-plotly-events required for comparison charts")

    def extract_click_data(*args, **kwargs):
        return None

    class PlotlyClickHandler:
        pass

# Sparkline imports
try:
    from .sparklines import (
        create_sparkline,
        create_metric_with_sparkline,
        detect_trend,
        TrendDirection,
    )
except ImportError as e:
    import warnings
    warnings.warn(f"Sparkline components unavailable: {e}. Install plost.")

    def create_sparkline(*args, **kwargs):
        raise ImportError("plost required for sparklines")

    def create_metric_with_sparkline(*args, **kwargs):
        raise ImportError("plost required for sparklines")

    def detect_trend(*args, **kwargs):
        return "flat"

    class TrendDirection:
        UP = "up"
        DOWN = "down"
        FLAT = "flat"

# Relationship graph imports
try:
    from .relationship_graph import (
        create_company_node,
        create_relationship_edge,
        build_ownership_graph,
        render_relationship_graph,
        RelationshipType,
        SECTOR_COLORS,
    )
except ImportError as e:
    import warnings
    warnings.warn(f"Graph components unavailable: {e}. Install streamlit-agraph.")

    def create_company_node(*args, **kwargs):
        raise ImportError("streamlit-agraph required for relationship graphs")

    def create_relationship_edge(*args, **kwargs):
        raise ImportError("streamlit-agraph required for relationship graphs")

    def build_ownership_graph(*args, **kwargs):
        raise ImportError("streamlit-agraph required for relationship graphs")

    def render_relationship_graph(*args, **kwargs):
        raise ImportError("streamlit-agraph required for relationship graphs")

    class RelationshipType:
        OWNS = "owns"
        SUBSIDIARY = "subsidiary"
        PARTNERSHIP = "partnership"

    SECTOR_COLORS = {}


def check_dependencies() -> dict:
    """
    Check which visualization dependencies are available.

    Returns:
        dict: Mapping of dependency name to availability status
    """
    status = {}

    try:
        import streamlit_echarts
        status["echarts"] = True
    except ImportError:
        status["echarts"] = False

    try:
        import streamlit_plotly_events
        status["plotly_events"] = True
    except ImportError:
        status["plotly_events"] = False

    try:
        import plost
        status["plost"] = True
    except ImportError:
        status["plost"] = False

    try:
        import streamlit_agraph
        status["agraph"] = True
    except ImportError:
        status["agraph"] = False

    return status


def get_installation_instructions() -> str:
    """
    Get pip installation instructions for missing dependencies.

    Returns:
        str: Installation command for missing packages
    """
    status = check_dependencies()
    missing = []

    package_map = {
        "echarts": "streamlit-echarts",
        "plotly_events": "streamlit-plotly-events",
        "plost": "plost",
        "agraph": "streamlit-agraph",
    }

    for key, available in status.items():
        if not available:
            missing.append(package_map[key])

    if missing:
        return f"pip install {' '.join(missing)}"
    return "All visualization dependencies are installed."
