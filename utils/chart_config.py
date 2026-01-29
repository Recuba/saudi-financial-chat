"""Chart configuration and styling for Ra'd AI.

Provides professional chart styling, matplotlib configuration, and
custom prompts for high-quality financial visualizations.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Professional color palette for financial charts
CHART_COLORS = {
    "primary": "#D4A84B",      # Gold (brand color)
    "secondary": "#4A90D9",    # Blue
    "tertiary": "#50C878",     # Green
    "quaternary": "#E57373",   # Red
    "background": "#0E0E0E",   # Dark background
    "grid": "#2A2A2A",         # Grid lines
    "text": "#E0E0E0",         # Light text
    "accent": "#9C27B0",       # Purple accent
}

# Color palette for multiple series
SERIES_COLORS = [
    "#D4A84B",  # Gold
    "#4A90D9",  # Blue
    "#50C878",  # Green
    "#E57373",  # Red
    "#9C27B0",  # Purple
    "#FF9800",  # Orange
    "#00BCD4",  # Cyan
    "#8BC34A",  # Light Green
    "#F44336",  # Bright Red
    "#3F51B5",  # Indigo
]

# Matplotlib configuration for professional charts
MATPLOTLIB_CONFIG = {
    # Figure settings
    "figure.figsize": (12, 7),
    "figure.dpi": 150,
    "figure.facecolor": "#0E0E0E",
    "figure.edgecolor": "#0E0E0E",
    "figure.autolayout": True,

    # Axes settings
    "axes.facecolor": "#0E0E0E",
    "axes.edgecolor": "#3A3A3A",
    "axes.labelcolor": "#E0E0E0",
    "axes.titlecolor": "#FFFFFF",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "normal",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,

    # Grid settings
    "grid.color": "#2A2A2A",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,

    # Legend settings
    "legend.facecolor": "#1A1A1A",
    "legend.edgecolor": "#3A3A3A",
    "legend.fontsize": 10,
    "legend.title_fontsize": 11,
    "legend.framealpha": 0.9,
    "legend.loc": "best",

    # Text settings
    "text.color": "#E0E0E0",
    "font.family": "sans-serif",
    "font.size": 10,

    # Tick settings
    "xtick.color": "#E0E0E0",
    "ytick.color": "#E0E0E0",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "xtick.major.size": 5,
    "ytick.major.size": 5,

    # Line settings
    "lines.linewidth": 2.0,
    "lines.markersize": 6,

    # Scatter settings
    "scatter.edgecolors": "face",

    # Savefig settings
    "savefig.facecolor": "#0E0E0E",
    "savefig.edgecolor": "#0E0E0E",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.2,
}


def apply_matplotlib_config() -> None:
    """Apply professional matplotlib configuration globally.

    This should be called once at application startup to set
    consistent chart styling.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib as mpl

        # Apply all configuration settings
        for key, value in MATPLOTLIB_CONFIG.items():
            try:
                mpl.rcParams[key] = value
            except KeyError:
                logger.debug(f"Matplotlib rcParam not found: {key}")

        # Set color cycle
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=SERIES_COLORS)

        logger.info("Applied professional matplotlib configuration")

    except ImportError:
        logger.warning("Matplotlib not available, skipping chart configuration")
    except Exception as e:
        logger.error(f"Error applying matplotlib config: {e}")


def get_chart_system_prompt() -> str:
    """Get the system prompt for generating professional charts.

    Returns:
        System prompt string with chart generation instructions
    """
    return """
When generating charts and visualizations, follow these guidelines for professional, clear output:

## Chart Quality Guidelines

### Layout & Spacing
- Always use `plt.tight_layout()` or `fig.tight_layout()` to prevent label overlap
- Add adequate padding with `plt.subplots_adjust()` if needed
- For rotated x-axis labels, use `rotation=45, ha='right'` to prevent overlap
- Limit x-axis labels to 15-20 maximum; aggregate or sample if more

### Labels & Text
- Use clear, descriptive titles that explain the insight
- Include units in axis labels (e.g., "Revenue (SAR Millions)")
- Format large numbers with commas or abbreviations (K, M, B)
- Avoid overlapping text by adjusting label positions or rotation
- Use `plt.ticklabel_format(style='plain', axis='y')` for large numbers

### Regression & Trend Lines
- Always show the regression equation and R² value on the chart
- Use `annotate()` or `text()` to display statistics in a clear location
- Add confidence intervals as shaded regions when appropriate
- Include data points as scatter plot with trend line overlay

### Colors & Styling
- Use high-contrast colors that are visible on dark backgrounds
- Primary color: #D4A84B (gold)
- Secondary color: #4A90D9 (blue)
- Use consistent color mapping for categories across charts
- Add slight transparency (alpha=0.7) for overlapping elements

### Legends & Annotations
- Position legends to avoid covering data points
- Use `bbox_to_anchor` to place legends outside the plot if needed
- Add annotations for key data points or outliers
- Include source/date information in figure notes

### Specific Chart Types

**Line Charts:**
```python
plt.figure(figsize=(12, 7))
plt.plot(x, y, marker='o', linewidth=2, markersize=6)
plt.xlabel('Year', fontsize=11)
plt.ylabel('Revenue (SAR Millions)', fontsize=11)
plt.title('Revenue Trend Analysis', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
```

**Regression Charts:**
```python
import numpy as np
from scipy import stats

# Calculate regression
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
line = slope * x + intercept

plt.figure(figsize=(12, 7))
plt.scatter(x, y, alpha=0.7, s=50, label='Data Points')
plt.plot(x, line, color='#E57373', linewidth=2, label='Trend Line')

# Add equation and R²
equation = f'y = {slope:.2f}x + {intercept:.2f}'
r_squared = f'R² = {r_value**2:.4f}'
plt.annotate(f'{equation}\\n{r_squared}', xy=(0.05, 0.95), xycoords='axes fraction',
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='#1A1A1A', alpha=0.8))

plt.xlabel('Independent Variable', fontsize=11)
plt.ylabel('Dependent Variable', fontsize=11)
plt.title('Linear Regression Analysis', fontsize=14, fontweight='bold')
plt.legend(loc='lower right')
plt.tight_layout()
```

**Bar Charts:**
```python
plt.figure(figsize=(12, 7))
bars = plt.bar(categories, values, color='#D4A84B', edgecolor='#B8922E')

# Add value labels on bars
for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:,.0f}', ha='center', va='bottom', fontsize=9)

plt.xlabel('Category', fontsize=11)
plt.ylabel('Value', fontsize=11)
plt.title('Comparison by Category', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
```

### Data Preparation
- Sort data logically (chronologically, by value, or alphabetically)
- Handle missing values before plotting
- Remove outliers or note them explicitly
- Aggregate data if too granular for visualization

### Common Fixes for Messy Charts
1. **Overlapping labels**: Use `plt.xticks(rotation=45, ha='right')` and `plt.tight_layout()`
2. **Cramped layout**: Increase figure size with `figsize=(12, 7)` or larger
3. **Unreadable numbers**: Format with `'{:,.0f}'.format(x)` or use log scale
4. **Missing context**: Always include title, axis labels, and legend
5. **Color issues**: Use the provided color palette for consistency

Always prioritize clarity and readability over complexity. A simple, well-labeled chart is better than a complex, confusing one.
"""


def get_financial_analysis_prompt() -> str:
    """Get additional prompts for financial data analysis.

    Returns:
        Financial analysis prompt string
    """
    return """
## Financial Data Analysis Guidelines

### Number Formatting
- Format currency values with appropriate scale (Thousands, Millions, Billions)
- Use SAR (Saudi Riyal) as the default currency
- Show percentages with 2 decimal places for ratios
- Use comma separators for thousands

### Financial Metrics
- When showing growth rates, include both absolute and percentage change
- For ratios (ROE, ROA, etc.), show as percentages
- Compare metrics against industry averages when available
- Highlight significant changes or outliers

### Time Series
- Use fiscal year for consistency
- Show year-over-year comparisons when relevant
- Include trend direction indicators

### Sector Analysis
- Group companies by sector for comparisons
- Use consistent color coding per sector
- Show sector averages as reference lines
"""


def get_pandasai_config() -> Dict[str, Any]:
    """Get the complete PandasAI configuration with custom prompts.

    Returns:
        Dictionary with PandasAI configuration options
    """
    return {
        "custom_instructions": get_chart_system_prompt() + get_financial_analysis_prompt(),
        "enable_cache": True,
        "verbose": False,
        "enforce_privacy": False,
        "save_charts": True,
        "save_charts_path": "exports/charts",
        "open_charts": False,
    }


def enhance_chart_request(query: str) -> str:
    """Enhance a user query to produce better chart output.

    Adds specific instructions for chart quality if the query
    appears to request a visualization.

    Args:
        query: Original user query

    Returns:
        Enhanced query with chart instructions
    """
    chart_keywords = [
        'chart', 'plot', 'graph', 'visualize', 'visualization',
        'regression', 'trend', 'scatter', 'bar', 'line', 'pie',
        'histogram', 'distribution', 'correlation', 'heatmap'
    ]

    query_lower = query.lower()

    # Check if query is about charts
    is_chart_query = any(keyword in query_lower for keyword in chart_keywords)

    if is_chart_query:
        enhancement = """

Please ensure the chart follows these requirements:
1. Use plt.tight_layout() to prevent label overlap
2. Rotate x-axis labels 45 degrees if there are many categories
3. Add clear title, axis labels with units
4. Format large numbers with commas or abbreviations
5. Use figure size (12, 7) for good proportions
6. If showing regression, include the equation and R² value on the chart
7. Use high-contrast colors visible on dark backgrounds
"""
        return query + enhancement

    return query


# Chart type specific configurations
CHART_TYPE_CONFIGS = {
    "line": {
        "marker": "o",
        "linewidth": 2,
        "markersize": 6,
        "alpha": 0.9,
    },
    "scatter": {
        "s": 60,
        "alpha": 0.7,
        "edgecolors": "white",
        "linewidths": 0.5,
    },
    "bar": {
        "edgecolor": "#B8922E",
        "linewidth": 1,
        "alpha": 0.9,
    },
    "regression": {
        "scatter_alpha": 0.6,
        "line_color": "#E57373",
        "line_width": 2.5,
        "confidence_alpha": 0.2,
    },
}


def get_chart_type_config(chart_type: str) -> Dict[str, Any]:
    """Get configuration for a specific chart type.

    Args:
        chart_type: Type of chart (line, scatter, bar, regression)

    Returns:
        Configuration dictionary for the chart type
    """
    return CHART_TYPE_CONFIGS.get(chart_type, {})
