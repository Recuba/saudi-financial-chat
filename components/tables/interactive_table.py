"""
Interactive Table Component using ITables for Saudi Financial Chat.

Provides a searchable, filterable table component for large financial datasets
with client-side processing for fast search and pagination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Import guard for itables
try:
    from itables import to_html_datatable
    from itables import options as itables_options
    ITABLES_AVAILABLE = True
except ImportError:
    ITABLES_AVAILABLE = False
    to_html_datatable = None
    itables_options = None


# =============================================================================
# Number Formatting Utilities
# =============================================================================

def format_sar_display(value: float, abbreviated: bool = True) -> str:
    """
    Format a value as SAR currency for display.

    Args:
        value: Numeric value to format
        abbreviated: Use K/M/B abbreviations

    Returns:
        Formatted SAR string
    """
    if pd.isna(value):
        return "-"

    if abbreviated:
        abs_val = abs(value)
        if abs_val >= 1e9:
            return f"SAR {value / 1e9:.1f}B"
        elif abs_val >= 1e6:
            return f"SAR {value / 1e6:.1f}M"
        elif abs_val >= 1e3:
            return f"SAR {value / 1e3:.1f}K"

    return f"SAR {value:,.2f}"


def format_percentage_display(value: float) -> str:
    """Format a decimal value as percentage."""
    if pd.isna(value):
        return "-"
    return f"{value * 100:.2f}%"


def format_ratio_display(value: float) -> str:
    """Format a value as a ratio."""
    if pd.isna(value):
        return "-"
    return f"{value:.2f}x"


# =============================================================================
# Column Type Detection
# =============================================================================

def detect_column_type(df: pd.DataFrame, column: str) -> str:
    """
    Detect the likely type of a financial column.

    Args:
        df: DataFrame containing the column
        column: Column name

    Returns:
        Column type string: 'currency', 'percentage', 'ratio', 'number', 'text'
    """
    col_lower = column.lower()
    dtype = df[column].dtype

    if not pd.api.types.is_numeric_dtype(dtype):
        return "text"

    # Check column name patterns
    if any(x in col_lower for x in ["roe", "roa", "margin", "rate", "percent", "pct", "yield"]):
        return "percentage"
    elif any(x in col_lower for x in ["debt_to", "d/e", "ratio", "leverage", "coverage"]):
        return "ratio"
    elif any(x in col_lower for x in ["revenue", "profit", "asset", "equity", "income",
                                       "expense", "sar", "capital", "liability", "cash"]):
        return "currency"
    elif any(x in col_lower for x in ["year", "count", "number", "qty", "quantity"]):
        return "number"

    # Check value ranges for heuristics
    max_val = df[column].abs().max()
    if pd.notna(max_val):
        if max_val <= 1:  # Likely a ratio or percentage
            mean_val = df[column].mean()
            if pd.notna(mean_val) and 0 <= mean_val <= 1:
                return "percentage"
            return "ratio"
        elif max_val >= 1000:  # Likely currency
            return "currency"

    return "number"


# =============================================================================
# DataTable Configuration
# =============================================================================

@dataclass
class TableColumn:
    """Configuration for a single table column."""

    name: str
    title: Optional[str] = None
    column_type: Literal["text", "currency", "percentage", "ratio", "number"] = "text"
    searchable: bool = True
    orderable: bool = True
    visible: bool = True
    width: Optional[str] = None
    class_name: Optional[str] = None

    @property
    def display_title(self) -> str:
        """Get the display title for the column."""
        return self.title or self.name.replace("_", " ").title()


@dataclass
class TableOptions:
    """ITables configuration options."""

    page_length: int = 25
    length_menu: List[int] = field(default_factory=lambda: [10, 25, 50, 100])
    searching: bool = True
    ordering: bool = True
    info: bool = True
    paging: bool = True
    scroll_x: bool = True
    scroll_y: Optional[str] = None  # e.g., "400px"
    dom: str = "lfrtip"  # DataTables DOM positioning
    language: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to ITables options dictionary."""
        opts = {
            "pageLength": self.page_length,
            "lengthMenu": self.length_menu,
            "searching": self.searching,
            "ordering": self.ordering,
            "info": self.info,
            "paging": self.paging,
            "scrollX": self.scroll_x,
            "dom": self.dom,
        }

        if self.scroll_y:
            opts["scrollY"] = self.scroll_y

        if self.language:
            opts["language"] = self.language

        return opts


# =============================================================================
# Interactive Table Class
# =============================================================================

class InteractiveTable:
    """
    Interactive searchable table component using ITables.

    Provides fast client-side search and filtering for large financial datasets.
    Automatically formats SAR currency, percentages, and ratios based on column types.

    Features:
    - Fast client-side search across all columns
    - Column-level sorting
    - Pagination with configurable page sizes
    - Auto-detection of financial column types
    - SAR currency formatting with K/M/B abbreviations
    - Fallback to st.dataframe when ITables not available

    Example:
        ```python
        from components.tables import InteractiveTable

        table = InteractiveTable(
            data=financial_df,
            search_enabled=True,
            page_size=25,
        )
        table.render()
        ```
    """

    def __init__(
        self,
        data: pd.DataFrame,
        columns: Optional[List[TableColumn]] = None,
        options: Optional[TableOptions] = None,
        format_values: bool = True,
        height: int = 600,
        key: Optional[str] = None,
    ):
        """
        Initialize the Interactive Table.

        Args:
            data: DataFrame containing financial data
            columns: Column configurations (auto-detected if None)
            options: Table display options
            format_values: Auto-format currency/percentage values
            height: Component height in pixels
            key: Unique key for component state
        """
        self.original_data = data.copy()
        self.columns = columns or self._auto_detect_columns()
        self.options = options or TableOptions()
        self.format_values = format_values
        self.height = height
        self.key = key or "interactive_table"

        # Prepare display data
        self.display_data = self._prepare_display_data()

    def _auto_detect_columns(self) -> List[TableColumn]:
        """Auto-detect column configurations from DataFrame."""
        configs: List[TableColumn] = []

        for col in self.original_data.columns:
            col_type = detect_column_type(self.original_data, col)

            configs.append(TableColumn(
                name=col,
                column_type=col_type,
            ))

        return configs

    def _prepare_display_data(self) -> pd.DataFrame:
        """Prepare data for display with formatting applied."""
        if not self.format_values:
            return self.original_data.copy()

        display_df = self.original_data.copy()

        for col_config in self.columns:
            if col_config.name not in display_df.columns:
                continue

            if col_config.column_type == "currency":
                display_df[col_config.name] = display_df[col_config.name].apply(
                    lambda x: format_sar_display(x, abbreviated=True)
                )
            elif col_config.column_type == "percentage":
                display_df[col_config.name] = display_df[col_config.name].apply(
                    format_percentage_display
                )
            elif col_config.column_type == "ratio":
                display_df[col_config.name] = display_df[col_config.name].apply(
                    format_ratio_display
                )

        # Rename columns to display titles
        rename_map = {
            col.name: col.display_title
            for col in self.columns
            if col.name in display_df.columns
        }
        display_df = display_df.rename(columns=rename_map)

        return display_df

    def _generate_html_table(self) -> str:
        """Generate HTML for the interactive table."""
        if not ITABLES_AVAILABLE:
            return ""

        # Build column definitions
        column_defs = []
        for i, col in enumerate(self.columns):
            if col.name not in self.original_data.columns:
                continue
            col_def = {
                "targets": i,
                "searchable": col.searchable,
                "orderable": col.orderable,
                "visible": col.visible,
            }
            if col.width:
                col_def["width"] = col.width
            if col.class_name:
                col_def["className"] = col.class_name
            column_defs.append(col_def)

        # Generate HTML using ITables
        options_dict = self.options.to_dict()
        options_dict["columnDefs"] = column_defs

        html = to_html_datatable(
            self.display_data,
            **options_dict,
        )

        return html

    def _render_fallback(self) -> None:
        """Render fallback using st.dataframe when ITables not available."""
        st.warning("ITables not available. Install with: `pip install itables`")

        # Add search box
        search_term = st.text_input(
            "Search",
            key=f"{self.key}_search",
            placeholder="Type to search...",
        )

        # Filter data based on search
        filtered_df = self.display_data
        if search_term:
            mask = self.display_data.apply(
                lambda row: row.astype(str).str.contains(search_term, case=False).any(),
                axis=1
            )
            filtered_df = self.display_data[mask]

        # Display info
        st.caption(f"Showing {len(filtered_df)} of {len(self.display_data)} entries")

        # Render with native Streamlit
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=self.height,
        )

    def render(self) -> None:
        """Render the interactive table."""
        if not ITABLES_AVAILABLE:
            self._render_fallback()
            return

        # Generate and display the HTML table
        html_content = self._generate_html_table()

        # Wrap in a styled container
        styled_html = f"""
        <style>
            .dataTables_wrapper {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                font-size: 14px;
            }}
            .dataTables_filter input {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 10px;
                margin-left: 5px;
            }}
            .dataTables_length select {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }}
            table.dataTable {{
                border-collapse: collapse;
                width: 100%;
            }}
            table.dataTable thead th {{
                background-color: #f8f9fa;
                border-bottom: 2px solid #dee2e6;
                padding: 12px 8px;
                text-align: left;
                font-weight: 600;
            }}
            table.dataTable tbody td {{
                padding: 10px 8px;
                border-bottom: 1px solid #dee2e6;
            }}
            table.dataTable tbody tr:hover {{
                background-color: #f5f5f5;
            }}
            .dataTables_info {{
                color: #666;
                padding-top: 10px;
            }}
            .dataTables_paginate {{
                padding-top: 10px;
            }}
            .dataTables_paginate .paginate_button {{
                padding: 5px 10px;
                margin: 0 2px;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
            }}
            .dataTables_paginate .paginate_button.current {{
                background-color: #0066cc;
                color: white;
                border-color: #0066cc;
            }}
            .dataTables_paginate .paginate_button:hover:not(.current) {{
                background-color: #f0f0f0;
            }}
        </style>
        {html_content}
        """

        components.html(styled_html, height=self.height, scrolling=True)

    def get_filtered_data(self, search_term: str) -> pd.DataFrame:
        """
        Get filtered data based on search term.

        Note: This filters the original data, not formatted display data.

        Args:
            search_term: Search string to filter by

        Returns:
            Filtered DataFrame
        """
        if not search_term:
            return self.original_data.copy()

        mask = self.original_data.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1
        )
        return self.original_data[mask].copy()


# =============================================================================
# Convenience Function
# =============================================================================

def create_interactive_table(
    data: pd.DataFrame,
    search_enabled: bool = True,
    page_size: int = 25,
    format_values: bool = True,
    show_row_count: bool = True,
    height: int = 600,
    key: Optional[str] = None,
) -> None:
    """
    Create and render an interactive searchable table.

    Convenience function for quickly displaying financial data with
    search and pagination capabilities.

    Args:
        data: DataFrame containing financial data
        search_enabled: Enable search functionality
        page_size: Default number of rows per page
        format_values: Auto-format currency/percentage values
        show_row_count: Show total row count above table
        height: Component height in pixels
        key: Unique component key

    Example:
        ```python
        from components.tables import create_interactive_table

        create_interactive_table(
            financial_df,
            search_enabled=True,
            page_size=50,
        )
        ```
    """
    if show_row_count:
        st.caption(f"Total records: {len(data):,}")

    options = TableOptions(
        page_length=page_size,
        searching=search_enabled,
    )

    table = InteractiveTable(
        data=data,
        options=options,
        format_values=format_values,
        height=height,
        key=key,
    )

    table.render()


def create_searchable_dataframe(
    data: pd.DataFrame,
    search_columns: Optional[List[str]] = None,
    format_columns: Optional[Dict[str, str]] = None,
    key: str = "searchable_df",
) -> pd.DataFrame:
    """
    Create a simple searchable dataframe with manual search input.

    This is a lightweight alternative that doesn't require ITables,
    using only native Streamlit components.

    Args:
        data: DataFrame to display
        search_columns: Columns to search in (all if None)
        format_columns: Dict mapping column names to format types
        key: Unique key for search input

    Returns:
        Filtered DataFrame based on search input

    Example:
        ```python
        filtered_df = create_searchable_dataframe(
            df,
            search_columns=["company_name", "sector"],
            format_columns={"revenue": "currency", "ROE": "percentage"},
        )
        ```
    """
    # Search input
    search_term = st.text_input(
        "Search",
        key=key,
        placeholder="Type to search across all columns...",
    )

    # Filter data
    filtered_df = data.copy()
    if search_term:
        search_cols = search_columns or data.columns.tolist()
        mask = data[search_cols].apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1
        )
        filtered_df = data[mask].copy()

    # Format columns if specified
    display_df = filtered_df.copy()
    if format_columns:
        for col, fmt_type in format_columns.items():
            if col not in display_df.columns:
                continue
            if fmt_type == "currency":
                display_df[col] = display_df[col].apply(format_sar_display)
            elif fmt_type == "percentage":
                display_df[col] = display_df[col].apply(format_percentage_display)
            elif fmt_type == "ratio":
                display_df[col] = display_df[col].apply(format_ratio_display)

    # Display info and table
    st.caption(f"Showing {len(filtered_df)} of {len(data)} records")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    return filtered_df
