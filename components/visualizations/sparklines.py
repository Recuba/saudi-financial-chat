"""
Sparkline Visualization Components.

Provides inline sparkline charts and trend detection for compact
financial data visualization using the plost library.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

# Streamlit import for rendering
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Optional dependency guard
try:
    import plost
    PLOST_AVAILABLE = True
except ImportError:
    PLOST_AVAILABLE = False
    plost = None


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
}


class TrendDirection(str, Enum):
    """Trend direction indicators."""
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


@dataclass
class TrendAnalysis:
    """
    Result of trend analysis on a data series.

    Attributes:
        direction: Overall trend direction
        change_percent: Percentage change from start to end
        volatility: Standard deviation of changes
        current_value: Most recent value
        previous_value: Previous value
        min_value: Minimum value in series
        max_value: Maximum value in series
    """
    direction: TrendDirection
    change_percent: float
    volatility: float
    current_value: float
    previous_value: float
    min_value: float
    max_value: float

    @property
    def trend_color(self) -> str:
        """Get theme color based on trend direction."""
        if self.direction == TrendDirection.UP:
            return THEME_COLORS["positive"]
        elif self.direction == TrendDirection.DOWN:
            return THEME_COLORS["negative"]
        return THEME_COLORS["neutral"]

    @property
    def trend_icon(self) -> str:
        """Get unicode arrow for trend direction."""
        if self.direction == TrendDirection.UP:
            return "▲"
        elif self.direction == TrendDirection.DOWN:
            return "▼"
        return "●"


def detect_trend(
    values: Union[List[float], pd.Series],
    threshold_percent: float = 1.0,
    lookback_periods: Optional[int] = None,
) -> TrendAnalysis:
    """
    Analyze trend direction and characteristics of a data series.

    Args:
        values: List or Series of numeric values
        threshold_percent: Minimum change % to be considered up/down (not flat)
        lookback_periods: Number of recent periods to analyze (None = all)

    Returns:
        TrendAnalysis with direction and statistics
    """
    if isinstance(values, pd.Series):
        values = values.tolist()

    if lookback_periods and len(values) > lookback_periods:
        values = values[-lookback_periods:]

    if len(values) < 2:
        return TrendAnalysis(
            direction=TrendDirection.FLAT,
            change_percent=0.0,
            volatility=0.0,
            current_value=values[0] if values else 0.0,
            previous_value=values[0] if values else 0.0,
            min_value=values[0] if values else 0.0,
            max_value=values[0] if values else 0.0,
        )

    current = values[-1]
    previous = values[-2]
    start = values[0]

    # Calculate percent change
    if start != 0:
        change_percent = ((current - start) / abs(start)) * 100
    else:
        change_percent = 0.0 if current == 0 else (100.0 if current > 0 else -100.0)

    # Calculate volatility (std dev of period-over-period changes)
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    volatility = pd.Series(changes).std() if changes else 0.0

    # Determine direction
    if abs(change_percent) < threshold_percent:
        direction = TrendDirection.FLAT
    elif change_percent > 0:
        direction = TrendDirection.UP
    else:
        direction = TrendDirection.DOWN

    return TrendAnalysis(
        direction=direction,
        change_percent=round(change_percent, 2),
        volatility=round(volatility, 4),
        current_value=current,
        previous_value=previous,
        min_value=min(values),
        max_value=max(values),
    )


def create_sparkline(
    values: Union[List[float], pd.Series, pd.DataFrame],
    value_column: Optional[str] = None,
    time_column: Optional[str] = None,
    color: Optional[str] = None,
    height: int = 50,
    width: Optional[int] = None,
    show_area: bool = True,
    key: Optional[str] = None,
) -> None:
    """
    Render an inline sparkline chart.

    Args:
        values: List, Series, or DataFrame of values
        value_column: Column name if DataFrame (required for DataFrame)
        time_column: Column name for x-axis (optional, uses index if not provided)
        color: Line color (auto-detects trend if None)
        height: Chart height in pixels
        width: Chart width (None for full width)
        show_area: Whether to show area fill under line
        key: Unique key for the component
    """
    if not PLOST_AVAILABLE:
        raise ImportError("plost is required. Install with: pip install plost")

    if not STREAMLIT_AVAILABLE:
        raise ImportError("streamlit is required for sparkline rendering")

    # Convert to DataFrame
    if isinstance(values, list):
        df = pd.DataFrame({"value": values, "index": range(len(values))})
        value_column = "value"
        time_column = "index"
    elif isinstance(values, pd.Series):
        df = pd.DataFrame({"value": values.values, "index": range(len(values))})
        value_column = "value"
        time_column = "index"
    else:
        df = values.copy()
        if value_column is None:
            raise ValueError("value_column required when passing DataFrame")
        if time_column is None:
            df["_index"] = range(len(df))
            time_column = "_index"

    # Auto-detect color from trend
    if color is None:
        trend = detect_trend(df[value_column].tolist())
        color = trend.trend_color

    # Render sparkline
    plost.line_chart(
        df,
        x=time_column,
        y=value_column,
        color=color,
        height=height,
        width=width,
        use_container_width=width is None,
    )


def create_metric_with_sparkline(
    label: str,
    current_value: float,
    history: Union[List[float], pd.Series],
    format_str: str = "{:.2f}",
    prefix: str = "",
    suffix: str = "",
    sparkline_height: int = 40,
    show_trend: bool = True,
    show_change: bool = True,
    invert_colors: bool = False,
) -> None:
    """
    Render a metric card with sparkline history and trend indicator.

    Args:
        label: Metric label/name
        current_value: Current metric value
        history: Historical values for sparkline
        format_str: Format string for value display
        prefix: Prefix for value (e.g., "$", "SAR")
        suffix: Suffix for value (e.g., "%", "M")
        sparkline_height: Height of sparkline in pixels
        show_trend: Whether to show trend arrow
        show_change: Whether to show change percentage
        invert_colors: Whether to invert positive/negative colors
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("streamlit is required for metric rendering")

    if isinstance(history, pd.Series):
        history = history.tolist()

    # Analyze trend
    trend = detect_trend(history)

    # Determine colors (with optional inversion)
    if invert_colors:
        positive_color = THEME_COLORS["negative"]
        negative_color = THEME_COLORS["positive"]
    else:
        positive_color = THEME_COLORS["positive"]
        negative_color = THEME_COLORS["negative"]

    if trend.direction == TrendDirection.UP:
        trend_color = positive_color
        delta_color = "normal"
    elif trend.direction == TrendDirection.DOWN:
        trend_color = negative_color
        delta_color = "inverse"
    else:
        trend_color = THEME_COLORS["neutral"]
        delta_color = "off"

    # Format values
    formatted_value = f"{prefix}{format_str.format(current_value)}{suffix}"

    # Build delta string
    if show_change:
        delta_str = f"{trend.change_percent:+.2f}%"
    else:
        delta_str = None

    # Render with Streamlit
    with st.container():
        # Custom CSS for styling
        st.markdown(f"""
        <style>
        .metric-sparkline-container {{
            background-color: {THEME_COLORS["background_light"]};
            border-radius: 8px;
            padding: 12px;
            border-left: 3px solid {THEME_COLORS["gold_primary"]};
        }}
        .metric-label {{
            color: {THEME_COLORS["text_secondary"]};
            font-size: 0.85rem;
            margin-bottom: 4px;
        }}
        .metric-value {{
            color: {THEME_COLORS["text_primary"]};
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .metric-trend {{
            color: {trend_color};
            font-size: 0.9rem;
            margin-left: 8px;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Metric display
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)

            value_html = f'<span class="metric-value">{formatted_value}</span>'
            if show_trend:
                value_html += f'<span class="metric-trend">{trend.trend_icon} {delta_str if delta_str else ""}</span>'

            st.markdown(value_html, unsafe_allow_html=True)

        with col2:
            if PLOST_AVAILABLE and len(history) > 1:
                # Create mini sparkline
                df = pd.DataFrame({
                    "value": history,
                    "index": range(len(history))
                })

                plost.line_chart(
                    df,
                    x="index",
                    y="value",
                    color=trend_color,
                    height=sparkline_height,
                    use_container_width=True,
                )


def create_sparkline_table(
    data: pd.DataFrame,
    label_column: str,
    value_column: str,
    history_column: str,
    format_str: str = "{:.2f}",
    prefix: str = "",
    suffix: str = "",
    sparkline_height: int = 30,
) -> None:
    """
    Render a table with sparklines for each row.

    Args:
        data: DataFrame with labels, current values, and history lists
        label_column: Column name for row labels
        value_column: Column name for current values
        history_column: Column name containing lists of historical values
        format_str: Format string for value display
        prefix: Prefix for values
        suffix: Suffix for values
        sparkline_height: Height of sparklines
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("streamlit is required for table rendering")

    st.markdown(f"""
    <style>
    .sparkline-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .sparkline-table th {{
        background-color: {THEME_COLORS["background_light"]};
        color: {THEME_COLORS["gold_primary"]};
        padding: 10px;
        text-align: left;
        border-bottom: 2px solid {THEME_COLORS["gold_dark"]};
    }}
    .sparkline-table td {{
        padding: 8px;
        border-bottom: 1px solid {THEME_COLORS["grid_line"] if "grid_line" in THEME_COLORS else "#333"};
        color: {THEME_COLORS["text_primary"]};
    }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    cols = st.columns([2, 2, 2, 3])
    cols[0].markdown(f"**{label_column}**")
    cols[1].markdown("**Value**")
    cols[2].markdown("**Change**")
    cols[3].markdown("**Trend**")

    st.divider()

    # Rows
    for _, row in data.iterrows():
        history = row[history_column]
        if isinstance(history, str):
            import json
            history = json.loads(history)

        trend = detect_trend(history)

        cols = st.columns([2, 2, 2, 3])

        cols[0].write(row[label_column])
        cols[1].write(f"{prefix}{format_str.format(row[value_column])}{suffix}")

        # Change with color
        change_color = trend.trend_color
        cols[2].markdown(
            f'<span style="color: {change_color}">{trend.trend_icon} {trend.change_percent:+.2f}%</span>',
            unsafe_allow_html=True
        )

        # Sparkline
        with cols[3]:
            if PLOST_AVAILABLE and len(history) > 1:
                df = pd.DataFrame({
                    "value": history,
                    "index": range(len(history))
                })
                plost.line_chart(
                    df,
                    x="index",
                    y="value",
                    color=change_color,
                    height=sparkline_height,
                    use_container_width=True,
                )


def create_mini_bar_sparkline(
    values: List[float],
    color: Optional[str] = None,
    height: int = 40,
    show_baseline: bool = True,
) -> None:
    """
    Render a mini bar chart sparkline.

    Args:
        values: List of values
        color: Bar color (auto-detects from trend if None)
        height: Chart height in pixels
        show_baseline: Whether to show zero baseline
    """
    if not PLOST_AVAILABLE:
        raise ImportError("plost is required. Install with: pip install plost")

    if not STREAMLIT_AVAILABLE:
        raise ImportError("streamlit is required")

    if color is None:
        trend = detect_trend(values)
        color = trend.trend_color

    df = pd.DataFrame({
        "value": values,
        "index": [str(i) for i in range(len(values))]
    })

    plost.bar_chart(
        df,
        bar="index",
        value="value",
        color=color,
        height=height,
        use_container_width=True,
    )


def format_sparkline_delta(
    current: float,
    previous: float,
    format_str: str = "{:+.2f}",
    show_percent: bool = True,
) -> Tuple[str, str, TrendDirection]:
    """
    Format delta value with trend information.

    Args:
        current: Current value
        previous: Previous value
        format_str: Format string for delta
        show_percent: Whether to show percentage

    Returns:
        Tuple of (formatted_delta, trend_color, trend_direction)
    """
    if previous == 0:
        if current == 0:
            return "0", THEME_COLORS["neutral"], TrendDirection.FLAT
        pct_change = 100.0 if current > 0 else -100.0
    else:
        pct_change = ((current - previous) / abs(previous)) * 100

    abs_change = current - previous

    if abs(pct_change) < 0.5:
        direction = TrendDirection.FLAT
        color = THEME_COLORS["neutral"]
    elif pct_change > 0:
        direction = TrendDirection.UP
        color = THEME_COLORS["positive"]
    else:
        direction = TrendDirection.DOWN
        color = THEME_COLORS["negative"]

    if show_percent:
        delta_str = f"{format_str.format(abs_change)} ({pct_change:+.1f}%)"
    else:
        delta_str = format_str.format(abs_change)

    return delta_str, color, direction
