"""Advanced Financial Charts for Ra'd AI.

Provides specialized visualizations for audited financial statement analysis
including waterfall charts, ratio analysis, sector comparisons, and trend analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# Import with graceful fallback
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


# Financial color palette
FINANCIAL_COLORS = {
    "positive": "#4CAF50",      # Green for gains/positive values
    "negative": "#F44336",      # Red for losses/negative values
    "neutral": "#9E9E9E",       # Gray for neutral
    "primary": "#D4A84B",       # Gold brand color
    "secondary": "#2196F3",     # Blue
    "tertiary": "#9C27B0",      # Purple
    "background": "#0E0E0E",    # Dark background
    "card": "#1A1A1A",          # Card background
    "text": "#FFFFFF",          # White text
    "text_muted": "#888888",    # Muted text
}

# Sector colors for consistency
SECTOR_COLORS = {
    "Banks": "#1E88E5",
    "Petrochemicals": "#43A047",
    "Retail": "#FB8C00",
    "Real Estate": "#8E24AA",
    "Telecom": "#00ACC1",
    "Healthcare": "#E53935",
    "Insurance": "#5E35B1",
    "Energy": "#FDD835",
    "Materials": "#6D4C41",
    "Utilities": "#00897B",
    "Consumer Services": "#D81B60",
    "Industrials": "#3949AB",
    "Food & Beverages": "#7CB342",
    "Transportation": "#039BE5",
    "Other": "#757575",
}


def get_plotly_layout(title: str = "", height: int = 500, dark_mode: bool = True) -> Dict[str, Any]:
    """Get consistent Plotly layout configuration.

    Args:
        title: Chart title
        height: Chart height in pixels
        dark_mode: Whether to use dark mode styling

    Returns:
        Plotly layout dictionary
    """
    bg_color = FINANCIAL_COLORS["background"] if dark_mode else "#FFFFFF"
    text_color = FINANCIAL_COLORS["text"] if dark_mode else "#000000"
    grid_color = "#333333" if dark_mode else "#E0E0E0"

    return {
        "title": {
            "text": title,
            "font": {"size": 18, "color": text_color},
            "x": 0.5,
            "xanchor": "center"
        },
        "paper_bgcolor": bg_color,
        "plot_bgcolor": bg_color,
        "font": {"color": text_color, "family": "Inter, sans-serif"},
        "height": height,
        "margin": {"l": 60, "r": 40, "t": 60, "b": 60},
        "xaxis": {
            "gridcolor": grid_color,
            "zerolinecolor": grid_color,
        },
        "yaxis": {
            "gridcolor": grid_color,
            "zerolinecolor": grid_color,
        },
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": text_color}
        },
        "hovermode": "x unified",
    }


# =============================================================================
# WATERFALL CHARTS - Income Statement Analysis
# =============================================================================

def create_income_statement_waterfall(
    revenue: float,
    cost_of_sales: float,
    gross_profit: float,
    operating_expenses: float,
    operating_profit: float,
    other_income: float = 0,
    interest_expense: float = 0,
    tax_expense: float = 0,
    net_profit: float = None,
    company_name: str = "",
    fiscal_year: int = None,
    currency: str = "SAR"
) -> Optional[go.Figure]:
    """Create a waterfall chart showing income statement breakdown.

    Args:
        revenue: Total revenue
        cost_of_sales: Cost of goods sold (positive number, will be shown as decrease)
        gross_profit: Gross profit
        operating_expenses: Operating expenses (positive number)
        operating_profit: Operating profit/EBIT
        other_income: Other income/expenses (can be negative)
        interest_expense: Interest expense (positive number)
        tax_expense: Tax expense (positive number)
        net_profit: Net profit (calculated if not provided)
        company_name: Company name for title
        fiscal_year: Fiscal year
        currency: Currency code

    Returns:
        Plotly figure or None if dependencies missing
    """
    if not HAS_PLOTLY:
        logger.warning("Plotly not available for waterfall chart")
        return None

    # Calculate net profit if not provided
    if net_profit is None:
        net_profit = operating_profit + other_income - interest_expense - tax_expense

    # Define waterfall steps
    labels = [
        "Revenue",
        "Cost of Sales",
        "Gross Profit",
        "Operating Expenses",
        "Operating Profit",
        "Other Income/Expense",
        "Interest Expense",
        "Tax Expense",
        "Net Profit"
    ]

    # Measure types: relative (change), total (running total), absolute (final)
    measures = [
        "absolute",   # Revenue
        "relative",   # Cost of Sales
        "total",      # Gross Profit
        "relative",   # Operating Expenses
        "total",      # Operating Profit
        "relative",   # Other Income
        "relative",   # Interest
        "relative",   # Tax
        "total"       # Net Profit
    ]

    # Values (negatives for costs/expenses)
    values = [
        revenue,
        -abs(cost_of_sales),
        gross_profit,
        -abs(operating_expenses),
        operating_profit,
        other_income,  # Can be positive or negative
        -abs(interest_expense),
        -abs(tax_expense),
        net_profit
    ]

    # Format values for display
    def format_value(v):
        if abs(v) >= 1e9:
            return f"{currency} {v/1e9:.1f}B"
        elif abs(v) >= 1e6:
            return f"{currency} {v/1e6:.1f}M"
        elif abs(v) >= 1e3:
            return f"{currency} {v/1e3:.1f}K"
        return f"{currency} {v:.0f}"

    text_values = [format_value(v) for v in values]

    # Create figure
    fig = go.Figure(go.Waterfall(
        name="Income Statement",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        text=text_values,
        textposition="outside",
        textfont={"size": 10},
        connector={"line": {"color": FINANCIAL_COLORS["text_muted"], "width": 1, "dash": "dot"}},
        increasing={"marker": {"color": FINANCIAL_COLORS["positive"]}},
        decreasing={"marker": {"color": FINANCIAL_COLORS["negative"]}},
        totals={"marker": {"color": FINANCIAL_COLORS["primary"]}},
        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>"
    ))

    # Title
    title = "Income Statement Breakdown"
    if company_name:
        title = f"{company_name} - {title}"
    if fiscal_year:
        title += f" ({fiscal_year})"

    # Update layout
    layout = get_plotly_layout(title, height=500)
    layout["xaxis"]["tickangle"] = -45
    layout["yaxis"]["title"] = f"Amount ({currency})"
    fig.update_layout(**layout)

    return fig


def create_balance_sheet_composition(
    total_assets: float,
    current_assets: float,
    non_current_assets: float,
    total_liabilities: float,
    current_liabilities: float,
    non_current_liabilities: float,
    total_equity: float,
    company_name: str = "",
    fiscal_year: int = None,
    currency: str = "SAR"
) -> Optional[go.Figure]:
    """Create a stacked bar chart showing balance sheet composition.

    Args:
        total_assets: Total assets
        current_assets: Current assets
        non_current_assets: Non-current/fixed assets
        total_liabilities: Total liabilities
        current_liabilities: Current liabilities
        non_current_liabilities: Non-current liabilities
        total_equity: Total equity
        company_name: Company name
        fiscal_year: Fiscal year
        currency: Currency code

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY:
        return None

    def format_value(v):
        if abs(v) >= 1e9:
            return f"{currency} {v/1e9:.1f}B"
        elif abs(v) >= 1e6:
            return f"{currency} {v/1e6:.1f}M"
        return f"{currency} {v/1e3:.1f}K"

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Assets", "Liabilities & Equity"),
        horizontal_spacing=0.1
    )

    # Assets side
    fig.add_trace(
        go.Bar(
            name="Current Assets",
            x=["Assets"],
            y=[current_assets],
            marker_color="#4CAF50",
            text=[format_value(current_assets)],
            textposition="inside",
            hovertemplate="Current Assets<br>%{text}<extra></extra>"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            name="Non-Current Assets",
            x=["Assets"],
            y=[non_current_assets],
            marker_color="#2196F3",
            text=[format_value(non_current_assets)],
            textposition="inside",
            hovertemplate="Non-Current Assets<br>%{text}<extra></extra>"
        ),
        row=1, col=1
    )

    # Liabilities & Equity side
    fig.add_trace(
        go.Bar(
            name="Current Liabilities",
            x=["Liabilities & Equity"],
            y=[current_liabilities],
            marker_color="#F44336",
            text=[format_value(current_liabilities)],
            textposition="inside",
            hovertemplate="Current Liabilities<br>%{text}<extra></extra>",
            showlegend=True
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            name="Non-Current Liabilities",
            x=["Liabilities & Equity"],
            y=[non_current_liabilities],
            marker_color="#FF9800",
            text=[format_value(non_current_liabilities)],
            textposition="inside",
            hovertemplate="Non-Current Liabilities<br>%{text}<extra></extra>",
            showlegend=True
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            name="Equity",
            x=["Liabilities & Equity"],
            y=[total_equity],
            marker_color=FINANCIAL_COLORS["primary"],
            text=[format_value(total_equity)],
            textposition="inside",
            hovertemplate="Total Equity<br>%{text}<extra></extra>",
            showlegend=True
        ),
        row=1, col=2
    )

    # Title
    title = "Balance Sheet Composition"
    if company_name:
        title = f"{company_name} - {title}"
    if fiscal_year:
        title += f" ({fiscal_year})"

    layout = get_plotly_layout(title, height=500)
    layout["barmode"] = "stack"
    fig.update_layout(**layout)

    return fig


# =============================================================================
# RATIO ANALYSIS CHARTS
# =============================================================================

def create_ratio_radar_chart(
    ratios: Dict[str, float],
    benchmark_ratios: Optional[Dict[str, float]] = None,
    company_name: str = "",
    benchmark_name: str = "Industry Average"
) -> Optional[go.Figure]:
    """Create a radar chart comparing financial ratios.

    Args:
        ratios: Dictionary of ratio name to value
        benchmark_ratios: Optional benchmark ratios for comparison
        company_name: Company name
        benchmark_name: Name of benchmark (e.g., "Industry Average")

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY:
        return None

    categories = list(ratios.keys())
    values = list(ratios.values())

    # Normalize values for radar display (0-100 scale)
    if HAS_NUMPY:
        max_vals = [max(abs(v), 1) for v in values]
        if benchmark_ratios:
            for k, v in benchmark_ratios.items():
                if k in ratios:
                    idx = categories.index(k)
                    max_vals[idx] = max(max_vals[idx], abs(v))
        normalized = [(v / m) * 100 for v, m in zip(values, max_vals)]
    else:
        normalized = values

    fig = go.Figure()

    # Add company trace
    fig.add_trace(go.Scatterpolar(
        r=normalized + [normalized[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=f"rgba(212, 168, 75, 0.3)",
        line=dict(color=FINANCIAL_COLORS["primary"], width=2),
        name=company_name or "Company",
        hovertemplate="<b>%{theta}</b><br>Value: %{customdata:.2f}<extra></extra>",
        customdata=values + [values[0]]
    ))

    # Add benchmark if provided
    if benchmark_ratios:
        bench_values = [benchmark_ratios.get(k, 0) for k in categories]
        if HAS_NUMPY:
            bench_normalized = [(v / m) * 100 for v, m in zip(bench_values, max_vals)]
        else:
            bench_normalized = bench_values

        fig.add_trace(go.Scatterpolar(
            r=bench_normalized + [bench_normalized[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor="rgba(33, 150, 243, 0.2)",
            line=dict(color=FINANCIAL_COLORS["secondary"], width=2, dash="dash"),
            name=benchmark_name,
            hovertemplate="<b>%{theta}</b><br>Value: %{customdata:.2f}<extra></extra>",
            customdata=bench_values + [bench_values[0]]
        ))

    title = f"Financial Ratios Analysis"
    if company_name:
        title = f"{company_name} - {title}"

    layout = get_plotly_layout(title, height=500)
    layout["polar"] = {
        "radialaxis": {
            "visible": True,
            "range": [0, 100],
            "gridcolor": "#333333",
        },
        "bgcolor": FINANCIAL_COLORS["card"]
    }
    fig.update_layout(**layout)

    return fig


def create_ratio_comparison_bars(
    companies: List[str],
    ratios_data: Dict[str, List[float]],
    ratio_types: Optional[Dict[str, str]] = None,
    title: str = "Financial Ratio Comparison"
) -> Optional[go.Figure]:
    """Create grouped bar chart comparing ratios across companies.

    Args:
        companies: List of company names
        ratios_data: Dict mapping ratio name to list of values (one per company)
        ratio_types: Optional dict mapping ratio name to type (percentage, ratio, currency)
        title: Chart title

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY:
        return None

    fig = go.Figure()

    colors = [
        FINANCIAL_COLORS["primary"],
        FINANCIAL_COLORS["secondary"],
        FINANCIAL_COLORS["tertiary"],
        FINANCIAL_COLORS["positive"],
        "#FF9800",
        "#00BCD4",
    ]

    for i, (ratio_name, values) in enumerate(ratios_data.items()):
        # Format hover text based on ratio type
        ratio_type = ratio_types.get(ratio_name, "ratio") if ratio_types else "ratio"

        if ratio_type == "percentage":
            hover_template = f"<b>{ratio_name}</b><br>%{{y:.1f}}%<extra></extra>"
        elif ratio_type == "currency":
            hover_template = f"<b>{ratio_name}</b><br>SAR %{{y:,.0f}}<extra></extra>"
        else:
            hover_template = f"<b>{ratio_name}</b><br>%{{y:.2f}}x<extra></extra>"

        fig.add_trace(go.Bar(
            name=ratio_name,
            x=companies,
            y=values,
            marker_color=colors[i % len(colors)],
            hovertemplate=hover_template
        ))

    layout = get_plotly_layout(title, height=450)
    layout["barmode"] = "group"
    layout["xaxis"]["tickangle"] = -45
    fig.update_layout(**layout)

    return fig


# =============================================================================
# TREND ANALYSIS CHARTS
# =============================================================================

def create_multi_year_trend(
    df: "pd.DataFrame",
    company_name: str,
    metrics: List[str],
    year_column: str = "fiscal_year",
    currency: str = "SAR"
) -> Optional[go.Figure]:
    """Create multi-year trend analysis for a company.

    Args:
        df: DataFrame with company data
        company_name: Company to analyze
        metrics: List of metric columns to plot
        year_column: Column containing fiscal year
        currency: Currency code

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return None

    # Filter for company
    company_df = df[df["company_name"] == company_name].sort_values(year_column)

    if len(company_df) == 0:
        return None

    fig = make_subplots(
        rows=len(metrics), cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=metrics
    )

    colors = [
        FINANCIAL_COLORS["primary"],
        FINANCIAL_COLORS["secondary"],
        FINANCIAL_COLORS["positive"],
        FINANCIAL_COLORS["tertiary"],
    ]

    for i, metric in enumerate(metrics, 1):
        if metric not in company_df.columns:
            continue

        years = company_df[year_column].tolist()
        values = company_df[metric].tolist()

        # Calculate YoY change
        changes = [0]
        for j in range(1, len(values)):
            if values[j-1] != 0:
                change = ((values[j] - values[j-1]) / abs(values[j-1])) * 100
                changes.append(change)
            else:
                changes.append(0)

        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines+markers",
                name=metric,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=8),
                hovertemplate=(
                    f"<b>{metric}</b><br>"
                    f"Year: %{{x}}<br>"
                    f"Value: {currency} %{{y:,.0f}}<br>"
                    f"YoY: %{{customdata:.1f}}%<extra></extra>"
                ),
                customdata=changes
            ),
            row=i, col=1
        )

    title = f"{company_name} - Multi-Year Financial Trends"
    layout = get_plotly_layout(title, height=200 * len(metrics))
    fig.update_layout(**layout)

    return fig


def create_yoy_comparison_chart(
    df: "pd.DataFrame",
    metric: str,
    year1: int,
    year2: int,
    top_n: int = 10,
    currency: str = "SAR"
) -> Optional[go.Figure]:
    """Create year-over-year comparison chart for a metric.

    Args:
        df: DataFrame with company data
        metric: Metric to compare
        year1: First year (earlier)
        year2: Second year (later)
        top_n: Number of top companies to show
        currency: Currency code

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return None

    # Get data for both years
    df1 = df[df["fiscal_year"] == year1][["company_name", metric]].copy()
    df2 = df[df["fiscal_year"] == year2][["company_name", metric]].copy()

    df1.columns = ["company_name", f"{metric}_{year1}"]
    df2.columns = ["company_name", f"{metric}_{year2}"]

    # Merge
    merged = pd.merge(df1, df2, on="company_name", how="inner")

    # Calculate change
    merged["change"] = merged[f"{metric}_{year2}"] - merged[f"{metric}_{year1}"]
    merged["change_pct"] = (merged["change"] / merged[f"{metric}_{year1}"].abs()) * 100

    # Sort by absolute change and take top N
    merged = merged.nlargest(top_n, f"{metric}_{year2}")

    fig = go.Figure()

    # Year 1 bars
    fig.add_trace(go.Bar(
        name=str(year1),
        x=merged["company_name"],
        y=merged[f"{metric}_{year1}"],
        marker_color=FINANCIAL_COLORS["secondary"],
        hovertemplate=f"<b>%{{x}}</b><br>{year1}: {currency} %{{y:,.0f}}<extra></extra>"
    ))

    # Year 2 bars
    fig.add_trace(go.Bar(
        name=str(year2),
        x=merged["company_name"],
        y=merged[f"{metric}_{year2}"],
        marker_color=FINANCIAL_COLORS["primary"],
        hovertemplate=(
            f"<b>%{{x}}</b><br>{year2}: {currency} %{{y:,.0f}}<br>"
            f"Change: %{{customdata:.1f}}%<extra></extra>"
        ),
        customdata=merged["change_pct"]
    ))

    title = f"{metric.replace('_', ' ').title()} - {year1} vs {year2} Comparison"
    layout = get_plotly_layout(title, height=500)
    layout["barmode"] = "group"
    layout["xaxis"]["tickangle"] = -45
    fig.update_layout(**layout)

    return fig


# =============================================================================
# SECTOR ANALYSIS CHARTS
# =============================================================================

def create_sector_sunburst(
    df: "pd.DataFrame",
    value_column: str = "revenue",
    sector_column: str = "sector",
    company_column: str = "company_name",
    currency: str = "SAR"
) -> Optional[go.Figure]:
    """Create a sunburst chart showing sector and company hierarchy.

    Args:
        df: DataFrame with company data
        value_column: Column to use for sizing
        sector_column: Column containing sector names
        company_column: Column containing company names
        currency: Currency code

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return None

    # Aggregate data
    sector_totals = df.groupby(sector_column)[value_column].sum().reset_index()

    ids = []
    labels = []
    parents = []
    values = []
    colors = []

    # Add sectors
    for _, row in sector_totals.iterrows():
        sector = row[sector_column]
        ids.append(sector)
        labels.append(sector)
        parents.append("")
        values.append(row[value_column])
        colors.append(SECTOR_COLORS.get(sector, SECTOR_COLORS["Other"]))

    # Add companies
    for _, row in df.iterrows():
        company = row[company_column]
        sector = row[sector_column]
        value = row[value_column]

        company_id = f"{sector}/{company}"
        ids.append(company_id)
        labels.append(company[:25] + "..." if len(company) > 25 else company)
        parents.append(sector)
        values.append(value)
        colors.append(SECTOR_COLORS.get(sector, SECTOR_COLORS["Other"]))

    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors),
        hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<br>Percent: %{percentParent:.1%}<extra></extra>",
        textfont=dict(color="white"),
    ))

    title = f"Market Composition by {value_column.replace('_', ' ').title()}"
    layout = get_plotly_layout(title, height=600)
    fig.update_layout(**layout)

    return fig


def create_sector_performance_heatmap(
    df: "pd.DataFrame",
    metrics: List[str],
    sector_column: str = "sector",
    aggregation: str = "mean"
) -> Optional[go.Figure]:
    """Create a heatmap showing sector performance across metrics.

    Args:
        df: DataFrame with company data
        metrics: List of metric columns to include
        sector_column: Column containing sector names
        aggregation: Aggregation method (mean, median, sum)

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return None

    # Aggregate by sector
    if aggregation == "mean":
        sector_data = df.groupby(sector_column)[metrics].mean()
    elif aggregation == "median":
        sector_data = df.groupby(sector_column)[metrics].median()
    else:
        sector_data = df.groupby(sector_column)[metrics].sum()

    # Normalize for heatmap display (z-score or min-max)
    if HAS_NUMPY:
        normalized = (sector_data - sector_data.min()) / (sector_data.max() - sector_data.min())
    else:
        normalized = sector_data

    fig = go.Figure(go.Heatmap(
        z=normalized.values,
        x=[m.replace("_", " ").title() for m in metrics],
        y=sector_data.index.tolist(),
        colorscale=[
            [0, FINANCIAL_COLORS["negative"]],
            [0.5, FINANCIAL_COLORS["neutral"]],
            [1, FINANCIAL_COLORS["positive"]]
        ],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Metric: %{x}<br>"
            "Normalized: %{z:.2f}<extra></extra>"
        ),
        showscale=True,
        colorbar=dict(title="Performance", tickformat=".1f")
    ))

    title = f"Sector Performance Heatmap ({aggregation.title()})"
    layout = get_plotly_layout(title, height=max(400, len(sector_data) * 40))
    layout["xaxis"]["tickangle"] = -45
    fig.update_layout(**layout)

    return fig


# =============================================================================
# RISK-RETURN ANALYSIS
# =============================================================================

def create_risk_return_scatter(
    df: "pd.DataFrame",
    return_column: str = "roe",
    risk_column: str = "debt_to_equity",
    size_column: str = "total_assets",
    company_column: str = "company_name",
    sector_column: str = "sector",
    title: str = "Risk-Return Analysis"
) -> Optional[go.Figure]:
    """Create a risk-return scatter plot.

    Args:
        df: DataFrame with company data
        return_column: Column representing returns (e.g., ROE)
        risk_column: Column representing risk (e.g., debt ratio)
        size_column: Column for bubble size
        company_column: Column with company names
        sector_column: Column with sector names
        title: Chart title

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return None

    # Clean data
    plot_df = df.dropna(subset=[return_column, risk_column]).copy()

    if len(plot_df) == 0:
        return None

    # Normalize size
    if size_column in plot_df.columns:
        sizes = plot_df[size_column]
        min_size, max_size = 10, 60
        normalized_sizes = min_size + (sizes - sizes.min()) / (sizes.max() - sizes.min()) * (max_size - min_size)
        plot_df["_size"] = normalized_sizes.fillna(min_size)
    else:
        plot_df["_size"] = 20

    fig = go.Figure()

    # Group by sector and plot
    for sector in plot_df[sector_column].unique():
        sector_df = plot_df[plot_df[sector_column] == sector]

        fig.add_trace(go.Scatter(
            x=sector_df[risk_column],
            y=sector_df[return_column],
            mode="markers",
            name=sector,
            marker=dict(
                size=sector_df["_size"],
                color=SECTOR_COLORS.get(sector, SECTOR_COLORS["Other"]),
                opacity=0.7,
                line=dict(width=1, color="white")
            ),
            text=sector_df[company_column],
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{return_column.upper()}: %{{y:.1f}}%<br>"
                f"{risk_column.replace('_', ' ').title()}: %{{x:.2f}}<br>"
                "<extra></extra>"
            )
        ))

    # Add quadrant lines (median values)
    median_return = plot_df[return_column].median()
    median_risk = plot_df[risk_column].median()

    fig.add_hline(y=median_return, line_dash="dash", line_color=FINANCIAL_COLORS["text_muted"], opacity=0.5)
    fig.add_vline(x=median_risk, line_dash="dash", line_color=FINANCIAL_COLORS["text_muted"], opacity=0.5)

    # Add quadrant labels
    fig.add_annotation(x=0.02, y=0.98, text="Low Risk<br>High Return",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=10, color=FINANCIAL_COLORS["positive"]))
    fig.add_annotation(x=0.98, y=0.98, text="High Risk<br>High Return",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=10, color=FINANCIAL_COLORS["primary"]))
    fig.add_annotation(x=0.02, y=0.02, text="Low Risk<br>Low Return",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=10, color=FINANCIAL_COLORS["neutral"]))
    fig.add_annotation(x=0.98, y=0.02, text="High Risk<br>Low Return",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=10, color=FINANCIAL_COLORS["negative"]))

    layout = get_plotly_layout(title, height=600)
    layout["xaxis"]["title"] = risk_column.replace("_", " ").title()
    layout["yaxis"]["title"] = return_column.upper() + " (%)"
    fig.update_layout(**layout)

    return fig


# =============================================================================
# FINANCIAL RATIO DASHBOARD
# =============================================================================

def create_financial_dashboard(
    company_data: Dict[str, Any],
    industry_benchmarks: Optional[Dict[str, float]] = None,
    company_name: str = "",
    fiscal_year: int = None
) -> Optional[go.Figure]:
    """Create a comprehensive financial dashboard with multiple KPIs.

    Args:
        company_data: Dictionary with financial metrics
        industry_benchmarks: Optional industry average benchmarks
        company_name: Company name
        fiscal_year: Fiscal year

    Returns:
        Plotly figure or None
    """
    if not HAS_PLOTLY:
        return None

    # Define KPI categories
    profitability = ["roe", "roa", "net_margin", "gross_margin"]
    liquidity = ["current_ratio", "quick_ratio"]
    leverage = ["debt_to_equity", "debt_to_assets"]
    efficiency = ["asset_turnover", "inventory_turnover"]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Profitability", "Liquidity", "Leverage", "Efficiency"),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )

    def add_gauge(row, col, title, value, benchmark=None, suffix="%", range_max=None):
        reference = None
        if benchmark is not None:
            reference = {"reference": benchmark, "relative": True}

        if range_max is None:
            range_max = max(abs(value) * 2, 100) if value else 100

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=value or 0,
                title={"text": title, "font": {"size": 14}},
                number={"suffix": suffix},
                delta=reference,
                gauge={
                    "axis": {"range": [0, range_max]},
                    "bar": {"color": FINANCIAL_COLORS["primary"]},
                    "steps": [
                        {"range": [0, range_max * 0.3], "color": FINANCIAL_COLORS["negative"]},
                        {"range": [range_max * 0.3, range_max * 0.7], "color": FINANCIAL_COLORS["neutral"]},
                        {"range": [range_max * 0.7, range_max], "color": FINANCIAL_COLORS["positive"]},
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.75,
                        "value": benchmark if benchmark else value * 0.9
                    }
                }
            ),
            row=row, col=col
        )

    # Add profitability gauge (use first available metric)
    for metric in profitability:
        if metric in company_data and company_data[metric] is not None:
            benchmark = industry_benchmarks.get(metric) if industry_benchmarks else None
            add_gauge(1, 1, metric.upper(), company_data[metric], benchmark)
            break

    # Add liquidity gauge
    for metric in liquidity:
        if metric in company_data and company_data[metric] is not None:
            benchmark = industry_benchmarks.get(metric) if industry_benchmarks else None
            add_gauge(1, 2, metric.replace("_", " ").title(), company_data[metric], benchmark, "x", 5)
            break

    # Add leverage gauge
    for metric in leverage:
        if metric in company_data and company_data[metric] is not None:
            benchmark = industry_benchmarks.get(metric) if industry_benchmarks else None
            add_gauge(2, 1, metric.replace("_", " ").title(), company_data[metric], benchmark, "x", 3)
            break

    # Add efficiency gauge
    for metric in efficiency:
        if metric in company_data and company_data[metric] is not None:
            benchmark = industry_benchmarks.get(metric) if industry_benchmarks else None
            add_gauge(2, 2, metric.replace("_", " ").title(), company_data[metric], benchmark, "x", 10)
            break

    title = "Financial Performance Dashboard"
    if company_name:
        title = f"{company_name} - {title}"
    if fiscal_year:
        title += f" ({fiscal_year})"

    layout = get_plotly_layout(title, height=600)
    fig.update_layout(**layout)

    return fig


# =============================================================================
# CHART RECOMMENDATION ENGINE
# =============================================================================

def recommend_chart(
    query: str,
    df: "pd.DataFrame" = None,
    available_columns: List[str] = None
) -> Dict[str, Any]:
    """Recommend the best chart type based on query and data.

    Args:
        query: User's natural language query
        df: Optional DataFrame to analyze
        available_columns: List of available columns

    Returns:
        Dictionary with chart recommendation and parameters
    """
    query_lower = query.lower()

    recommendations = {
        "chart_type": None,
        "function": None,
        "params": {},
        "description": ""
    }

    # Income statement keywords
    if any(kw in query_lower for kw in ["income statement", "waterfall", "profit breakdown", "revenue to profit"]):
        recommendations["chart_type"] = "income_waterfall"
        recommendations["function"] = "create_income_statement_waterfall"
        recommendations["description"] = "Waterfall chart showing income statement progression from revenue to net profit"

    # Balance sheet keywords
    elif any(kw in query_lower for kw in ["balance sheet", "assets and liabilities", "asset composition"]):
        recommendations["chart_type"] = "balance_sheet"
        recommendations["function"] = "create_balance_sheet_composition"
        recommendations["description"] = "Stacked bar chart showing balance sheet composition"

    # Ratio analysis keywords
    elif any(kw in query_lower for kw in ["ratio", "roe", "roa", "margin", "financial health"]):
        if any(kw in query_lower for kw in ["compare", "vs", "versus", "between"]):
            recommendations["chart_type"] = "ratio_comparison"
            recommendations["function"] = "create_ratio_comparison_bars"
            recommendations["description"] = "Grouped bar chart comparing ratios across companies"
        else:
            recommendations["chart_type"] = "ratio_radar"
            recommendations["function"] = "create_ratio_radar_chart"
            recommendations["description"] = "Radar chart showing company's ratio profile"

    # Trend keywords
    elif any(kw in query_lower for kw in ["trend", "over time", "historical", "growth", "year over year", "yoy"]):
        if "compare" in query_lower or "vs" in query_lower:
            recommendations["chart_type"] = "yoy_comparison"
            recommendations["function"] = "create_yoy_comparison_chart"
            recommendations["description"] = "Bar chart comparing metrics across years"
        else:
            recommendations["chart_type"] = "multi_year_trend"
            recommendations["function"] = "create_multi_year_trend"
            recommendations["description"] = "Line chart showing multi-year trends"

    # Sector keywords
    elif any(kw in query_lower for kw in ["sector", "industry", "market share", "composition"]):
        if any(kw in query_lower for kw in ["heatmap", "performance", "compare sectors"]):
            recommendations["chart_type"] = "sector_heatmap"
            recommendations["function"] = "create_sector_performance_heatmap"
            recommendations["description"] = "Heatmap showing sector performance across metrics"
        else:
            recommendations["chart_type"] = "sector_sunburst"
            recommendations["function"] = "create_sector_sunburst"
            recommendations["description"] = "Sunburst chart showing market composition by sector"

    # Risk-return keywords
    elif any(kw in query_lower for kw in ["risk", "return", "scatter", "quadrant", "portfolio"]):
        recommendations["chart_type"] = "risk_return"
        recommendations["function"] = "create_risk_return_scatter"
        recommendations["description"] = "Scatter plot showing risk-return profile with quadrants"

    # Dashboard keywords
    elif any(kw in query_lower for kw in ["dashboard", "overview", "summary", "kpi", "health check"]):
        recommendations["chart_type"] = "dashboard"
        recommendations["function"] = "create_financial_dashboard"
        recommendations["description"] = "Multi-gauge dashboard showing key financial metrics"

    # Default to bar chart
    else:
        recommendations["chart_type"] = "bar"
        recommendations["function"] = None
        recommendations["description"] = "Standard bar chart for comparison"

    return recommendations


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    # Waterfall & Composition
    "create_income_statement_waterfall",
    "create_balance_sheet_composition",
    # Ratio Analysis
    "create_ratio_radar_chart",
    "create_ratio_comparison_bars",
    # Trend Analysis
    "create_multi_year_trend",
    "create_yoy_comparison_chart",
    # Sector Analysis
    "create_sector_sunburst",
    "create_sector_performance_heatmap",
    # Risk-Return
    "create_risk_return_scatter",
    # Dashboard
    "create_financial_dashboard",
    # Utilities
    "recommend_chart",
    "get_plotly_layout",
    # Colors
    "FINANCIAL_COLORS",
    "SECTOR_COLORS",
]
