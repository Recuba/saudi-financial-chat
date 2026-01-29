"""
ECharts Financial Visualization Components.

Provides candlestick charts, treemaps, and heatmaps for financial data
visualization using the streamlit-echarts library.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

# Optional dependency guard
try:
    from streamlit_echarts import st_echarts
    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False
    st_echarts = None


class EChartsTheme(str, Enum):
    """Theme options for ECharts visualizations."""
    DARK = "dark"
    LIGHT = "light"


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

# Sector colors for consistency across visualizations
SECTOR_PALETTE = {
    "Banks": "#D4A84B",
    "Petrochemicals": "#4CAF50",
    "Retail": "#2196F3",
    "Telecom": "#9C27B0",
    "Insurance": "#FF9800",
    "Real Estate": "#00BCD4",
    "Healthcare": "#E91E63",
    "Materials": "#795548",
    "Utilities": "#607D8B",
    "Food & Beverages": "#8BC34A",
    "Energy": "#FF5722",
    "Capital Goods": "#3F51B5",
    "default": "#9E9E9E",
}


def get_echarts_theme(theme: EChartsTheme = EChartsTheme.DARK) -> Dict[str, Any]:
    """
    Get ECharts theme configuration for Saudi Financial styling.

    Args:
        theme: Light or dark theme selection

    Returns:
        Dict containing ECharts theme configuration
    """
    is_dark = theme == EChartsTheme.DARK

    return {
        "backgroundColor": THEME_COLORS["background_dark"] if is_dark else "#FFFFFF",
        "textStyle": {
            "color": THEME_COLORS["text_primary"] if is_dark else "#333333",
            "fontFamily": "Inter, sans-serif",
        },
        "title": {
            "textStyle": {
                "color": THEME_COLORS["gold_primary"],
                "fontWeight": "bold",
            },
            "subtextStyle": {
                "color": THEME_COLORS["text_secondary"] if is_dark else "#666666",
            },
        },
        "legend": {
            "textStyle": {
                "color": THEME_COLORS["text_secondary"] if is_dark else "#333333",
            },
        },
        "tooltip": {
            "backgroundColor": THEME_COLORS["background_light"] if is_dark else "#FFFFFF",
            "borderColor": THEME_COLORS["gold_dark"],
            "textStyle": {
                "color": THEME_COLORS["text_primary"] if is_dark else "#333333",
            },
        },
        "axisLine": {
            "lineStyle": {
                "color": THEME_COLORS["grid_line"] if is_dark else "#CCCCCC",
            },
        },
        "splitLine": {
            "lineStyle": {
                "color": THEME_COLORS["grid_line"] if is_dark else "#EEEEEE",
            },
        },
    }


def create_candlestick_chart(
    data: Union[pd.DataFrame, List[Dict[str, Any]]],
    dates: Optional[List[str]] = None,
    title: str = "Stock Price",
    height: int = 400,
    show_volume: bool = True,
    theme: EChartsTheme = EChartsTheme.DARK,
    ma_periods: Optional[List[int]] = None,
) -> Optional[Any]:
    """
    Create an interactive candlestick chart for stock price data.

    Args:
        data: DataFrame with OHLCV columns or list of [open, close, low, high] values
        dates: List of date strings for x-axis (required if data is list)
        title: Chart title
        height: Chart height in pixels
        show_volume: Whether to show volume bars below
        theme: Light or dark theme
        ma_periods: Moving average periods to display (e.g., [5, 20, 60])

    Returns:
        Streamlit ECharts component or None if unavailable
    """
    if not ECHARTS_AVAILABLE:
        raise ImportError("streamlit-echarts is required. Install with: pip install streamlit-echarts")

    # Process DataFrame input
    if isinstance(data, pd.DataFrame):
        df = data.copy()

        # Standardize column names
        col_map = {
            "Open": "open", "High": "high", "Low": "low", "Close": "close",
            "Volume": "volume", "Date": "date", "date": "date"
        }
        df.columns = [col_map.get(c, c.lower()) for c in df.columns]

        if dates is None:
            if "date" in df.columns:
                dates = df["date"].astype(str).tolist()
            else:
                dates = df.index.astype(str).tolist()

        # Format: [open, close, low, high]
        candlestick_data = df[["open", "close", "low", "high"]].values.tolist()
        volume_data = df["volume"].tolist() if "volume" in df.columns else None
        close_prices = df["close"].tolist()
    else:
        candlestick_data = data
        volume_data = None
        close_prices = [d[1] for d in data]  # close is index 1

    theme_config = get_echarts_theme(theme)
    is_dark = theme == EChartsTheme.DARK

    # Build series
    series = [
        {
            "name": "Price",
            "type": "candlestick",
            "data": candlestick_data,
            "itemStyle": {
                "color": THEME_COLORS["positive"],
                "color0": THEME_COLORS["negative"],
                "borderColor": THEME_COLORS["positive"],
                "borderColor0": THEME_COLORS["negative"],
            },
            "xAxisIndex": 0,
            "yAxisIndex": 0,
        }
    ]

    # Add moving averages
    if ma_periods:
        ma_colors = ["#E8C872", "#2196F3", "#9C27B0", "#FF9800"]
        for i, period in enumerate(ma_periods):
            ma_data = _calculate_ma(close_prices, period)
            series.append({
                "name": f"MA{period}",
                "type": "line",
                "data": ma_data,
                "smooth": True,
                "lineStyle": {"width": 1.5},
                "itemStyle": {"color": ma_colors[i % len(ma_colors)]},
                "symbol": "none",
                "xAxisIndex": 0,
                "yAxisIndex": 0,
            })

    # Grid configuration
    grids = [{"left": "10%", "right": "8%", "top": "15%", "height": "55%" if show_volume else "70%"}]
    x_axes = [{
        "type": "category",
        "data": dates,
        "gridIndex": 0,
        "axisLine": {"lineStyle": {"color": THEME_COLORS["grid_line"]}},
        "axisLabel": {"color": THEME_COLORS["text_secondary"]},
        "boundaryGap": True,
        "axisPointer": {"show": True},
    }]
    y_axes = [{
        "type": "value",
        "gridIndex": 0,
        "scale": True,
        "splitArea": {"show": False},
        "axisLine": {"lineStyle": {"color": THEME_COLORS["grid_line"]}},
        "axisLabel": {"color": THEME_COLORS["text_secondary"]},
        "splitLine": {"lineStyle": {"color": THEME_COLORS["grid_line"], "type": "dashed"}},
    }]

    # Add volume chart
    if show_volume and volume_data:
        grids.append({"left": "10%", "right": "8%", "top": "75%", "height": "15%"})
        x_axes.append({
            "type": "category",
            "gridIndex": 1,
            "data": dates,
            "axisLabel": {"show": False},
            "axisTick": {"show": False},
            "axisLine": {"lineStyle": {"color": THEME_COLORS["grid_line"]}},
        })
        y_axes.append({
            "type": "value",
            "gridIndex": 1,
            "splitNumber": 2,
            "axisLabel": {"show": False},
            "axisLine": {"show": False},
            "splitLine": {"show": False},
        })

        # Color volume bars based on price change
        volume_colors = []
        for i, v in enumerate(volume_data):
            if i == 0:
                volume_colors.append(THEME_COLORS["neutral"])
            else:
                volume_colors.append(
                    THEME_COLORS["positive"] if close_prices[i] >= close_prices[i-1]
                    else THEME_COLORS["negative"]
                )

        series.append({
            "name": "Volume",
            "type": "bar",
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "data": [
                {"value": v, "itemStyle": {"color": volume_colors[i]}}
                for i, v in enumerate(volume_data)
            ],
        })

    option = {
        "backgroundColor": theme_config["backgroundColor"],
        "title": {
            "text": title,
            "left": "center",
            "textStyle": theme_config["title"]["textStyle"],
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
            **theme_config["tooltip"],
        },
        "legend": {
            "data": ["Price"] + ([f"MA{p}" for p in ma_periods] if ma_periods else []),
            "top": 30,
            "textStyle": theme_config["legend"]["textStyle"],
        },
        "grid": grids,
        "xAxis": x_axes,
        "yAxis": y_axes,
        "series": series,
        "dataZoom": [
            {"type": "inside", "xAxisIndex": [0, 1] if show_volume else [0], "start": 50, "end": 100},
            {"show": True, "type": "slider", "bottom": 10, "height": 20, "xAxisIndex": [0, 1] if show_volume else [0]},
        ],
    }

    return st_echarts(option, height=f"{height}px", key=f"candlestick_{title}")


def create_sector_treemap(
    data: Union[pd.DataFrame, List[Dict[str, Any]]],
    value_column: str = "market_cap",
    name_column: str = "company",
    sector_column: str = "sector",
    title: str = "Sector Distribution",
    height: int = 500,
    theme: EChartsTheme = EChartsTheme.DARK,
    show_labels: bool = True,
) -> Optional[Any]:
    """
    Create an interactive treemap showing sector/company distribution.

    Args:
        data: DataFrame or list of dicts with sector, company, and value data
        value_column: Column name for size values
        name_column: Column name for item names
        sector_column: Column name for sector grouping
        title: Chart title
        height: Chart height in pixels
        theme: Light or dark theme
        show_labels: Whether to show item labels

    Returns:
        Streamlit ECharts component or None if unavailable
    """
    if not ECHARTS_AVAILABLE:
        raise ImportError("streamlit-echarts is required. Install with: pip install streamlit-echarts")

    # Convert to DataFrame if needed
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Build hierarchical data structure
    tree_data = []
    for sector in df[sector_column].unique():
        sector_df = df[df[sector_column] == sector]
        sector_color = SECTOR_PALETTE.get(sector, SECTOR_PALETTE["default"])

        children = []
        for _, row in sector_df.iterrows():
            children.append({
                "name": row[name_column],
                "value": row[value_column],
                "itemStyle": {"color": sector_color},
            })

        tree_data.append({
            "name": sector,
            "value": sector_df[value_column].sum(),
            "children": children,
            "itemStyle": {"color": sector_color, "borderColor": "#0E0E0E", "borderWidth": 2},
        })

    theme_config = get_echarts_theme(theme)

    option = {
        "backgroundColor": theme_config["backgroundColor"],
        "title": {
            "text": title,
            "left": "center",
            "textStyle": theme_config["title"]["textStyle"],
        },
        "tooltip": {
            "formatter": "{b}: {c}",
            **theme_config["tooltip"],
        },
        "series": [{
            "type": "treemap",
            "data": tree_data,
            "roam": "move",
            "breadcrumb": {
                "show": True,
                "itemStyle": {
                    "color": THEME_COLORS["background_light"],
                    "borderColor": THEME_COLORS["gold_dark"],
                    "textStyle": {"color": THEME_COLORS["text_primary"]},
                },
            },
            "label": {
                "show": show_labels,
                "formatter": "{b}",
                "color": THEME_COLORS["text_primary"],
                "fontSize": 11,
            },
            "upperLabel": {
                "show": True,
                "height": 30,
                "color": THEME_COLORS["text_primary"],
                "backgroundColor": "transparent",
            },
            "itemStyle": {
                "borderColor": THEME_COLORS["background_dark"],
                "borderWidth": 1,
                "gapWidth": 1,
            },
            "levels": [
                {
                    "itemStyle": {
                        "borderColor": THEME_COLORS["gold_dark"],
                        "borderWidth": 2,
                        "gapWidth": 2,
                    },
                    "upperLabel": {"show": True},
                },
                {
                    "itemStyle": {
                        "borderColor": THEME_COLORS["grid_line"],
                        "borderWidth": 1,
                        "gapWidth": 1,
                    },
                    "emphasis": {
                        "itemStyle": {"borderColor": THEME_COLORS["gold_primary"]},
                    },
                },
            ],
        }],
    }

    return st_echarts(option, height=f"{height}px", key=f"treemap_{title}")


def create_correlation_heatmap(
    data: Union[pd.DataFrame, List[List[float]]],
    x_labels: Optional[List[str]] = None,
    y_labels: Optional[List[str]] = None,
    title: str = "Correlation Matrix",
    height: int = 500,
    theme: EChartsTheme = EChartsTheme.DARK,
    min_value: float = -1.0,
    max_value: float = 1.0,
    show_values: bool = True,
) -> Optional[Any]:
    """
    Create an interactive heatmap for correlation matrices.

    Args:
        data: DataFrame correlation matrix or 2D list of values
        x_labels: Labels for x-axis (defaults to column names if DataFrame)
        y_labels: Labels for y-axis (defaults to index if DataFrame)
        title: Chart title
        height: Chart height in pixels
        theme: Light or dark theme
        min_value: Minimum value for color scale
        max_value: Maximum value for color scale
        show_values: Whether to show values in cells

    Returns:
        Streamlit ECharts component or None if unavailable
    """
    if not ECHARTS_AVAILABLE:
        raise ImportError("streamlit-echarts is required. Install with: pip install streamlit-echarts")

    # Process DataFrame
    if isinstance(data, pd.DataFrame):
        matrix = data.values.tolist()
        if x_labels is None:
            x_labels = data.columns.tolist()
        if y_labels is None:
            y_labels = data.index.tolist()
    else:
        matrix = data
        if x_labels is None:
            x_labels = [str(i) for i in range(len(matrix[0]))]
        if y_labels is None:
            y_labels = [str(i) for i in range(len(matrix))]

    # Convert to ECharts format: [x_index, y_index, value]
    heatmap_data = []
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            heatmap_data.append([j, i, round(value, 3) if value is not None else None])

    theme_config = get_echarts_theme(theme)

    option = {
        "backgroundColor": theme_config["backgroundColor"],
        "title": {
            "text": title,
            "left": "center",
            "textStyle": theme_config["title"]["textStyle"],
        },
        "tooltip": {
            "position": "top",
            "formatter": lambda params: f"{y_labels[params['data'][1]]} vs {x_labels[params['data'][0]]}: {params['data'][2]:.3f}" if params['data'][2] is not None else "N/A",
            **theme_config["tooltip"],
        },
        "grid": {
            "left": "15%",
            "right": "15%",
            "top": "15%",
            "bottom": "15%",
        },
        "xAxis": {
            "type": "category",
            "data": x_labels,
            "axisLabel": {
                "color": THEME_COLORS["text_secondary"],
                "rotate": 45,
                "fontSize": 10,
            },
            "axisLine": {"lineStyle": {"color": THEME_COLORS["grid_line"]}},
            "splitArea": {"show": True},
        },
        "yAxis": {
            "type": "category",
            "data": y_labels,
            "axisLabel": {
                "color": THEME_COLORS["text_secondary"],
                "fontSize": 10,
            },
            "axisLine": {"lineStyle": {"color": THEME_COLORS["grid_line"]}},
            "splitArea": {"show": True},
        },
        "visualMap": {
            "min": min_value,
            "max": max_value,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "0%",
            "textStyle": {"color": THEME_COLORS["text_secondary"]},
            "inRange": {
                "color": [
                    THEME_COLORS["negative"],
                    THEME_COLORS["background_light"],
                    THEME_COLORS["positive"],
                ],
            },
        },
        "series": [{
            "name": "Correlation",
            "type": "heatmap",
            "data": heatmap_data,
            "label": {
                "show": show_values,
                "color": THEME_COLORS["text_primary"],
                "fontSize": 9,
            },
            "emphasis": {
                "itemStyle": {
                    "borderColor": THEME_COLORS["gold_primary"],
                    "borderWidth": 2,
                },
            },
        }],
    }

    # Use JavaScript formatter for tooltip
    option["tooltip"]["formatter"] = None

    return st_echarts(option, height=f"{height}px", key=f"heatmap_{title}")


def _calculate_ma(data: List[float], period: int) -> List[Optional[float]]:
    """
    Calculate moving average for a data series.

    Args:
        data: List of values
        period: MA period

    Returns:
        List of MA values (None for initial period)
    """
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            avg = sum(data[i - period + 1:i + 1]) / period
            result.append(round(avg, 2))
    return result


def create_gauge_chart(
    value: float,
    title: str = "Performance",
    min_value: float = 0,
    max_value: float = 100,
    height: int = 300,
    theme: EChartsTheme = EChartsTheme.DARK,
    thresholds: Optional[List[Tuple[float, str]]] = None,
) -> Optional[Any]:
    """
    Create a gauge chart for KPI visualization.

    Args:
        value: Current value to display
        title: Gauge title
        min_value: Minimum scale value
        max_value: Maximum scale value
        height: Chart height in pixels
        theme: Light or dark theme
        thresholds: List of (value, color) tuples for ranges

    Returns:
        Streamlit ECharts component or None if unavailable
    """
    if not ECHARTS_AVAILABLE:
        raise ImportError("streamlit-echarts is required. Install with: pip install streamlit-echarts")

    theme_config = get_echarts_theme(theme)

    # Default thresholds
    if thresholds is None:
        thresholds = [
            (0.3, THEME_COLORS["negative"]),
            (0.7, THEME_COLORS["gold_primary"]),
            (1.0, THEME_COLORS["positive"]),
        ]

    # Convert thresholds to axis line colors
    axis_colors = [[t[0], t[1]] for t in thresholds]

    option = {
        "backgroundColor": theme_config["backgroundColor"],
        "series": [{
            "type": "gauge",
            "min": min_value,
            "max": max_value,
            "progress": {"show": True, "width": 18},
            "axisLine": {
                "lineStyle": {
                    "width": 18,
                    "color": axis_colors,
                },
            },
            "axisTick": {"show": False},
            "splitLine": {
                "length": 15,
                "lineStyle": {"width": 2, "color": THEME_COLORS["text_secondary"]},
            },
            "axisLabel": {
                "distance": 25,
                "color": THEME_COLORS["text_secondary"],
                "fontSize": 12,
            },
            "anchor": {
                "show": True,
                "showAbove": True,
                "size": 20,
                "itemStyle": {"borderWidth": 8, "borderColor": THEME_COLORS["gold_dark"]},
            },
            "title": {
                "show": True,
                "offsetCenter": [0, "70%"],
                "fontSize": 16,
                "color": THEME_COLORS["gold_primary"],
            },
            "detail": {
                "valueAnimation": True,
                "fontSize": 30,
                "offsetCenter": [0, "40%"],
                "color": THEME_COLORS["text_primary"],
                "formatter": "{value}",
            },
            "data": [{"value": value, "name": title}],
        }],
    }

    return st_echarts(option, height=f"{height}px", key=f"gauge_{title}")
