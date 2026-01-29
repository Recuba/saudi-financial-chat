"""Data preview component for Ra'd AI."""

from typing import List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import streamlit as st
except ImportError:
    st = None


# Columns to prioritize in preview
KEY_COLUMNS = [
    "company_name",
    "symbol",
    "sector",
    "fiscal_year",
    "period_end",
    "revenue",
    "net_profit",
    "total_assets",
    "metric",
    "value",
    "ratio",
]


def get_preview_columns(df: "pd.DataFrame", max_cols: int = 6) -> List[str]:
    """Get columns to show in preview, prioritizing key columns."""
    if pd is None:
        return []

    all_cols = df.columns.tolist()

    # Start with key columns that exist in df
    preview_cols = [c for c in KEY_COLUMNS if c in all_cols]

    # Add remaining columns up to max
    for col in all_cols:
        if col not in preview_cols and len(preview_cols) < max_cols:
            preview_cols.append(col)

    return preview_cols[:max_cols]


def format_preview_dataframe(
    df: "pd.DataFrame",
    max_rows: int = 5,
    max_cols: int = 6
) -> "pd.DataFrame":
    """Format dataframe for preview display."""
    if pd is None:
        raise ImportError("pandas required")

    preview_cols = get_preview_columns(df, max_cols)
    return df[preview_cols].head(max_rows)


def render_data_preview(
    df: "pd.DataFrame",
    title: str = "Data Preview",
    expanded: bool = True,
    max_rows: int = 5,
    show_download: bool = True
) -> None:
    """Render an interactive data preview."""
    if st is None:
        raise RuntimeError("Streamlit is required to render data preview")

    total_rows = len(df)
    total_cols = len(df.columns)

    with st.expander(f"{title} ({total_rows:,} rows, {total_cols} cols)", expanded=expanded):
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{total_rows:,}")
        with col2:
            st.metric("Columns", total_cols)
        with col3:
            if "company_name" in df.columns:
                st.metric("Companies", df["company_name"].nunique())

        # Preview table
        preview_df = format_preview_dataframe(df, max_rows=max_rows)
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

        # Show more / column info
        if total_rows > max_rows:
            st.caption(f"Showing {max_rows} of {total_rows:,} rows")

        # Download button
        if show_download:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="data_preview.csv",
                mime="text/csv",
                key="preview_download"
            )
