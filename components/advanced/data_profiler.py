"""
Data Profiler Component.

Provides data profiling capabilities using ydata-profiling.
Falls back to basic statistics when ydata-profiling is not available.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import io
import base64

# Check if ydata-profiling is available
try:
    from ydata_profiling import ProfileReport
    YDATA_PROFILING_AVAILABLE = True
except ImportError:
    try:
        # Try older pandas-profiling name
        from pandas_profiling import ProfileReport
        YDATA_PROFILING_AVAILABLE = True
    except ImportError:
        YDATA_PROFILING_AVAILABLE = False
        ProfileReport = None


def get_quick_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get quick statistics about the DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with basic statistics
    """
    if df is None or df.empty:
        return {
            "rows": 0,
            "columns": 0,
            "memory_mb": 0,
            "data_types": {},
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
        }

    # Memory usage
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 * 1024)

    # Data types breakdown
    dtype_counts = df.dtypes.value_counts().to_dict()
    dtype_counts = {str(k): int(v) for k, v in dtype_counts.items()}

    # Column categorization
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64', 'datetimetz']).columns.tolist()
    bool_cols = df.select_dtypes(include=['bool']).columns.tolist()

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "memory_mb": round(memory_mb, 2),
        "memory_bytes": memory_bytes,
        "data_types": dtype_counts,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "boolean_columns": bool_cols,
        "total_cells": len(df) * len(df.columns),
    }


def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check data quality metrics.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary with data quality metrics
    """
    if df is None or df.empty:
        return {
            "missing_values": {},
            "missing_percentage": {},
            "total_missing": 0,
            "total_missing_percentage": 0,
            "duplicate_rows": 0,
            "duplicate_percentage": 0,
            "columns_with_missing": [],
            "complete_columns": [],
        }

    # Missing values analysis
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df) * 100).round(2)

    missing_dict = missing_counts.to_dict()
    missing_pct_dict = missing_percentages.to_dict()

    # Columns with/without missing values
    cols_with_missing = [col for col, count in missing_dict.items() if count > 0]
    complete_cols = [col for col, count in missing_dict.items() if count == 0]

    # Total missing
    total_missing = missing_counts.sum()
    total_cells = len(df) * len(df.columns)
    total_missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0

    # Duplicate rows
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / len(df) * 100) if len(df) > 0 else 0

    # Constant columns (single unique value)
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]

    # High cardinality columns (many unique values)
    high_cardinality_cols = []
    for col in df.select_dtypes(include=['object', 'string', 'category']).columns:
        cardinality = df[col].nunique()
        if cardinality > len(df) * 0.5:  # More than 50% unique
            high_cardinality_cols.append((col, cardinality))

    return {
        "missing_values": missing_dict,
        "missing_percentage": missing_pct_dict,
        "total_missing": int(total_missing),
        "total_missing_percentage": round(total_missing_pct, 2),
        "duplicate_rows": int(duplicate_count),
        "duplicate_percentage": round(duplicate_pct, 2),
        "columns_with_missing": cols_with_missing,
        "complete_columns": complete_cols,
        "constant_columns": constant_cols,
        "high_cardinality_columns": high_cardinality_cols,
    }


def _get_column_profile(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Get detailed profile for a single column."""
    col_data = df[column]
    dtype = str(col_data.dtype)

    profile = {
        "name": column,
        "dtype": dtype,
        "count": len(col_data),
        "missing": col_data.isnull().sum(),
        "missing_pct": round(col_data.isnull().sum() / len(col_data) * 100, 2) if len(col_data) > 0 else 0,
        "unique": col_data.nunique(),
        "unique_pct": round(col_data.nunique() / len(col_data) * 100, 2) if len(col_data) > 0 else 0,
    }

    # Numeric columns
    if pd.api.types.is_numeric_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            profile.update({
                "min": float(non_null.min()),
                "max": float(non_null.max()),
                "mean": float(non_null.mean()),
                "median": float(non_null.median()),
                "std": float(non_null.std()) if len(non_null) > 1 else 0,
                "zeros": int((non_null == 0).sum()),
                "negative": int((non_null < 0).sum()),
            })

    # Categorical/string columns
    elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data) or col_data.dtype == 'object':
        non_null = col_data.dropna()
        if len(non_null) > 0:
            value_counts = non_null.value_counts()
            profile.update({
                "top_values": value_counts.head(5).to_dict(),
                "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                "most_common_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            })

            # String-specific stats
            if col_data.dtype == 'object':
                try:
                    str_lengths = non_null.astype(str).str.len()
                    profile.update({
                        "min_length": int(str_lengths.min()),
                        "max_length": int(str_lengths.max()),
                        "avg_length": round(str_lengths.mean(), 2),
                    })
                except Exception:
                    pass

    # Datetime columns
    elif pd.api.types.is_datetime64_any_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            profile.update({
                "min_date": str(non_null.min()),
                "max_date": str(non_null.max()),
                "date_range_days": (non_null.max() - non_null.min()).days,
            })

    return profile


def get_quick_profile_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Get a quick profile summary for all columns.

    Args:
        df: Input DataFrame

    Returns:
        List of column profiles
    """
    if df is None or df.empty:
        return []

    profiles = []
    for col in df.columns:
        try:
            profile = _get_column_profile(df, col)
            profiles.append(profile)
        except Exception as e:
            profiles.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "error": str(e)
            })

    return profiles


def generate_profile_report(
    df: pd.DataFrame,
    title: str = "Data Profile Report",
    minimal: bool = True,
    explorative: bool = False,
    dark_mode: bool = False,
    **kwargs
) -> Optional[Any]:
    """
    Generate a full ydata-profiling report.

    Args:
        df: Input DataFrame
        title: Report title
        minimal: Use minimal mode (faster, less detailed)
        explorative: Use explorative mode (slower, more detailed)
        dark_mode: Use dark theme
        **kwargs: Additional arguments for ProfileReport

    Returns:
        ProfileReport object or None if not available
    """
    if not YDATA_PROFILING_AVAILABLE:
        return None

    if df is None or df.empty:
        return None

    try:
        report = ProfileReport(
            df,
            title=title,
            minimal=minimal,
            explorative=explorative,
            dark_mode=dark_mode,
            **kwargs
        )
        return report
    except Exception as e:
        st.error(f"Error generating profile report: {str(e)}")
        return None


def _render_quick_stats_panel(stats: Dict[str, Any]) -> None:
    """Render the quick stats panel."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rows", f"{stats['rows']:,}")
    with col2:
        st.metric("Columns", stats['columns'])
    with col3:
        st.metric("Memory", f"{stats['memory_mb']:.2f} MB")
    with col4:
        st.metric("Total Cells", f"{stats['total_cells']:,}")

    # Data types breakdown
    with st.expander("Data Types Breakdown", expanded=False):
        if stats['data_types']:
            dtype_df = pd.DataFrame([
                {"Type": k, "Count": v}
                for k, v in stats['data_types'].items()
            ])
            st.dataframe(dtype_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Numeric columns:** {len(stats['numeric_columns'])}")
            if stats['numeric_columns']:
                st.write(", ".join(stats['numeric_columns'][:10]))
                if len(stats['numeric_columns']) > 10:
                    st.write(f"... and {len(stats['numeric_columns']) - 10} more")

        with col2:
            st.write(f"**Categorical columns:** {len(stats['categorical_columns'])}")
            if stats['categorical_columns']:
                st.write(", ".join(stats['categorical_columns'][:10]))
                if len(stats['categorical_columns']) > 10:
                    st.write(f"... and {len(stats['categorical_columns']) - 10} more")


def _render_data_quality_panel(quality: Dict[str, Any]) -> None:
    """Render the data quality panel."""
    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        color = "inverse" if quality['total_missing_percentage'] > 10 else "normal"
        st.metric(
            "Missing Values",
            f"{quality['total_missing']:,}",
            f"{quality['total_missing_percentage']:.1f}%"
        )

    with col2:
        st.metric(
            "Duplicate Rows",
            f"{quality['duplicate_rows']:,}",
            f"{quality['duplicate_percentage']:.1f}%"
        )

    with col3:
        st.metric(
            "Complete Columns",
            len(quality['complete_columns']),
            f"of {len(quality['complete_columns']) + len(quality['columns_with_missing'])}"
        )

    # Missing values details
    if quality['columns_with_missing']:
        with st.expander(f"Columns with Missing Values ({len(quality['columns_with_missing'])})", expanded=False):
            missing_df = pd.DataFrame([
                {
                    "Column": col,
                    "Missing": quality['missing_values'][col],
                    "Percentage": f"{quality['missing_percentage'][col]:.1f}%"
                }
                for col in quality['columns_with_missing']
            ]).sort_values("Missing", ascending=False)

            st.dataframe(missing_df, use_container_width=True, hide_index=True)

    # Constant columns warning
    if quality['constant_columns']:
        st.warning(f"**Constant columns detected:** {', '.join(quality['constant_columns'])}")

    # High cardinality warning
    if quality['high_cardinality_columns']:
        with st.expander("High Cardinality Columns", expanded=False):
            st.info("These columns have many unique values (>50% of rows)")
            for col, cardinality in quality['high_cardinality_columns']:
                st.write(f"- **{col}**: {cardinality:,} unique values")


def _render_column_profiles(profiles: List[Dict[str, Any]]) -> None:
    """Render column profile summaries."""
    if not profiles:
        return

    # Create summary dataframe
    summary_data = []
    for p in profiles:
        row = {
            "Column": p.get("name", ""),
            "Type": p.get("dtype", ""),
            "Missing %": f"{p.get('missing_pct', 0):.1f}%",
            "Unique": p.get("unique", 0),
        }

        # Add type-specific summary
        if "mean" in p:
            row["Summary"] = f"Mean: {p['mean']:.2f}, Range: [{p['min']:.2f}, {p['max']:.2f}]"
        elif "most_common" in p and p["most_common"]:
            row["Summary"] = f"Top: {p['most_common'][:30]}{'...' if len(str(p['most_common'])) > 30 else ''}"
        elif "min_date" in p:
            row["Summary"] = f"{p['min_date'][:10]} to {p['max_date'][:10]}"
        else:
            row["Summary"] = "-"

        summary_data.append(row)

    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_fallback_profiler(df: pd.DataFrame, key: str) -> None:
    """Render fallback profiler when ydata-profiling is not available."""
    st.warning(
        "ydata-profiling is not installed. Using basic profiler. "
        "Install with: `pip install ydata-profiling`"
    )

    # Quick stats
    st.subheader("Quick Statistics")
    stats = get_quick_stats(df)
    _render_quick_stats_panel(stats)

    # Data quality
    st.subheader("Data Quality")
    quality = check_data_quality(df)
    _render_data_quality_panel(quality)

    # Column profiles
    st.subheader("Column Profiles")
    profiles = get_quick_profile_summary(df)
    _render_column_profiles(profiles)

    # Numeric statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        with st.expander("Numeric Column Statistics", expanded=False):
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)


def render_data_profiler(
    df: pd.DataFrame,
    key: str = "data_profiler",
    show_quick_stats: bool = True,
    show_quality_check: bool = True,
    show_full_report: bool = True,
    minimal_report: bool = True,
    dark_mode: bool = False,
) -> None:
    """
    Render the complete data profiler component.

    Args:
        df: DataFrame to profile
        key: Unique key for the component
        show_quick_stats: Show quick statistics panel
        show_quality_check: Show data quality check panel
        show_full_report: Show option for full ydata-profiling report
        minimal_report: Use minimal mode for full report (faster)
        dark_mode: Use dark theme for report
    """
    if df is None or df.empty:
        st.info("No data available for profiling.")
        return

    # Quick Stats
    if show_quick_stats:
        st.subheader("Quick Statistics")
        stats = get_quick_stats(df)
        _render_quick_stats_panel(stats)

    # Data Quality
    if show_quality_check:
        st.subheader("Data Quality Check")
        quality = check_data_quality(df)
        _render_data_quality_panel(quality)

    # Quick Profile Summary
    st.subheader("Column Summary")
    profiles = get_quick_profile_summary(df)
    _render_column_profiles(profiles)

    # Full Report (ydata-profiling)
    if show_full_report:
        st.subheader("Full Profile Report")

        if not YDATA_PROFILING_AVAILABLE:
            st.info(
                "Full profiling requires ydata-profiling. "
                "Install with: `pip install ydata-profiling`"
            )
            return

        # Report options
        col1, col2 = st.columns([3, 1])

        with col1:
            report_type = st.radio(
                "Report type",
                options=["Minimal (Fast)", "Explorative (Detailed)"],
                horizontal=True,
                key=f"{key}_report_type"
            )

        with col2:
            generate_btn = st.button("Generate Report", key=f"{key}_generate")

        if generate_btn:
            is_minimal = report_type == "Minimal (Fast)"
            is_explorative = report_type == "Explorative (Detailed)"

            with st.spinner("Generating profile report... This may take a moment."):
                # Limit data for large datasets
                if len(df) > 10000:
                    st.info(f"Sampling 10,000 rows from {len(df):,} for performance.")
                    sample_df = df.sample(n=10000, random_state=42)
                else:
                    sample_df = df

                report = generate_profile_report(
                    sample_df,
                    title="Data Profile Report",
                    minimal=is_minimal,
                    explorative=is_explorative,
                    dark_mode=dark_mode
                )

                if report is not None:
                    # Store in session state
                    st.session_state[f"{key}_report"] = report
                    st.success("Report generated successfully!")

        # Display report if available
        if f"{key}_report" in st.session_state:
            report = st.session_state[f"{key}_report"]

            tab1, tab2 = st.tabs(["View Report", "Download"])

            with tab1:
                try:
                    # Render HTML report in Streamlit
                    report_html = report.to_html()
                    st.components.v1.html(report_html, height=800, scrolling=True)
                except Exception as e:
                    st.error(f"Error displaying report: {str(e)}")
                    st.info("Try downloading the report instead.")

            with tab2:
                try:
                    # Generate downloadable HTML
                    html_content = report.to_html()
                    b64 = base64.b64encode(html_content.encode()).decode()

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"data_profile_{timestamp}.html"

                    st.download_button(
                        label="Download HTML Report",
                        data=html_content,
                        file_name=filename,
                        mime="text/html",
                        key=f"{key}_download"
                    )
                except Exception as e:
                    st.error(f"Error preparing download: {str(e)}")
