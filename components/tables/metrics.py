"""
Financial Metrics Components for Saudi Financial Chat.

Provides styled metric cards with K/M/B number abbreviations,
delta calculations, and flexible layouts for displaying financial KPIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import pandas as pd
import streamlit as st

# Import guard for streamlit-extras
try:
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.stylable_container import stylable_container
    STREAMLIT_EXTRAS_AVAILABLE = True
except ImportError:
    STREAMLIT_EXTRAS_AVAILABLE = False
    style_metric_cards = None
    stylable_container = None


# =============================================================================
# Number Formatting Utilities
# =============================================================================

def format_number_abbreviated(
    value: float,
    decimals: int = 1,
    prefix: str = "",
    suffix: str = "",
    force_sign: bool = False,
) -> str:
    """
    Format a number with K/M/B abbreviations.

    Args:
        value: The numeric value to format
        decimals: Number of decimal places (default: 1)
        prefix: String to prepend (e.g., "SAR ")
        suffix: String to append (e.g., "%")
        force_sign: Show + sign for positive numbers

    Returns:
        Formatted string with abbreviation

    Examples:
        >>> format_number_abbreviated(1500000)
        '1.5M'
        >>> format_number_abbreviated(2500000000, prefix="SAR ")
        'SAR 2.5B'
        >>> format_number_abbreviated(0.25, suffix="%")
        '0.3%'
    """
    if pd.isna(value):
        return "-"

    abs_value = abs(value)
    sign = "+" if force_sign and value > 0 else ""

    if abs_value >= 1e12:
        formatted = f"{value / 1e12:.{decimals}f}T"
    elif abs_value >= 1e9:
        formatted = f"{value / 1e9:.{decimals}f}B"
    elif abs_value >= 1e6:
        formatted = f"{value / 1e6:.{decimals}f}M"
    elif abs_value >= 1e3:
        formatted = f"{value / 1e3:.{decimals}f}K"
    else:
        formatted = f"{value:.{decimals}f}"

    return f"{sign}{prefix}{formatted}{suffix}"


def format_sar_currency(
    value: float,
    abbreviated: bool = True,
    decimals: int = 1,
) -> str:
    """
    Format a value as SAR currency.

    Args:
        value: Numeric value to format
        abbreviated: Use K/M/B abbreviations
        decimals: Number of decimal places

    Returns:
        Formatted SAR string

    Examples:
        >>> format_sar_currency(1500000000)
        'SAR 1.5B'
        >>> format_sar_currency(1500000000, abbreviated=False)
        'SAR 1,500,000,000.00'
    """
    if pd.isna(value):
        return "-"

    if abbreviated:
        return format_number_abbreviated(value, decimals=decimals, prefix="SAR ")
    else:
        return f"SAR {value:,.{decimals}f}"


def format_percentage(
    value: float,
    is_decimal: bool = True,
    decimals: int = 2,
    force_sign: bool = False,
) -> str:
    """
    Format a value as percentage.

    Args:
        value: Numeric value (decimal or whole number)
        is_decimal: If True, value is decimal (0.25 = 25%)
        decimals: Number of decimal places
        force_sign: Show + sign for positive values

    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "-"

    pct_value = value * 100 if is_decimal else value
    sign = "+" if force_sign and pct_value > 0 else ""

    return f"{sign}{pct_value:.{decimals}f}%"


def calculate_delta_percentage(
    current: float,
    previous: float,
    decimals: int = 2,
) -> Tuple[float, str]:
    """
    Calculate percentage change between two values.

    Args:
        current: Current period value
        previous: Previous period value
        decimals: Decimal places for formatted string

    Returns:
        Tuple of (delta_percentage, formatted_string)

    Example:
        >>> calculate_delta_percentage(120, 100)
        (0.2, '+20.00%')
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return (0.0, "-")

    delta = (current - previous) / abs(previous)
    sign = "+" if delta > 0 else ""
    formatted = f"{sign}{delta * 100:.{decimals}f}%"

    return (delta, formatted)


def calculate_delta_absolute(
    current: float,
    previous: float,
    abbreviated: bool = True,
    prefix: str = "",
) -> Tuple[float, str]:
    """
    Calculate absolute change between two values.

    Args:
        current: Current period value
        previous: Previous period value
        abbreviated: Use K/M/B formatting
        prefix: Prefix for formatted string (e.g., "SAR ")

    Returns:
        Tuple of (delta_value, formatted_string)
    """
    if pd.isna(current) or pd.isna(previous):
        return (0.0, "-")

    delta = current - previous

    if abbreviated:
        formatted = format_number_abbreviated(delta, prefix=prefix, force_sign=True)
    else:
        sign = "+" if delta > 0 else ""
        formatted = f"{sign}{prefix}{delta:,.2f}"

    return (delta, formatted)


# =============================================================================
# Metric Card Components
# =============================================================================

@dataclass
class MetricConfig:
    """Configuration for a single metric card."""

    label: str
    value: float
    previous_value: Optional[float] = None
    format_type: Literal["number", "currency", "percentage", "ratio"] = "number"
    abbreviated: bool = True
    decimals: int = 1
    delta_type: Literal["percentage", "absolute", "none"] = "percentage"
    invert_delta: bool = False  # True if decrease is good (e.g., debt)
    icon: Optional[str] = None
    help_text: Optional[str] = None

    def get_formatted_value(self) -> str:
        """Get the formatted display value."""
        if self.format_type == "currency":
            return format_sar_currency(self.value, self.abbreviated, self.decimals)
        elif self.format_type == "percentage":
            return format_percentage(self.value, is_decimal=True, decimals=self.decimals)
        elif self.format_type == "ratio":
            if pd.isna(self.value):
                return "-"
            return f"{self.value:.{self.decimals}f}x"
        else:
            return format_number_abbreviated(self.value, self.decimals)

    def get_delta(self) -> Tuple[Optional[float], Optional[str]]:
        """Get the delta value and formatted string."""
        if self.previous_value is None or self.delta_type == "none":
            return (None, None)

        if self.delta_type == "percentage":
            delta, formatted = calculate_delta_percentage(
                self.value, self.previous_value, decimals=1
            )
        else:  # absolute
            prefix = "SAR " if self.format_type == "currency" else ""
            delta, formatted = calculate_delta_absolute(
                self.value, self.previous_value,
                abbreviated=self.abbreviated,
                prefix=prefix,
            )

        return (delta, formatted)


class MetricCard:
    """
    A styled metric card component for financial KPIs.

    Displays a metric value with optional delta comparison,
    K/M/B abbreviations, and SAR currency formatting.

    Features:
    - Automatic K/M/B number abbreviations
    - SAR currency formatting
    - Percentage and ratio formatting
    - Delta calculations (percentage or absolute)
    - Positive/negative delta coloring
    - Help text tooltips

    Example:
        ```python
        from components.tables import MetricCard

        card = MetricCard(
            label="Revenue",
            value=1500000000,
            previous_value=1200000000,
            format_type="currency",
        )
        card.render()
        ```
    """

    def __init__(
        self,
        label: str,
        value: float,
        previous_value: Optional[float] = None,
        format_type: Literal["number", "currency", "percentage", "ratio"] = "number",
        abbreviated: bool = True,
        decimals: int = 1,
        delta_type: Literal["percentage", "absolute", "none"] = "percentage",
        invert_delta: bool = False,
        help_text: Optional[str] = None,
    ):
        """
        Initialize a MetricCard.

        Args:
            label: Metric label/title
            value: Current metric value
            previous_value: Previous period value for delta calculation
            format_type: How to format the value
            abbreviated: Use K/M/B abbreviations
            decimals: Decimal places
            delta_type: Type of delta calculation
            invert_delta: Invert delta colors (green for decrease)
            help_text: Tooltip help text
        """
        self.config = MetricConfig(
            label=label,
            value=value,
            previous_value=previous_value,
            format_type=format_type,
            abbreviated=abbreviated,
            decimals=decimals,
            delta_type=delta_type,
            invert_delta=invert_delta,
            help_text=help_text,
        )

    def render(self) -> None:
        """Render the metric card using Streamlit."""
        formatted_value = self.config.get_formatted_value()
        delta_value, delta_str = self.config.get_delta()

        # Determine delta color direction
        delta_color = "normal"
        if self.config.invert_delta and delta_value is not None:
            delta_color = "inverse"

        # Render with st.metric
        st.metric(
            label=self.config.label,
            value=formatted_value,
            delta=delta_str,
            delta_color=delta_color if delta_value is not None else "off",
            help=self.config.help_text,
        )


class MetricsRow:
    """
    A row of metric cards with consistent styling.

    Provides a convenient way to display multiple related metrics
    in a horizontal row with proper spacing and styling.

    Example:
        ```python
        from components.tables import MetricsRow, MetricConfig

        metrics = MetricsRow([
            MetricConfig("Revenue", 1500000000, 1200000000, "currency"),
            MetricConfig("Net Profit", 300000000, 250000000, "currency"),
            MetricConfig("ROE", 0.25, 0.22, "percentage"),
        ])
        metrics.render()
        ```
    """

    def __init__(
        self,
        metrics: List[Union[MetricConfig, Dict[str, Any]]],
        columns: Optional[int] = None,
        apply_style: bool = True,
        border_color: str = "#CCC",
        background_color: str = "#F0F2F6",
        border_radius: int = 10,
    ):
        """
        Initialize a MetricsRow.

        Args:
            metrics: List of MetricConfig objects or dicts
            columns: Number of columns (auto-detected if None)
            apply_style: Apply streamlit-extras styling
            border_color: Card border color
            background_color: Card background color
            border_radius: Card border radius in pixels
        """
        self.metrics = [
            m if isinstance(m, MetricConfig) else MetricConfig(**m)
            for m in metrics
        ]
        self.columns = columns or len(metrics)
        self.apply_style = apply_style
        self.border_color = border_color
        self.background_color = background_color
        self.border_radius = border_radius

    def render(self) -> None:
        """Render the metrics row."""
        cols = st.columns(self.columns)

        for i, metric in enumerate(self.metrics):
            col_idx = i % self.columns

            with cols[col_idx]:
                card = MetricCard(
                    label=metric.label,
                    value=metric.value,
                    previous_value=metric.previous_value,
                    format_type=metric.format_type,
                    abbreviated=metric.abbreviated,
                    decimals=metric.decimals,
                    delta_type=metric.delta_type,
                    invert_delta=metric.invert_delta,
                    help_text=metric.help_text,
                )
                card.render()

        # Apply styling if available
        if self.apply_style and STREAMLIT_EXTRAS_AVAILABLE:
            style_metric_cards(
                border_left_color=self.border_color,
                background_color=self.background_color,
                border_radius_px=self.border_radius,
            )


# =============================================================================
# Convenience Functions
# =============================================================================

def create_financial_metrics(
    data: Dict[str, Any],
    previous_data: Optional[Dict[str, Any]] = None,
    layout: Literal["row", "grid"] = "row",
    columns_per_row: int = 4,
) -> None:
    """
    Create financial metrics display from a data dictionary.

    Automatically detects metric types based on column names and formats
    values appropriately for SAR currency, percentages, and ratios.

    Args:
        data: Dictionary of metric_name: value pairs
        previous_data: Optional dictionary of previous period values
        layout: Display layout ("row" or "grid")
        columns_per_row: Metrics per row in grid layout

    Example:
        ```python
        from components.tables import create_financial_metrics

        create_financial_metrics({
            "revenue": 1500000000,
            "net_profit": 300000000,
            "ROE": 0.25,
            "debt_to_equity": 1.5,
        })
        ```
    """
    # Define metric type detection rules
    currency_keywords = ["revenue", "profit", "income", "expense", "asset",
                        "equity", "liability", "capital", "cash", "sar"]
    percentage_keywords = ["roe", "roa", "margin", "rate", "percent", "pct", "yield"]
    ratio_keywords = ["ratio", "debt_to", "coverage", "leverage", "multiple"]
    invert_delta_keywords = ["expense", "debt", "liability", "cost"]

    metrics: List[MetricConfig] = []

    for key, value in data.items():
        key_lower = key.lower()

        # Detect format type
        if any(kw in key_lower for kw in percentage_keywords):
            format_type = "percentage"
        elif any(kw in key_lower for kw in ratio_keywords):
            format_type = "ratio"
        elif any(kw in key_lower for kw in currency_keywords):
            format_type = "currency"
        else:
            format_type = "number"

        # Check if delta should be inverted
        invert_delta = any(kw in key_lower for kw in invert_delta_keywords)

        # Get previous value if available
        prev_value = previous_data.get(key) if previous_data else None

        # Create label from key
        label = key.replace("_", " ").title()

        metrics.append(MetricConfig(
            label=label,
            value=value,
            previous_value=prev_value,
            format_type=format_type,
            invert_delta=invert_delta,
        ))

    # Render metrics
    if layout == "row":
        row = MetricsRow(metrics, columns=len(metrics))
        row.render()
    else:  # grid
        row = MetricsRow(metrics, columns=columns_per_row)
        row.render()


def create_company_metrics_summary(
    company_data: pd.Series,
    previous_data: Optional[pd.Series] = None,
) -> None:
    """
    Create a metrics summary for a single company.

    Displays key financial metrics in a formatted row with
    automatic formatting and delta calculations.

    Args:
        company_data: Series containing company financial data
        previous_data: Optional Series containing previous period data

    Example:
        ```python
        company = df[df['company_name'] == 'Saudi Aramco'].iloc[0]
        previous = df_prev[df_prev['company_name'] == 'Saudi Aramco'].iloc[0]
        create_company_metrics_summary(company, previous)
        ```
    """
    # Define key metrics to display
    key_metrics = [
        ("revenue", "Revenue", "currency"),
        ("net_profit", "Net Profit", "currency"),
        ("total_assets", "Total Assets", "currency"),
        ("ROE", "ROE", "percentage"),
        ("ROA", "ROA", "percentage"),
        ("debt_to_equity", "D/E Ratio", "ratio"),
    ]

    metrics: List[MetricConfig] = []

    for field, label, format_type in key_metrics:
        if field not in company_data.index:
            continue

        value = company_data[field]
        prev_value = previous_data[field] if previous_data is not None and field in previous_data.index else None

        # Invert delta for debt ratio
        invert_delta = field == "debt_to_equity"

        metrics.append(MetricConfig(
            label=label,
            value=value,
            previous_value=prev_value,
            format_type=format_type,
            invert_delta=invert_delta,
        ))

    # Display company name as header
    if "company_name" in company_data.index:
        st.subheader(company_data["company_name"])

    # Render metrics row
    row = MetricsRow(metrics, columns=len(metrics))
    row.render()


def create_sector_comparison_metrics(
    sector_data: pd.DataFrame,
    value_column: str,
    group_column: str = "sector",
    format_type: Literal["number", "currency", "percentage", "ratio"] = "currency",
    top_n: int = 5,
) -> None:
    """
    Create comparison metrics for top sectors/industries.

    Groups data by a column and displays top N aggregated values
    as metric cards.

    Args:
        sector_data: DataFrame with sector/industry data
        value_column: Column to aggregate and display
        group_column: Column to group by
        format_type: Value format type
        top_n: Number of top groups to display

    Example:
        ```python
        create_sector_comparison_metrics(
            df,
            value_column="revenue",
            group_column="sector",
            top_n=5,
        )
        ```
    """
    # Aggregate data
    aggregated = sector_data.groupby(group_column)[value_column].sum().nlargest(top_n)

    metrics: List[MetricConfig] = []
    for group_name, value in aggregated.items():
        metrics.append(MetricConfig(
            label=str(group_name),
            value=value,
            format_type=format_type,
            delta_type="none",
        ))

    # Render
    st.caption(f"Top {top_n} by {value_column.replace('_', ' ').title()}")
    row = MetricsRow(metrics, columns=min(top_n, 5))
    row.render()


# =============================================================================
# Styled Container Utilities
# =============================================================================

def create_metric_container(
    title: str,
    metrics: List[MetricConfig],
    border_color: str = "#E0E0E0",
    background_color: str = "#FFFFFF",
) -> None:
    """
    Create a styled container with multiple metrics.

    Uses streamlit-extras stylable_container when available,
    otherwise falls back to standard Streamlit container.

    Args:
        title: Container title
        metrics: List of MetricConfig objects
        border_color: Container border color
        background_color: Container background color
    """
    if STREAMLIT_EXTRAS_AVAILABLE and stylable_container:
        with stylable_container(
            key=f"metric_container_{title.lower().replace(' ', '_')}",
            css_styles=f"""
                {{
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    padding: 1rem;
                    background-color: {background_color};
                }}
            """,
        ):
            st.markdown(f"**{title}**")
            row = MetricsRow(metrics, apply_style=False)
            row.render()
    else:
        with st.container():
            st.markdown(f"**{title}**")
            row = MetricsRow(metrics, apply_style=False)
            row.render()


def create_kpi_dashboard(
    kpis: Dict[str, List[MetricConfig]],
    columns: int = 2,
) -> None:
    """
    Create a full KPI dashboard with multiple metric groups.

    Organizes metrics into titled sections with consistent styling.

    Args:
        kpis: Dictionary mapping section titles to metric lists
        columns: Number of columns for section layout

    Example:
        ```python
        create_kpi_dashboard({
            "Profitability": [
                MetricConfig("Revenue", 1500000000, format_type="currency"),
                MetricConfig("ROE", 0.25, format_type="percentage"),
            ],
            "Leverage": [
                MetricConfig("D/E Ratio", 1.5, format_type="ratio"),
            ],
        })
        ```
    """
    # Create column layout for sections
    cols = st.columns(columns)

    for i, (section_title, section_metrics) in enumerate(kpis.items()):
        col_idx = i % columns

        with cols[col_idx]:
            create_metric_container(section_title, section_metrics)
