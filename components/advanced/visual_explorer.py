"""
PyGWalker Visual Explorer Component.

Provides interactive visual data exploration using PyGWalker.
Falls back to a basic column selector + dataframe view if PyGWalker is not installed.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Any, Dict
from datetime import datetime
import hashlib

# Check if PyGWalker is available
try:
    import pygwalker as pyg
    from pygwalker.api.streamlit import StreamlitRenderer
    PYGWALKER_AVAILABLE = True
except ImportError:
    PYGWALKER_AVAILABLE = False
    pyg = None
    StreamlitRenderer = None


def prepare_data_for_explorer(
    df: pd.DataFrame,
    max_rows: int = 50000,
    datetime_to_string: bool = True,
    sample_method: str = "head"
) -> pd.DataFrame:
    """
    Prepare DataFrame for PyGWalker explorer.

    Args:
        df: Input DataFrame to prepare
        max_rows: Maximum number of rows to include (for performance)
        datetime_to_string: Convert datetime columns to strings for compatibility
        sample_method: How to sample if exceeding max_rows ('head', 'tail', 'random')

    Returns:
        Prepared DataFrame ready for visualization
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Create a copy to avoid modifying original
    prepared_df = df.copy()

    # Limit rows for performance
    if len(prepared_df) > max_rows:
        if sample_method == "head":
            prepared_df = prepared_df.head(max_rows)
        elif sample_method == "tail":
            prepared_df = prepared_df.tail(max_rows)
        elif sample_method == "random":
            prepared_df = prepared_df.sample(n=max_rows, random_state=42)

        st.info(f"Data limited to {max_rows:,} rows for performance. Original: {len(df):,} rows.")

    # Convert datetime columns to strings for PyGWalker compatibility
    if datetime_to_string:
        datetime_cols = prepared_df.select_dtypes(include=['datetime64', 'datetimetz']).columns
        for col in datetime_cols:
            prepared_df[col] = prepared_df[col].astype(str)

    # Handle problematic data types
    for col in prepared_df.columns:
        # Convert timedelta to string
        if pd.api.types.is_timedelta64_dtype(prepared_df[col]):
            prepared_df[col] = prepared_df[col].astype(str)

        # Convert complex objects to string
        if prepared_df[col].dtype == 'object':
            try:
                # Check if column contains non-string objects
                sample = prepared_df[col].dropna().head(10)
                if len(sample) > 0 and not all(isinstance(x, (str, int, float, bool, type(None))) for x in sample):
                    prepared_df[col] = prepared_df[col].astype(str)
            except Exception:
                prepared_df[col] = prepared_df[col].astype(str)

    return prepared_df


def _get_data_hash(df: pd.DataFrame) -> str:
    """Generate a hash for the DataFrame to use as cache key."""
    try:
        # Use shape and column names for quick hash
        hash_str = f"{df.shape}_{list(df.columns)}_{df.index[0] if len(df) > 0 else 'empty'}"
        return hashlib.md5(hash_str.encode()).hexdigest()[:16]
    except Exception:
        return str(id(df))


@st.cache_resource
def _get_cached_renderer(data_hash: str, spec: Optional[str] = None) -> Any:
    """
    Get a cached PyGWalker renderer instance.

    This is cached to avoid recreating the renderer on every rerun.
    The data_hash ensures we recreate when data changes.
    """
    # This function body is just for the cache key
    # Actual renderer creation happens in render_visual_explorer
    return None


def _render_fallback_explorer(df: pd.DataFrame, key: str = "fallback_explorer") -> None:
    """
    Render a basic fallback explorer when PyGWalker is not available.

    Provides column selection and basic visualization options.
    """
    st.warning("PyGWalker is not installed. Using basic data explorer. Install with: `pip install pygwalker`")

    if df is None or df.empty:
        st.info("No data available to explore.")
        return

    # Column selector
    st.subheader("Column Selector")

    all_columns = list(df.columns)

    # Categorize columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64', 'datetimetz']).columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Column Types:**")
        st.write(f"- Numeric: {len(numeric_cols)}")
        st.write(f"- Text: {len(text_cols)}")
        st.write(f"- Date: {len(date_cols)}")

    with col2:
        st.write("**Data Shape:**")
        st.write(f"- Rows: {len(df):,}")
        st.write(f"- Columns: {len(df.columns)}")

    # Column selection
    selected_columns = st.multiselect(
        "Select columns to display",
        options=all_columns,
        default=all_columns[:min(10, len(all_columns))],
        key=f"{key}_columns"
    )

    if not selected_columns:
        st.info("Please select at least one column.")
        return

    # Display options
    col1, col2, col3 = st.columns(3)

    with col1:
        max_rows_display = st.number_input(
            "Max rows to display",
            min_value=10,
            max_value=10000,
            value=100,
            step=50,
            key=f"{key}_max_rows"
        )

    with col2:
        sort_column = st.selectbox(
            "Sort by column",
            options=["(None)"] + selected_columns,
            key=f"{key}_sort"
        )

    with col3:
        if sort_column != "(None)":
            sort_ascending = st.checkbox("Ascending", value=True, key=f"{key}_asc")
        else:
            sort_ascending = True

    # Filter data
    display_df = df[selected_columns].copy()

    if sort_column != "(None)":
        display_df = display_df.sort_values(by=sort_column, ascending=sort_ascending)

    display_df = display_df.head(max_rows_display)

    # Display dataframe
    st.subheader("Data View")
    st.dataframe(display_df, use_container_width=True)

    # Basic statistics for numeric columns
    numeric_selected = [c for c in selected_columns if c in numeric_cols]
    if numeric_selected:
        with st.expander("Numeric Column Statistics", expanded=False):
            st.dataframe(df[numeric_selected].describe(), use_container_width=True)

    # Simple chart option
    if numeric_selected and len(display_df) <= 1000:
        with st.expander("Quick Chart", expanded=False):
            chart_type = st.selectbox(
                "Chart type",
                options=["Line", "Bar", "Area"],
                key=f"{key}_chart_type"
            )

            y_column = st.selectbox(
                "Y-axis column",
                options=numeric_selected,
                key=f"{key}_y_col"
            )

            if chart_type == "Line":
                st.line_chart(display_df[y_column])
            elif chart_type == "Bar":
                st.bar_chart(display_df[y_column])
            elif chart_type == "Area":
                st.area_chart(display_df[y_column])


def render_visual_explorer(
    df: pd.DataFrame,
    key: str = "visual_explorer",
    spec: Optional[str] = None,
    dark_mode: bool = False,
    max_rows: int = 50000,
    show_toolbar: bool = True,
    **kwargs
) -> None:
    """
    Render the PyGWalker visual explorer component.

    Args:
        df: DataFrame to explore
        key: Unique key for the component
        spec: Optional PyGWalker spec JSON for saved configurations
        dark_mode: Whether to use dark mode theme
        max_rows: Maximum rows to include (for performance)
        show_toolbar: Whether to show the PyGWalker toolbar
        **kwargs: Additional arguments passed to PyGWalker

    Returns:
        None (renders directly to Streamlit)
    """
    if df is None or df.empty:
        st.info("No data available for visual exploration.")
        return

    # Prepare data
    prepared_df = prepare_data_for_explorer(df, max_rows=max_rows)

    if not PYGWALKER_AVAILABLE:
        _render_fallback_explorer(prepared_df, key=key)
        return

    try:
        # Configure appearance
        appearance = "dark" if dark_mode else "light"

        # Create PyGWalker renderer
        # Using StreamlitRenderer for better Streamlit integration
        if StreamlitRenderer is not None:
            renderer = StreamlitRenderer(
                prepared_df,
                spec=spec,
                appearance=appearance,
                kernel_computation=True,
                **kwargs
            )

            # Render the explorer
            renderer.explorer()
        else:
            # Fallback to basic pyg.walk if StreamlitRenderer not available
            pyg.walk(
                prepared_df,
                spec=spec,
                dark=dark_mode == "dark",
                **kwargs
            )

    except Exception as e:
        st.error(f"Error rendering visual explorer: {str(e)}")
        st.info("Falling back to basic explorer...")
        _render_fallback_explorer(prepared_df, key=key)


def get_explorer_config(
    title: str = "Data Explorer",
    default_fields: Optional[List[str]] = None,
    hide_data_source: bool = False
) -> Dict[str, Any]:
    """
    Get configuration options for the visual explorer.

    Args:
        title: Title for the explorer
        default_fields: List of default fields to show
        hide_data_source: Whether to hide the data source panel

    Returns:
        Configuration dictionary for PyGWalker
    """
    config = {
        "title": title,
        "hideDataSourceConfig": hide_data_source,
    }

    if default_fields:
        config["defaultFields"] = default_fields

    return config


# Convenience function for quick exploration
def quick_explore(df: pd.DataFrame, title: str = "Quick Explorer") -> None:
    """
    Quick exploration of a DataFrame with minimal configuration.

    Args:
        df: DataFrame to explore
        title: Title for the explorer section
    """
    st.subheader(title)
    render_visual_explorer(
        df,
        key=f"quick_{title.lower().replace(' ', '_')}",
        max_rows=10000,
        show_toolbar=True
    )
