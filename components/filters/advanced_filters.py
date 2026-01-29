"""Advanced filtering component for Ra'd AI."""

from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import streamlit as st
except ImportError:
    st = None


def get_available_sectors(df: "pd.DataFrame") -> List[str]:
    """Get unique sectors from dataframe.

    Args:
        df: DataFrame with sector column

    Returns:
        Sorted list of unique sectors
    """
    if "sector" in df.columns:
        return sorted(df["sector"].dropna().unique().tolist())
    return []


def get_year_range(df: "pd.DataFrame") -> Tuple[int, int]:
    """Get min/max years from dataframe.

    Args:
        df: DataFrame with fiscal_year column

    Returns:
        Tuple of (min_year, max_year)
    """
    if "fiscal_year" in df.columns:
        years = df["fiscal_year"].dropna()
        return int(years.min()), int(years.max())
    return (2020, 2024)


def get_available_companies(df: "pd.DataFrame") -> List[str]:
    """Get unique company names."""
    if "company_name" in df.columns:
        return sorted(df["company_name"].dropna().unique().tolist())
    return []


def apply_filters(df: "pd.DataFrame", filters: Dict[str, Any]) -> "pd.DataFrame":
    """Apply filters to dataframe.

    Args:
        df: DataFrame to filter
        filters: Dictionary of filter conditions

    Returns:
        Filtered DataFrame
    """
    if pd is None:
        raise ImportError("pandas required")

    result = df.copy()

    # Sector filter
    if filters.get("sectors"):
        result = result[result["sector"].isin(filters["sectors"])]

    # Year filter
    if filters.get("years") and "fiscal_year" in result.columns:
        min_year, max_year = filters["years"]
        result = result[
            (result["fiscal_year"] >= min_year) &
            (result["fiscal_year"] <= max_year)
        ]

    # Company filter
    if filters.get("companies"):
        result = result[result["company_name"].isin(filters["companies"])]

    return result


def render_advanced_filters(df: "pd.DataFrame") -> Dict[str, Any]:
    """Render advanced filter panel in sidebar.

    Args:
        df: DataFrame to get filter options from

    Returns:
        Dictionary of selected filter values
    """
    if st is None:
        raise RuntimeError("Streamlit required")

    filters = {}

    with st.expander("🔍 Advanced Filters", expanded=False):
        # Sector filter
        sectors = get_available_sectors(df)
        if sectors:
            selected_sectors = st.multiselect(
                "Sectors",
                options=sectors,
                default=None,
                help="Filter by company sector"
            )
            if selected_sectors:
                filters["sectors"] = selected_sectors

        # Year range filter
        if "fiscal_year" in df.columns:
            min_year, max_year = get_year_range(df)
            selected_years = st.slider(
                "Fiscal Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                help="Filter by fiscal year"
            )
            filters["years"] = selected_years

        # Company search
        companies = get_available_companies(df)
        if companies:
            selected_companies = st.multiselect(
                "Companies",
                options=companies,
                default=None,
                help="Filter by specific companies"
            )
            if selected_companies:
                filters["companies"] = selected_companies

        # Clear filters button
        if filters:
            if st.button("Clear Filters", key="clear_filters"):
                filters = {}
                st.rerun()

    return filters
