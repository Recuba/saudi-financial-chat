"""
Plotly Interactive Visualization Components.

Provides scatter plots, bar charts, and comparison charts with click event
handling using the streamlit-plotly-events library.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd

# Optional dependency guard
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from streamlit_plotly_events import plotly_events
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    px = None
    plotly_events = None


# Saudi Financial theme color palette
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
    "grid_line": "#333333",
}

# Color sequence for multi-series charts
COLOR_SEQUENCE = [
    "#D4A84B",  # Gold
    "#4CAF50",  # Green
    "#2196F3",  # Blue
    "#9C27B0",  # Purple
    "#FF9800",  # Orange
    "#00BCD4",  # Cyan
    "#E91E63",  # Pink
    "#795548",  # Brown
    "#607D8B",  # Gray Blue
    "#8BC34A",  # Light Green
]


@dataclass
class PlotlyClickHandler:
    """
    Handler for managing Plotly click events and selections.

    Attributes:
        selected_points: List of currently selected point data
        click_callback: Optional callback function for click events
        selection_mode: 'single' or 'multi' selection mode
    """
    selected_points: List[Dict[str, Any]] = field(default_factory=list)
    click_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    selection_mode: str = "single"

    def handle_click(self, click_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Process click event data from plotly_events.

        Args:
            click_data: Raw click data from plotly_events

        Returns:
            Processed click data or None if no click
        """
        if not click_data:
            return None

        point = click_data[0]
        processed = extract_click_data(click_data)

        if self.selection_mode == "single":
            self.selected_points = [processed] if processed else []
        else:
            if processed:
                # Toggle selection
                existing = next(
                    (p for p in self.selected_points
                     if p.get("x") == processed.get("x") and p.get("y") == processed.get("y")),
                    None
                )
                if existing:
                    self.selected_points.remove(existing)
                else:
                    self.selected_points.append(processed)

        if self.click_callback and processed:
            self.click_callback(processed)

        return processed

    def clear_selection(self) -> None:
        """Clear all selected points."""
        self.selected_points = []

    def get_selected_values(self, key: str = "customdata") -> List[Any]:
        """
        Get values from selected points.

        Args:
            key: Data key to extract

        Returns:
            List of values for the specified key
        """
        return [p.get(key) for p in self.selected_points if key in p]


def extract_click_data(click_data: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    """
    Extract and normalize click data from plotly_events response.

    Args:
        click_data: Raw click data from plotly_events

    Returns:
        Normalized dict with x, y, pointIndex, curveNumber, customdata
        or None if no valid click data
    """
    if not click_data or len(click_data) == 0:
        return None

    point = click_data[0]

    return {
        "x": point.get("x"),
        "y": point.get("y"),
        "pointIndex": point.get("pointIndex", point.get("pointNumber")),
        "curveNumber": point.get("curveNumber", 0),
        "customdata": point.get("customdata"),
        "text": point.get("text"),
        "raw": point,
    }


def _apply_theme(fig: "go.Figure", dark_mode: bool = True) -> "go.Figure":
    """
    Apply Saudi Financial theme to a Plotly figure.

    Args:
        fig: Plotly figure object
        dark_mode: Whether to use dark mode styling

    Returns:
        Styled figure
    """
    bg_color = THEME_COLORS["background_dark"] if dark_mode else "#FFFFFF"
    paper_color = THEME_COLORS["background_dark"] if dark_mode else "#FFFFFF"
    text_color = THEME_COLORS["text_primary"] if dark_mode else "#333333"
    grid_color = THEME_COLORS["grid_line"] if dark_mode else "#EEEEEE"

    fig.update_layout(
        paper_bgcolor=paper_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, family="Inter, sans-serif"),
        title_font=dict(color=THEME_COLORS["gold_primary"], size=18),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME_COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor=THEME_COLORS["background_light"],
            font_size=12,
            font_color=THEME_COLORS["text_primary"],
            bordercolor=THEME_COLORS["gold_dark"],
        ),
    )

    fig.update_xaxes(
        gridcolor=grid_color,
        linecolor=grid_color,
        tickcolor=THEME_COLORS["text_secondary"],
        tickfont=dict(color=THEME_COLORS["text_secondary"]),
        title_font=dict(color=THEME_COLORS["text_secondary"]),
    )

    fig.update_yaxes(
        gridcolor=grid_color,
        linecolor=grid_color,
        tickcolor=THEME_COLORS["text_secondary"],
        tickfont=dict(color=THEME_COLORS["text_secondary"]),
        title_font=dict(color=THEME_COLORS["text_secondary"]),
    )

    return fig


def create_interactive_scatter(
    data: Union[pd.DataFrame, Dict[str, List]],
    x: str,
    y: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    custom_data: Optional[List[str]] = None,
    title: str = "Interactive Scatter Plot",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    height: int = 500,
    dark_mode: bool = True,
    click_key: str = "scatter_click",
) -> Tuple[Optional["go.Figure"], Optional[Dict[str, Any]]]:
    """
    Create an interactive scatter plot with click event support.

    Args:
        data: DataFrame or dict with data columns
        x: Column name for x-axis values
        y: Column name for y-axis values
        color: Column name for color grouping
        size: Column name for marker sizes
        hover_data: Additional columns to show on hover
        custom_data: Columns to include in click event data
        title: Chart title
        x_label: X-axis label (defaults to column name)
        y_label: Y-axis label (defaults to column name)
        height: Chart height in pixels
        dark_mode: Whether to use dark theme
        click_key: Unique key for the click event handler

    Returns:
        Tuple of (figure, click_data) where click_data is None if no click
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("streamlit-plotly-events and plotly required. Install with: pip install streamlit-plotly-events plotly")

    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Build scatter plot
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        hover_data=hover_data,
        custom_data=custom_data,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )

    # Apply theme
    fig = _apply_theme(fig, dark_mode)

    # Update axes labels
    fig.update_xaxes(title_text=x_label or x)
    fig.update_yaxes(title_text=y_label or y)

    # Enhance markers
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color=THEME_COLORS["background_dark"]),
        ),
        selector=dict(mode="markers"),
    )

    fig.update_layout(height=height)

    # Render with click events
    click_data = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        key=click_key,
    )

    return fig, extract_click_data(click_data)


def create_selectable_bar_chart(
    data: Union[pd.DataFrame, Dict[str, List]],
    x: str,
    y: str,
    color: Optional[str] = None,
    orientation: str = "v",
    title: str = "Bar Chart",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    height: int = 400,
    dark_mode: bool = True,
    show_values: bool = True,
    click_key: str = "bar_click",
    barmode: str = "group",
) -> Tuple[Optional["go.Figure"], Optional[Dict[str, Any]]]:
    """
    Create an interactive bar chart with selection support.

    Args:
        data: DataFrame or dict with data columns
        x: Column name for categories (or values if horizontal)
        y: Column name for values (or categories if horizontal)
        color: Column name for color grouping
        orientation: 'v' for vertical, 'h' for horizontal
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        height: Chart height in pixels
        dark_mode: Whether to use dark theme
        show_values: Whether to show value labels on bars
        click_key: Unique key for the click event handler
        barmode: 'group', 'stack', or 'relative'

    Returns:
        Tuple of (figure, click_data) where click_data contains selected bar info
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("streamlit-plotly-events and plotly required. Install with: pip install streamlit-plotly-events plotly")

    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Build bar chart
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        orientation=orientation,
        title=title,
        barmode=barmode,
        color_discrete_sequence=COLOR_SEQUENCE,
        text=y if show_values else None,
    )

    # Apply theme
    fig = _apply_theme(fig, dark_mode)

    # Update axes labels
    fig.update_xaxes(title_text=x_label or x)
    fig.update_yaxes(title_text=y_label or y)

    # Style bars
    fig.update_traces(
        marker_line_color=THEME_COLORS["background_dark"],
        marker_line_width=1,
        textposition="outside" if orientation == "v" else "auto",
        textfont=dict(color=THEME_COLORS["text_secondary"], size=10),
    )

    fig.update_layout(
        height=height,
        bargap=0.15,
        bargroupgap=0.1,
    )

    # Render with click events
    click_data = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        key=click_key,
    )

    return fig, extract_click_data(click_data)


def create_company_comparison_chart(
    companies: List[str],
    metrics: Dict[str, List[float]],
    title: str = "Company Comparison",
    height: int = 500,
    dark_mode: bool = True,
    chart_type: str = "radar",
    click_key: str = "comparison_click",
) -> Tuple[Optional["go.Figure"], Optional[Dict[str, Any]]]:
    """
    Create a company comparison chart (radar or grouped bar).

    Args:
        companies: List of company names
        metrics: Dict mapping metric names to lists of values (one per company)
        title: Chart title
        height: Chart height in pixels
        dark_mode: Whether to use dark theme
        chart_type: 'radar' or 'bar'
        click_key: Unique key for the click event handler

    Returns:
        Tuple of (figure, click_data)
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("streamlit-plotly-events and plotly required. Install with: pip install streamlit-plotly-events plotly")

    metric_names = list(metrics.keys())

    if chart_type == "radar":
        fig = go.Figure()

        for i, company in enumerate(companies):
            values = [metrics[m][i] for m in metric_names]
            # Close the radar shape
            values_closed = values + [values[0]]
            theta_closed = metric_names + [metric_names[0]]

            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=theta_closed,
                fill="toself",
                name=company,
                line=dict(color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)], width=2),
                fillcolor=f"rgba({_hex_to_rgb(COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)])}, 0.2)",
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    gridcolor=THEME_COLORS["grid_line"],
                    linecolor=THEME_COLORS["grid_line"],
                    tickfont=dict(color=THEME_COLORS["text_secondary"]),
                ),
                angularaxis=dict(
                    gridcolor=THEME_COLORS["grid_line"],
                    linecolor=THEME_COLORS["grid_line"],
                    tickfont=dict(color=THEME_COLORS["text_secondary"]),
                ),
                bgcolor=THEME_COLORS["background_dark"] if dark_mode else "#FFFFFF",
            ),
            title=title,
        )
    else:
        # Grouped bar chart
        df_data = []
        for metric in metric_names:
            for i, company in enumerate(companies):
                df_data.append({
                    "Metric": metric,
                    "Company": company,
                    "Value": metrics[metric][i],
                })

        df = pd.DataFrame(df_data)

        fig = px.bar(
            df,
            x="Metric",
            y="Value",
            color="Company",
            barmode="group",
            title=title,
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    # Apply theme
    fig = _apply_theme(fig, dark_mode)
    fig.update_layout(height=height)

    # Render with click events
    click_data = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        key=click_key,
    )

    return fig, extract_click_data(click_data)


def create_time_series_chart(
    data: Union[pd.DataFrame, Dict[str, List]],
    x: str,
    y: Union[str, List[str]],
    title: str = "Time Series",
    x_label: str = "Date",
    y_label: str = "Value",
    height: int = 400,
    dark_mode: bool = True,
    show_range_slider: bool = True,
    click_key: str = "timeseries_click",
) -> Tuple[Optional["go.Figure"], Optional[Dict[str, Any]]]:
    """
    Create an interactive time series chart with range slider.

    Args:
        data: DataFrame or dict with time series data
        x: Column name for datetime values
        y: Column name(s) for y-axis values
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        height: Chart height in pixels
        dark_mode: Whether to use dark theme
        show_range_slider: Whether to show date range slider
        click_key: Unique key for the click event handler

    Returns:
        Tuple of (figure, click_data)
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("streamlit-plotly-events and plotly required. Install with: pip install streamlit-plotly-events plotly")

    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = go.Figure()

    y_columns = [y] if isinstance(y, str) else y

    for i, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            name=col,
            mode="lines",
            line=dict(
                color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)],
                width=2,
            ),
            hovertemplate=f"{col}: %{{y:.2f}}<extra></extra>",
        ))

    # Apply theme
    fig = _apply_theme(fig, dark_mode)

    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode="x unified",
    )

    if show_range_slider:
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeslider=dict(
                bgcolor=THEME_COLORS["background_light"],
                bordercolor=THEME_COLORS["grid_line"],
            ),
        )

    # Render with click events
    click_data = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        key=click_key,
    )

    return fig, extract_click_data(click_data)


def create_pie_chart(
    data: Union[pd.DataFrame, Dict[str, List]],
    values: str,
    names: str,
    title: str = "Distribution",
    height: int = 400,
    dark_mode: bool = True,
    hole: float = 0.4,
    click_key: str = "pie_click",
) -> Tuple[Optional["go.Figure"], Optional[Dict[str, Any]]]:
    """
    Create an interactive donut/pie chart.

    Args:
        data: DataFrame or dict with data
        values: Column name for values
        names: Column name for labels
        title: Chart title
        height: Chart height in pixels
        dark_mode: Whether to use dark theme
        hole: Size of center hole (0 for pie, >0 for donut)
        click_key: Unique key for the click event handler

    Returns:
        Tuple of (figure, click_data)
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("streamlit-plotly-events and plotly required. Install with: pip install streamlit-plotly-events plotly")

    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        hole=hole,
        color_discrete_sequence=COLOR_SEQUENCE,
    )

    # Apply theme
    fig = _apply_theme(fig, dark_mode)

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color=THEME_COLORS["text_primary"]),
        marker=dict(line=dict(color=THEME_COLORS["background_dark"], width=2)),
    )

    fig.update_layout(height=height)

    # Render with click events
    click_data = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        key=click_key,
    )

    return fig, extract_click_data(click_data)


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string for rgba()."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"
