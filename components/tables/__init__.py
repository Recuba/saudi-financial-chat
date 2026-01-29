"""
Data Tables & Grids Components for Saudi Financial Chat.

This package provides high-performance table components for displaying
and interacting with financial data from Saudi-listed companies.

Components:
- FinancialGrid: AG-Grid based component with SAR formatting, export, and selection
- InteractiveTable: ITables component with search and filtering for large datasets
- MetricCard: Styled metric cards with delta calculations and K/M/B formatting
"""

from typing import TYPE_CHECKING

# Component imports with availability flags
from .financial_grid import (
    FinancialGrid,
    create_financial_grid,
    AGGRID_AVAILABLE,
)

from .interactive_table import (
    InteractiveTable,
    create_interactive_table,
    ITABLES_AVAILABLE,
)

from .metrics import (
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

__all__ = [
    # Financial Grid
    "FinancialGrid",
    "create_financial_grid",
    "AGGRID_AVAILABLE",
    # Interactive Table
    "InteractiveTable",
    "create_interactive_table",
    "ITABLES_AVAILABLE",
    # Metrics
    "MetricCard",
    "MetricConfig",
    "MetricsRow",
    "format_number_abbreviated",
    "format_sar_currency",
    "calculate_delta_percentage",
    "create_financial_metrics",
    "create_company_metrics_summary",
    "STREAMLIT_EXTRAS_AVAILABLE",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Saudi Financial Chat Team"
