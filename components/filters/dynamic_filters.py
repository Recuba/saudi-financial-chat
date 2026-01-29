"""
Dynamic Multi-Select Filters
============================
Provides dynamic filtering capabilities using streamlit-dynamic-filters
with fallback to native Streamlit multiselect widgets.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import streamlit as st

# Import guard for optional dependency
try:
    from streamlit_dynamic_filters import DynamicFilters
    DYNAMIC_FILTERS_AVAILABLE = True
except ImportError:
    DYNAMIC_FILTERS_AVAILABLE = False


class DynamicFilterManager:
    """
    Manager class for dynamic filtering of DataFrames.

    Provides a unified interface for filtering data with automatic
    fallback to native Streamlit widgets when streamlit-dynamic-filters
    is not available.

    Attributes:
        df: The source DataFrame to filter
        filter_columns: List of column names to create filters for
        key_prefix: Prefix for session state keys to avoid conflicts
    """

    def __init__(
        self,
        df: pd.DataFrame,
        filter_columns: List[str],
        key_prefix: str = "filter"
    ):
        """
        Initialize the DynamicFilterManager.

        Args:
            df: DataFrame to filter
            filter_columns: List of column names to create filters for
            key_prefix: Prefix for session state keys (default: "filter")
        """
        self.df = df
        self.filter_columns = [col for col in filter_columns if col in df.columns]
        self.key_prefix = key_prefix
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state for filter values."""
        state_key = f"{self.key_prefix}_values"
        if state_key not in st.session_state:
            st.session_state[state_key] = {}

    def _get_filter_key(self, column: str) -> str:
        """Generate a unique session state key for a filter column."""
        return f"{self.key_prefix}_{column}"

    def render(
        self,
        location: str = "sidebar",
        use_container_width: bool = True
    ) -> pd.DataFrame:
        """
        Render filter widgets and return filtered DataFrame.

        Args:
            location: Where to render filters ("sidebar" or "columns")
            use_container_width: Whether filters should use full container width

        Returns:
            Filtered DataFrame based on selected filter values
        """
        if DYNAMIC_FILTERS_AVAILABLE and location == "sidebar":
            return self._render_with_dynamic_filters()
        else:
            return self._render_with_native_widgets(location, use_container_width)

    def _render_with_dynamic_filters(self) -> pd.DataFrame:
        """Render using streamlit-dynamic-filters package."""
        dynamic_filters = DynamicFilters(
            self.df,
            filters=self.filter_columns,
            filters_name=self.key_prefix
        )
        dynamic_filters.display_filters(location="sidebar")
        return dynamic_filters.filter_df()

    def _render_with_native_widgets(
        self,
        location: str,
        use_container_width: bool
    ) -> pd.DataFrame:
        """Render using native Streamlit multiselect widgets."""
        filtered_df = self.df.copy()
        state_key = f"{self.key_prefix}_values"

        # Determine container based on location
        if location == "sidebar":
            container = st.sidebar
        else:
            container = st

        # Render filters
        for column in self.filter_columns:
            filter_key = self._get_filter_key(column)

            # Get available options from currently filtered data
            available_options = sorted(filtered_df[column].dropna().unique().tolist())

            # Format column name for display
            display_name = column.replace("_", " ").title()

            selected = container.multiselect(
                label=display_name,
                options=available_options,
                default=st.session_state[state_key].get(column, []),
                key=filter_key,
                help=f"Select one or more {display_name.lower()} values"
            )

            # Store selection in session state
            st.session_state[state_key][column] = selected

            # Apply filter if selections made
            if selected:
                filtered_df = filtered_df[filtered_df[column].isin(selected)]

        return filtered_df

    def get_filter_summary(self) -> Dict[str, List[Any]]:
        """
        Get a summary of currently active filters.

        Returns:
            Dictionary mapping column names to selected values
        """
        state_key = f"{self.key_prefix}_values"
        if state_key not in st.session_state:
            return {}

        return {
            col: values
            for col, values in st.session_state[state_key].items()
            if values
        }

    def clear_filters(self) -> None:
        """Clear all filter selections."""
        state_key = f"{self.key_prefix}_values"
        st.session_state[state_key] = {}

        # Also clear individual filter keys
        for column in self.filter_columns:
            filter_key = self._get_filter_key(column)
            if filter_key in st.session_state:
                del st.session_state[filter_key]


def extract_filter_options(
    df: pd.DataFrame,
    columns: List[str],
    sort: bool = True,
    include_counts: bool = False
) -> Dict[str, List[Any]]:
    """
    Extract unique filter options from DataFrame columns.

    Args:
        df: Source DataFrame
        columns: List of column names to extract options from
        sort: Whether to sort options alphabetically (default: True)
        include_counts: Whether to include value counts (default: False)

    Returns:
        Dictionary mapping column names to list of unique values
        or list of (value, count) tuples if include_counts is True
    """
    options = {}

    for col in columns:
        if col not in df.columns:
            continue

        if include_counts:
            counts = df[col].value_counts().sort_index() if sort else df[col].value_counts()
            options[col] = [(val, cnt) for val, cnt in counts.items()]
        else:
            unique_vals = df[col].dropna().unique().tolist()
            options[col] = sorted(unique_vals) if sort else unique_vals

    return options


def apply_filters(
    df: pd.DataFrame,
    filters: Dict[str, Union[List[Any], Any]]
) -> pd.DataFrame:
    """
    Apply filter conditions to a DataFrame.

    Args:
        df: DataFrame to filter
        filters: Dictionary mapping column names to filter values
                 Values can be single values or lists for multi-select

    Returns:
        Filtered DataFrame

    Example:
        >>> filtered = apply_filters(df, {
        ...     "sector": ["Banking", "Retail"],
        ...     "fiscal_year": 2024
        ... })
    """
    result = df.copy()

    for column, values in filters.items():
        if column not in result.columns:
            continue

        if values is None or (isinstance(values, list) and len(values) == 0):
            continue

        if isinstance(values, list):
            result = result[result[column].isin(values)]
        else:
            result = result[result[column] == values]

    return result


def render_filter_summary(
    filters: Dict[str, List[Any]],
    container: Optional[Any] = None
) -> None:
    """
    Render a visual summary of active filters.

    Args:
        filters: Dictionary mapping column names to selected values
        container: Streamlit container to render in (default: main area)
    """
    if container is None:
        container = st

    if not filters:
        container.info("No filters applied")
        return

    # Count total active filters
    total_filters = sum(len(v) for v in filters.values())

    container.markdown(f"**Active Filters:** {total_filters}")

    # Display each filter as pills/tags
    filter_html_parts = []
    for column, values in filters.items():
        if not values:
            continue

        col_display = column.replace("_", " ").title()

        for val in values:
            filter_html_parts.append(
                f'<span style="'
                f'background: linear-gradient(135deg, #B8860B 0%, #D4A84B 100%);'
                f'color: #0E0E0E;'
                f'padding: 4px 12px;'
                f'border-radius: 16px;'
                f'margin: 2px;'
                f'display: inline-block;'
                f'font-size: 0.85rem;'
                f'font-weight: 500;'
                f'">{col_display}: {val}</span>'
            )

    if filter_html_parts:
        container.markdown(
            f'<div style="display: flex; flex-wrap: wrap; gap: 4px;">'
            f'{"".join(filter_html_parts)}'
            f'</div>',
            unsafe_allow_html=True
        )


def render_dynamic_filters(
    df: pd.DataFrame,
    filter_columns: List[str],
    key_prefix: str = "dyn_filter",
    location: str = "sidebar",
    show_summary: bool = True,
    summary_container: Optional[Any] = None
) -> Tuple[pd.DataFrame, Dict[str, List[Any]]]:
    """
    Convenience function to render dynamic filters and return filtered data.

    Args:
        df: DataFrame to filter
        filter_columns: List of column names to create filters for
        key_prefix: Prefix for session state keys
        location: Where to render filters ("sidebar" or "columns")
        show_summary: Whether to show filter summary
        summary_container: Container for summary (default: main area)

    Returns:
        Tuple of (filtered DataFrame, active filters dictionary)

    Example:
        >>> filtered_df, active_filters = render_dynamic_filters(
        ...     df=analytics_df,
        ...     filter_columns=["sector", "industry", "fiscal_year"],
        ...     location="sidebar"
        ... )
    """
    manager = DynamicFilterManager(df, filter_columns, key_prefix)
    filtered_df = manager.render(location=location)
    active_filters = manager.get_filter_summary()

    if show_summary and active_filters:
        render_filter_summary(active_filters, summary_container)

    return filtered_df, active_filters


def clear_all_filters(key_prefix: str = "dyn_filter") -> None:
    """
    Clear all filters with the given prefix.

    Args:
        key_prefix: The prefix used when creating filters
    """
    state_key = f"{key_prefix}_values"
    if state_key in st.session_state:
        st.session_state[state_key] = {}

    # Find and clear all related session state keys
    keys_to_remove = [
        key for key in st.session_state.keys()
        if key.startswith(f"{key_prefix}_")
    ]

    for key in keys_to_remove:
        del st.session_state[key]


def render_filter_controls(
    key_prefix: str = "dyn_filter",
    container: Optional[Any] = None
) -> bool:
    """
    Render filter control buttons (clear all, etc.).

    Args:
        key_prefix: The prefix used when creating filters
        container: Container to render controls in

    Returns:
        True if clear button was clicked
    """
    if container is None:
        container = st

    col1, col2 = container.columns([3, 1])

    with col2:
        if st.button("Clear All", key=f"{key_prefix}_clear_btn", type="secondary"):
            clear_all_filters(key_prefix)
            st.rerun()
            return True

    return False
