"""
AG-Grid Financial Data Component for Saudi Financial Chat.

Provides a high-performance data grid for displaying Saudi financial data
with SAR currency formatting, percentage columns, Excel export, and row selection.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import pandas as pd
import streamlit as st

# Import guard for streamlit-aggrid
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
    from st_aggrid.shared import ExcelExportMode
    AGGRID_AVAILABLE = True
except ImportError:
    AGGRID_AVAILABLE = False
    AgGrid = None
    GridOptionsBuilder = None
    GridUpdateMode = None
    JsCode = None
    ExcelExportMode = None


# =============================================================================
# Currency and Number Formatting
# =============================================================================

def format_sar_value(value: float, decimals: int = 1, use_scale: bool = True) -> str:
    """
    Format a numeric value as SR currency with proper scaling.

    Scale factor is '000 (thousands). Values shown in MM (millions) or B (billions).
    Example: 1,000,000 -> "SR 1,000MM" (1 million = 1,000 thousands)

    Args:
        value: The numeric value to format
        decimals: Number of decimal places (default: 1)
        use_scale: Whether to use MM/B abbreviations

    Returns:
        Formatted string with SR prefix
    """
    if pd.isna(value):
        return "-"

    if not use_scale:
        return f"SR {value:,.{decimals}f}"

    abs_value = abs(value)
    if abs_value >= 1e9:
        # Billions
        scaled = value / 1e9
        return f"SR {scaled:,.{decimals}f}B"
    elif abs_value >= 1e6:
        # Millions - show as thousands with MM suffix
        scaled = value / 1e3  # Convert to thousands
        return f"SR {scaled:,.0f}MM"
    elif abs_value >= 1e3:
        # Thousands
        scaled = value / 1e3
        return f"SR {scaled:,.{decimals}f}K"
    else:
        return f"SR {value:,.{decimals}f}"


def format_percentage_value(value: float, decimals: int = 1) -> str:
    """
    Format a numeric value as a percentage.

    Args:
        value: The numeric value (0.538 = 53.8%)
        decimals: Number of decimal places (default: 1)

    Returns:
        Formatted percentage string (e.g., "53.8%")
    """
    if pd.isna(value):
        return "-"
    return f"{value * 100:.{decimals}f}%"


def format_ratio_value(value: float, decimals: int = 2) -> str:
    """
    Format a numeric value as a ratio.

    Args:
        value: The numeric value
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted ratio string (e.g., "1.77x")
    """
    if pd.isna(value):
        return "-"
    return f"{value:.{decimals}f}x"


# =============================================================================
# AG-Grid JavaScript Formatters
# =============================================================================

# SR Currency Formatter (for AG-Grid) - Full value with commas
SR_FORMATTER_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return '-';
    return 'SR ' + params.value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}
"""

# SR Currency Formatter with scale ('000) - MM for millions, B for billions
SR_ABBREVIATED_FORMATTER_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return '-';
    var value = params.value;
    var absValue = Math.abs(value);

    if (absValue >= 1e9) {
        // Billions
        value = value / 1e9;
        return 'SR ' + value.toLocaleString('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }) + 'B';
    } else if (absValue >= 1e6) {
        // Millions - show in thousands with MM suffix
        value = value / 1e3;
        return 'SR ' + value.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }) + 'MM';
    } else if (absValue >= 1e3) {
        // Thousands
        value = value / 1e3;
        return 'SR ' + value.toLocaleString('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }) + 'K';
    }
    return 'SR ' + value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}
"""

# Percentage Formatter (assumes value is decimal, e.g., 0.538 = 53.8%)
PERCENTAGE_FORMATTER_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return '-';
    return (params.value * 100).toFixed(1) + '%';
}
"""

# Ratio Formatter (for debt-to-equity, etc.) - e.g., 1.77x
RATIO_FORMATTER_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return '-';
    return params.value.toFixed(2) + 'x';
}
"""

# Number with commas formatter
NUMBER_FORMATTER_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return '-';
    return params.value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}
"""

# Legacy aliases for backwards compatibility
SAR_FORMATTER_JS = SR_FORMATTER_JS
SAR_ABBREVIATED_FORMATTER_JS = SR_ABBREVIATED_FORMATTER_JS

# Cell style for positive/negative values (green/red)
POSITIVE_NEGATIVE_STYLE_JS = """
function(params) {
    if (params.value == null || isNaN(params.value)) return {};
    if (params.value > 0) {
        return { color: '#10B981', fontWeight: 'bold' };
    } else if (params.value < 0) {
        return { color: '#EF4444', fontWeight: 'bold' };
    }
    return {};
}
"""


# =============================================================================
# Column Configuration
# =============================================================================

@dataclass
class ColumnConfig:
    """Configuration for a single grid column."""

    field: str
    header_name: str
    column_type: Literal["text", "currency", "currency_abbreviated", "percentage", "ratio", "number"] = "text"
    width: Optional[int] = None
    min_width: int = 100
    pinned: Optional[Literal["left", "right"]] = None
    sortable: bool = True
    filterable: bool = True
    resizable: bool = True
    editable: bool = False
    hide: bool = False
    cell_style_positive_negative: bool = False

    def to_column_def(self) -> Dict[str, Any]:
        """Convert to AG-Grid column definition."""
        col_def: Dict[str, Any] = {
            "field": self.field,
            "headerName": self.header_name,
            "sortable": self.sortable,
            "filter": self.filterable,
            "resizable": self.resizable,
            "editable": self.editable,
            "hide": self.hide,
            "minWidth": self.min_width,
        }

        if self.width:
            col_def["width"] = self.width

        if self.pinned:
            col_def["pinned"] = self.pinned

        # Apply formatters based on column type
        if AGGRID_AVAILABLE:
            if self.column_type == "currency":
                col_def["valueFormatter"] = JsCode(SAR_FORMATTER_JS)
                col_def["type"] = "numericColumn"
            elif self.column_type == "currency_abbreviated":
                col_def["valueFormatter"] = JsCode(SAR_ABBREVIATED_FORMATTER_JS)
                col_def["type"] = "numericColumn"
            elif self.column_type == "percentage":
                col_def["valueFormatter"] = JsCode(PERCENTAGE_FORMATTER_JS)
                col_def["type"] = "numericColumn"
            elif self.column_type == "ratio":
                col_def["valueFormatter"] = JsCode(RATIO_FORMATTER_JS)
                col_def["type"] = "numericColumn"
            elif self.column_type == "number":
                col_def["valueFormatter"] = JsCode(NUMBER_FORMATTER_JS)
                col_def["type"] = "numericColumn"

            if self.cell_style_positive_negative:
                col_def["cellStyle"] = JsCode(POSITIVE_NEGATIVE_STYLE_JS)

        return col_def


# =============================================================================
# Default Financial Column Configurations
# =============================================================================

DEFAULT_FINANCIAL_COLUMNS: List[ColumnConfig] = [
    ColumnConfig(
        field="company_name",
        header_name="Company",
        column_type="text",
        pinned="left",
        min_width=200,
        width=250,
    ),
    ColumnConfig(
        field="sector",
        header_name="Sector",
        column_type="text",
        min_width=120,
    ),
    ColumnConfig(
        field="industry",
        header_name="Industry",
        column_type="text",
        min_width=150,
    ),
    ColumnConfig(
        field="fiscal_year",
        header_name="Fiscal Year",
        column_type="number",
        min_width=100,
        width=110,
    ),
    ColumnConfig(
        field="revenue",
        header_name="Revenue (SAR)",
        column_type="currency_abbreviated",
        min_width=130,
    ),
    ColumnConfig(
        field="net_profit",
        header_name="Net Profit (SAR)",
        column_type="currency_abbreviated",
        cell_style_positive_negative=True,
        min_width=140,
    ),
    ColumnConfig(
        field="total_assets",
        header_name="Total Assets (SAR)",
        column_type="currency_abbreviated",
        min_width=150,
    ),
    ColumnConfig(
        field="ROE",
        header_name="ROE",
        column_type="percentage",
        cell_style_positive_negative=True,
        min_width=90,
    ),
    ColumnConfig(
        field="ROA",
        header_name="ROA",
        column_type="percentage",
        cell_style_positive_negative=True,
        min_width=90,
    ),
    ColumnConfig(
        field="debt_to_equity",
        header_name="D/E Ratio",
        column_type="ratio",
        min_width=100,
    ),
]


# =============================================================================
# Financial Grid Class
# =============================================================================

@dataclass
class GridTheme:
    """AG-Grid theme configuration."""

    name: Literal["streamlit", "alpine", "alpine-dark", "balham", "balham-dark", "material"] = "streamlit"
    row_height: int = 35
    header_height: int = 40


@dataclass
class GridOptions:
    """AG-Grid options configuration."""

    selection_mode: Literal["single", "multiple", "disabled"] = "multiple"
    enable_pagination: bool = True
    page_size: int = 25
    enable_sorting: bool = True
    enable_filtering: bool = True
    enable_excel_export: bool = True
    enable_csv_export: bool = True
    enable_column_resize: bool = True
    auto_size_columns: bool = False
    fit_columns_on_grid_load: bool = True
    theme: GridTheme = field(default_factory=GridTheme)


class FinancialGrid:
    """
    AG-Grid component for displaying Saudi financial data.

    Features:
    - SAR currency formatting with abbreviations
    - Percentage and ratio formatting
    - Column pinning (company name pinned left by default)
    - Excel/CSV export functionality
    - Single or multiple row selection
    - Positive/negative value coloring
    - Fallback to st.dataframe when AG-Grid not available

    Example:
        ```python
        import pandas as pd
        from components.tables import FinancialGrid

        df = pd.DataFrame({
            "company_name": ["Saudi Aramco", "SABIC"],
            "revenue": [1500000000000, 180000000000],
            "ROE": [0.25, 0.18],
        })

        grid = FinancialGrid(df)
        selected_rows = grid.render()
        ```
    """

    def __init__(
        self,
        data: pd.DataFrame,
        columns: Optional[List[ColumnConfig]] = None,
        options: Optional[GridOptions] = None,
        key: Optional[str] = None,
    ):
        """
        Initialize the Financial Grid.

        Args:
            data: DataFrame containing financial data
            columns: List of column configurations (auto-detected if None)
            options: Grid options for behavior and appearance
            key: Unique key for Streamlit component state
        """
        self.data = data.copy()
        self.columns = columns or self._auto_detect_columns()
        self.options = options or GridOptions()
        self.key = key or "financial_grid"

    def _auto_detect_columns(self) -> List[ColumnConfig]:
        """Auto-detect column configurations from DataFrame."""
        configs: List[ColumnConfig] = []

        # Map known column names to configurations
        column_map = {col.field: col for col in DEFAULT_FINANCIAL_COLUMNS}

        for col in self.data.columns:
            if col in column_map:
                configs.append(column_map[col])
            else:
                # Create default config based on dtype
                dtype = self.data[col].dtype
                col_type: Literal["text", "currency", "currency_abbreviated", "percentage", "ratio", "number"] = "text"

                if pd.api.types.is_numeric_dtype(dtype):
                    # Heuristic: if column name suggests percentage
                    if any(x in col.lower() for x in ["roe", "roa", "margin", "ratio", "rate", "percent", "pct"]):
                        col_type = "percentage"
                    elif any(x in col.lower() for x in ["debt", "leverage"]):
                        col_type = "ratio"
                    elif any(x in col.lower() for x in ["revenue", "profit", "asset", "equity", "income", "expense", "sar"]):
                        col_type = "currency_abbreviated"
                    else:
                        col_type = "number"

                configs.append(ColumnConfig(
                    field=col,
                    header_name=col.replace("_", " ").title(),
                    column_type=col_type,
                ))

        return configs

    def _build_grid_options(self) -> Any:
        """Build AG-Grid options using GridOptionsBuilder."""
        if not AGGRID_AVAILABLE:
            return None

        builder = GridOptionsBuilder.from_dataframe(self.data)

        # Apply column configurations
        for col_config in self.columns:
            if col_config.field in self.data.columns:
                col_def = col_config.to_column_def()
                # Remove 'field' to avoid duplicate argument error
                col_def.pop("field", None)
                builder.configure_column(col_config.field, **col_def)

        # Selection configuration
        if self.options.selection_mode != "disabled":
            builder.configure_selection(
                selection_mode=self.options.selection_mode,
                use_checkbox=True,
                header_checkbox=self.options.selection_mode == "multiple",
            )

        # Pagination
        if self.options.enable_pagination:
            builder.configure_pagination(
                enabled=True,
                paginationAutoPageSize=False,
                paginationPageSize=self.options.page_size,
            )

        # Sidebar with column visibility and filters
        builder.configure_side_bar(
            filters_panel=self.options.enable_filtering,
            columns_panel=True,
        )

        # Default column settings
        builder.configure_default_column(
            sortable=self.options.enable_sorting,
            filterable=self.options.enable_filtering,
            resizable=self.options.enable_column_resize,
        )

        # Grid options
        grid_options = builder.build()

        # Additional grid options
        grid_options["rowHeight"] = self.options.theme.row_height
        grid_options["headerHeight"] = self.options.theme.header_height

        if self.options.fit_columns_on_grid_load:
            grid_options["domLayout"] = "normal"

        return grid_options

    def _render_fallback(self) -> pd.DataFrame:
        """Render fallback using st.dataframe when AG-Grid not available."""
        st.warning("AG-Grid not available. Install with: `pip install streamlit-aggrid`")

        # Format the data for display
        display_df = self.data.copy()

        for col_config in self.columns:
            if col_config.field in display_df.columns:
                if col_config.column_type == "currency":
                    display_df[col_config.field] = display_df[col_config.field].apply(
                        lambda x: format_sar_value(x)
                    )
                elif col_config.column_type == "currency_abbreviated":
                    display_df[col_config.field] = display_df[col_config.field].apply(
                        lambda x: self._format_abbreviated(x)
                    )
                elif col_config.column_type == "percentage":
                    display_df[col_config.field] = display_df[col_config.field].apply(
                        lambda x: format_percentage_value(x)
                    )
                elif col_config.column_type == "ratio":
                    display_df[col_config.field] = display_df[col_config.field].apply(
                        lambda x: format_ratio_value(x)
                    )

        # Use Streamlit's native dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        return pd.DataFrame()  # No selection available in fallback

    def _format_abbreviated(self, value: float) -> str:
        """Format value with K/M/B abbreviations."""
        if pd.isna(value):
            return "-"

        abs_value = abs(value)
        if abs_value >= 1e9:
            return f"SAR {value / 1e9:.1f}B"
        elif abs_value >= 1e6:
            return f"SAR {value / 1e6:.1f}M"
        elif abs_value >= 1e3:
            return f"SAR {value / 1e3:.1f}K"
        else:
            return f"SAR {value:,.2f}"

    def render(self) -> pd.DataFrame:
        """
        Render the financial grid.

        Returns:
            DataFrame containing selected rows (empty if none selected)
        """
        if not AGGRID_AVAILABLE:
            return self._render_fallback()

        grid_options = self._build_grid_options()

        # Determine update mode based on selection
        update_mode = GridUpdateMode.SELECTION_CHANGED
        if self.options.selection_mode == "disabled":
            update_mode = GridUpdateMode.NO_UPDATE

        # Render the grid
        grid_response = AgGrid(
            self.data,
            gridOptions=grid_options,
            update_mode=update_mode,
            fit_columns_on_grid_load=self.options.fit_columns_on_grid_load,
            theme=self.options.theme.name,
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,  # Required for custom formatters
            key=self.key,
        )

        # Return selected rows
        selected_rows = grid_response.get("selected_rows", None)
        if selected_rows is not None and len(selected_rows) > 0:
            return pd.DataFrame(selected_rows)
        return pd.DataFrame()

    def export_to_excel(self, filename: str = "financial_data.xlsx") -> bytes:
        """
        Export grid data to Excel format.

        Args:
            filename: Name for the Excel file

        Returns:
            Bytes containing the Excel file
        """
        buffer = io.BytesIO()

        # Create formatted export
        export_df = self.data.copy()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Financial Data")

        return buffer.getvalue()

    def export_to_csv(self) -> str:
        """
        Export grid data to CSV format.

        Returns:
            CSV string
        """
        return self.data.to_csv(index=False)


# =============================================================================
# Convenience Function
# =============================================================================

def create_financial_grid(
    data: pd.DataFrame,
    columns: Optional[List[ColumnConfig]] = None,
    selection_mode: Literal["single", "multiple", "disabled"] = "multiple",
    enable_pagination: bool = True,
    page_size: int = 25,
    enable_export: bool = True,
    theme: str = "streamlit",
    key: Optional[str] = None,
) -> Tuple[pd.DataFrame, Optional[bytes]]:
    """
    Create and render a financial grid with common options.

    This is a convenience function that creates a FinancialGrid with
    commonly used options and handles the export buttons.

    Args:
        data: DataFrame containing financial data
        columns: Column configurations (auto-detected if None)
        selection_mode: Row selection mode
        enable_pagination: Enable pagination
        page_size: Rows per page
        enable_export: Show export buttons
        theme: Grid theme name
        key: Unique component key

    Returns:
        Tuple of (selected_rows_df, excel_bytes or None)

    Example:
        ```python
        selected, excel_data = create_financial_grid(df)
        if not selected.empty:
            st.write(f"Selected {len(selected)} companies")
        ```
    """
    options = GridOptions(
        selection_mode=selection_mode,
        enable_pagination=enable_pagination,
        page_size=page_size,
        enable_excel_export=enable_export,
        enable_csv_export=enable_export,
        theme=GridTheme(name=theme),
    )

    grid = FinancialGrid(
        data=data,
        columns=columns,
        options=options,
        key=key,
    )

    # Export buttons
    excel_bytes = None
    if enable_export and AGGRID_AVAILABLE:
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            excel_bytes = grid.export_to_excel()
            st.download_button(
                label="Export Excel",
                data=excel_bytes,
                file_name="financial_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key}_excel_export" if key else "excel_export",
            )
        with col2:
            csv_data = grid.export_to_csv()
            st.download_button(
                label="Export CSV",
                data=csv_data,
                file_name="financial_data.csv",
                mime="text/csv",
                key=f"{key}_csv_export" if key else "csv_export",
            )

    # Render grid
    selected_rows = grid.render()

    return selected_rows, excel_bytes
