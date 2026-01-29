"""Auto-visualization for query responses."""

import re
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None


CHART_KEYWORDS = [
    "chart", "plot", "graph", "visualize", "visualization",
    "bar", "pie", "line", "trend", "compare", "comparison",
    "show me", "display", "draw"
]


def should_render_chart(query: str) -> bool:
    """Detect if query requests a chart.

    Args:
        query: The user's query string

    Returns:
        True if the query appears to request a chart visualization
    """
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in CHART_KEYWORDS)


def detect_chart_type(query: str) -> str:
    """Detect what type of chart is requested.

    Args:
        query: The user's query string

    Returns:
        Chart type: "pie", "line", "bar", or "auto"
    """
    query_lower = query.lower()
    if "pie" in query_lower:
        return "pie"
    elif "line" in query_lower or "trend" in query_lower or "over time" in query_lower:
        return "line"
    elif "bar" in query_lower:
        return "bar"
    return "auto"


def infer_chart_columns(df: "pd.DataFrame", query: str) -> Tuple[str, str]:
    """Infer x and y columns from dataframe and query.

    Args:
        df: The DataFrame to visualize
        query: The user's query string

    Returns:
        Tuple of (x_column, y_column) names
    """
    if pd is None:
        return ("", "")

    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    string_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Default selections
    x_col = string_cols[0] if string_cols else cols[0]
    y_col = numeric_cols[0] if numeric_cols else cols[-1]

    # Try to match column names mentioned in the query
    query_lower = query.lower()
    for col in cols:
        if col.lower() in query_lower:
            if col in numeric_cols:
                y_col = col
            else:
                x_col = col

    return (x_col, y_col)


def create_bar_chart(
    df: "pd.DataFrame",
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None
) -> Any:
    """Create a styled bar chart.

    Args:
        df: The DataFrame to visualize
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column for color grouping

    Returns:
        Plotly figure object
    """
    if px is None:
        raise ImportError("plotly required for charts")

    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color=color,
        color_discrete_sequence=["#D4A84B"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8E8"),
        title_font=dict(color="#D4A84B"),
    )
    return fig


def create_pie_chart(
    df: "pd.DataFrame",
    names: str,
    values: str,
    title: str = ""
) -> Any:
    """Create a styled pie chart.

    Args:
        df: The DataFrame to visualize
        names: Column name for pie slice names
        values: Column name for pie slice values
        title: Chart title

    Returns:
        Plotly figure object
    """
    if px is None:
        raise ImportError("plotly required")

    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8E8")
    )
    return fig


def create_line_chart(
    df: "pd.DataFrame",
    x: str,
    y: str,
    title: str = ""
) -> Any:
    """Create a styled line chart.

    Args:
        df: The DataFrame to visualize
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title

    Returns:
        Plotly figure object
    """
    if px is None:
        raise ImportError("plotly required")

    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=["#D4A84B"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8E8"),
    )
    return fig


def auto_visualize(df: "pd.DataFrame", query: str) -> Optional[Any]:
    """Automatically create appropriate visualization.

    Analyzes the query and dataframe to determine the best chart type
    and automatically select appropriate columns.

    Args:
        df: The DataFrame to visualize
        query: The user's query string

    Returns:
        Plotly figure object or None if visualization cannot be created
    """
    if df is None or len(df) == 0:
        return None

    chart_type = detect_chart_type(query)
    x_col, y_col = infer_chart_columns(df, query)
    title = f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}"

    try:
        if chart_type == "pie":
            return create_pie_chart(df, names=x_col, values=y_col, title=title)
        elif chart_type == "line":
            return create_line_chart(df, x=x_col, y=y_col, title=title)
        else:
            # Default to bar chart for "bar" and "auto"
            return create_bar_chart(df, x=x_col, y=y_col, title=title)
    except Exception:
        return None
