"""Sidebar component for Ra'd AI.

Provides database info, dataset selection, model selection, and column reference.
Enhanced with data context, company search, and freshness indicators.
"""

import os
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from utils.data_loader import (
    load_data,
    get_dataset_info,
    get_column_info,
    get_data_path,
    DATASET_DISPLAY_NAMES
)
from utils.llm_config import (
    get_llm_config_status,
    get_api_key,
    get_model_options,
    get_selected_model,
    set_selected_model,
    DEFAULT_MODEL,
)


def get_data_freshness() -> Dict[str, Any]:
    """Get data freshness information from parquet file timestamps.

    Returns:
        Dictionary with last_updated timestamp and freshness status
    """
    data_path = get_data_path()
    parquet_files = list(data_path.glob("*.parquet"))

    if not parquet_files:
        return {"last_updated": None, "status": "unknown", "days_old": None}

    # Get most recent modification time
    latest_mtime = max(os.path.getmtime(f) for f in parquet_files)
    last_updated = datetime.fromtimestamp(latest_mtime)

    days_old = (datetime.now() - last_updated).days

    if days_old <= 7:
        status = "fresh"
    elif days_old <= 30:
        status = "recent"
    else:
        status = "stale"

    return {
        "last_updated": last_updated,
        "status": status,
        "days_old": days_old
    }


def get_extended_dataset_info() -> Dict[str, Any]:
    """Get extended dataset information including sectors and years.

    Returns:
        Dictionary with comprehensive dataset statistics
    """
    data = load_data()
    analytics = data.get("analytics")

    info = get_dataset_info()

    # Extend with sector and year information
    if analytics is not None:
        if 'sector' in analytics.columns:
            info['sectors'] = analytics['sector'].nunique()
            info['sector_list'] = sorted(analytics['sector'].dropna().unique().tolist())
        else:
            info['sectors'] = 0
            info['sector_list'] = []

        if 'fiscal_year' in analytics.columns:
            years = analytics['fiscal_year'].dropna().unique()
            info['year_min'] = int(min(years)) if len(years) > 0 else None
            info['year_max'] = int(max(years)) if len(years) > 0 else None
            info['year_count'] = len(years)
        else:
            info['year_min'] = None
            info['year_max'] = None
            info['year_count'] = 0

        if 'currency' in analytics.columns:
            info['currencies'] = analytics['currency'].nunique()
        else:
            info['currencies'] = 1

        info['total_records'] = len(analytics)
    else:
        info['sectors'] = 0
        info['sector_list'] = []
        info['year_min'] = None
        info['year_max'] = None
        info['year_count'] = 0
        info['currencies'] = 1
        info['total_records'] = 0

    return info


def render_database_info() -> None:
    """Render the enhanced database information section with context."""
    st.header("Database Info")

    info = get_extended_dataset_info()
    freshness = get_data_freshness()

    # Primary metrics row
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Companies",
            value=f"{info['companies']:,}",
            help="Unique companies in the database"
        )
        st.metric(
            label="Metrics",
            value=f"{info['metrics']:,}",
            help="Unique financial metrics (e.g., revenue, assets)"
        )

    with col2:
        st.metric(
            label="Periods",
            value=f"{info['periods']:,}",
            help="Total fiscal periods across all companies"
        )
        st.metric(
            label="Ratios",
            value=f"{info['ratios']:,}",
            help="Calculated financial ratios (e.g., ROE, ROA)"
        )

    # Extended context section
    with st.expander("Data Context", expanded=False):
        # Sector information
        if info['sectors'] > 0:
            st.markdown(f"**Sectors:** {info['sectors']}")
            sector_display = ", ".join(info['sector_list'][:5])
            if len(info['sector_list']) > 5:
                sector_display += f" (+{len(info['sector_list']) - 5} more)"
            st.caption(sector_display)

        # Year range
        if info['year_min'] and info['year_max']:
            if info['year_min'] == info['year_max']:
                st.markdown(f"**Fiscal Year:** {info['year_min']}")
            else:
                st.markdown(f"**Years:** {info['year_min']} - {info['year_max']}")

        # Total records
        st.markdown(f"**Total Records:** {info['total_records']:,}")

        # Currency info
        if info.get('currencies', 1) > 1:
            st.markdown(f"**Currencies:** {info['currencies']}")

    # Data freshness indicator
    if freshness['last_updated']:
        status_icon = {
            "fresh": "🟢",
            "recent": "🟡",
            "stale": "🔴"
        }.get(freshness['status'], "⚪")

        if freshness['days_old'] == 0:
            freshness_text = "Updated today"
        elif freshness['days_old'] == 1:
            freshness_text = "Updated yesterday"
        else:
            freshness_text = f"Updated {freshness['days_old']} days ago"

        st.caption(f"{status_icon} {freshness_text}")

        if freshness['status'] == 'stale':
            st.warning("Data may be outdated. Consider refreshing.", icon="⚠️")


def search_companies(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for companies by name.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of matching company dictionaries with name, sector, and year
    """
    if not query or len(query) < 2:
        return []

    data = load_data()
    analytics = data.get("analytics")

    if analytics is None or 'company_name' not in analytics.columns:
        return []

    # Case-insensitive search
    query_lower = query.lower()
    mask = analytics['company_name'].str.lower().str.contains(query_lower, na=False)
    matches = analytics[mask].drop_duplicates(subset=['company_name'])

    # Sort by exact match first, then alphabetically
    matches = matches.copy()
    matches['exact_match'] = matches['company_name'].str.lower() == query_lower
    matches = matches.sort_values(['exact_match', 'company_name'], ascending=[False, True])

    results = []
    for _, row in matches.head(limit).iterrows():
        result = {
            'company_name': row['company_name'],
            'sector': row.get('sector', 'Unknown'),
            'fiscal_year': row.get('fiscal_year', None)
        }
        results.append(result)

    return results


def render_company_search() -> Optional[str]:
    """Render company quick search functionality.

    Returns:
        Selected company name or None
    """
    st.header("Company Search")

    search_query = st.text_input(
        "Find Company",
        placeholder="Type company name...",
        key="company_search",
        help="Search for companies by name (partial matches supported)"
    )

    selected_company = None

    if search_query and len(search_query) >= 2:
        results = search_companies(search_query)

        if results:
            st.caption(f"Found {len(results)} match{'es' if len(results) > 1 else ''}")

            for i, result in enumerate(results[:5]):
                company_name = result['company_name']
                sector = result['sector']
                year = result['fiscal_year']

                # Truncate long names
                display_name = company_name[:35] + "..." if len(company_name) > 35 else company_name

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{display_name}**")
                    st.caption(f"{sector} | {year}" if year else sector)

                with col2:
                    if st.button("Query", key=f"company_btn_{i}"):
                        st.session_state.query = f"Show all financial data for {company_name}"
                        selected_company = company_name
                        st.rerun()

            if len(results) > 5:
                st.caption(f"... and {len(results) - 5} more")
        else:
            st.caption("No companies found. Try a different search term.")

    return selected_company


def render_dataset_selector() -> str:
    """Render dataset selection dropdown.

    Returns:
        Selected dataset name
    """
    st.header("Dataset Selection")

    dataset_choice = st.selectbox(
        "Choose dataset to query:",
        options=list(DATASET_DISPLAY_NAMES.keys()),
        format_func=lambda x: DATASET_DISPLAY_NAMES[x],
        help="Select which dataset to analyze with your queries"
    )

    # Show dataset description
    descriptions = {
        "analytics": "Pre-joined view with all metrics and ratios - best for most queries",
        "filings": "Company metadata including sector, symbol, and fiscal year info",
        "facts": "Raw financial metrics (16,000+ data points)",
        "ratios": "Calculated financial ratios (18,000+ data points)"
    }

    st.caption(descriptions.get(dataset_choice, ""))

    return dataset_choice


def render_column_reference(dataset_name: str) -> None:
    """Render available columns for the selected dataset.

    Args:
        dataset_name: Name of the currently selected dataset
    """
    st.header("Available Columns")

    data = load_data()
    df = data[dataset_name]

    if dataset_name == "analytics":
        cols = df.columns.tolist()
        # Show grouped columns
        with st.expander(f"View all {len(cols)} columns", expanded=False):
            # Group columns by category
            company_cols = [c for c in cols if c in ['company_name', 'company_folder', 'sector', 'symbol', 'ticker', 'isin', 'sector_primary', 'industry']]
            period_cols = [c for c in cols if c in ['period_end', 'fiscal_year', 'filing_id', 'currency', 'currency_code', 'rounding', 'scale_factor']]
            metric_cols = [c for c in cols if c not in company_cols + period_cols]

            st.markdown("**Company Info:**")
            st.code("\n".join(company_cols))

            st.markdown("**Period Info:**")
            st.code("\n".join(period_cols))

            st.markdown("**Financial Metrics:**")
            st.code("\n".join(sorted(metric_cols)))

    elif dataset_name == "filings":
        st.code("\n".join(df.columns.tolist()))

    elif dataset_name == "facts":
        st.markdown("**Columns:**")
        st.code("\n".join(df.columns.tolist()))
        with st.expander(f"Available Metrics ({df['metric'].nunique()})", expanded=False):
            st.code("\n".join(sorted(df['metric'].unique().tolist())))

    elif dataset_name == "ratios":
        st.markdown("**Columns:**")
        st.code("\n".join(df.columns.tolist()))
        with st.expander(f"Available Ratios ({df['ratio'].nunique()})", expanded=False):
            st.code("\n".join(sorted(df['ratio'].unique().tolist())))


def render_model_selector() -> bool:
    """Render the AI model selection dropdown.

    Returns:
        True if model was changed, False otherwise
    """
    st.header("AI Model")

    api_key = get_api_key()
    if not api_key:
        st.warning("Configure API key first")
        return False

    # Get available models
    model_options = get_model_options(api_key)

    if not model_options:
        st.error("Could not fetch models")
        return False

    # Get current selection
    current_model = get_selected_model()

    # If current model not in options, use default
    if current_model not in model_options:
        current_model = DEFAULT_MODEL
        if current_model not in model_options:
            current_model = list(model_options.keys())[0]

    # Model dropdown
    model_ids = list(model_options.keys())

    try:
        current_index = model_ids.index(current_model)
    except ValueError:
        current_index = 0

    selected_model = st.selectbox(
        "Choose AI model:",
        options=model_ids,
        index=current_index,
        format_func=lambda x: model_options.get(x, x),
        help="Select the AI model for answering queries. Pricing shown as $/1M tokens (input/output).",
        key="model_selector"
    )

    # Check if model changed
    model_changed = selected_model != get_selected_model()
    if model_changed:
        set_selected_model(selected_model)

    return model_changed


def render_llm_status() -> None:
    """Render LLM configuration status indicator."""
    status = get_llm_config_status()

    if status["configured"]:
        # Show compact status
        model_name = status['model_display']
        # Truncate long model names
        if len(model_name) > 30:
            model_name = model_name[:27] + "..."
        st.success(f"AI Ready", icon="✅")
    else:
        st.error("AI not configured", icon="⚠️")
        with st.expander("Setup required"):
            st.write("Configure your OpenRouter API key in secrets.")
            st.code('OPENROUTER_API_KEY = "sk-or-..."', language="toml")


def render_sidebar() -> Tuple[str, bool]:
    """Render the complete sidebar.

    Returns:
        Tuple of (selected dataset name, model_changed boolean)
    """
    with st.sidebar:
        render_database_info()
        st.divider()

        # Company quick search
        render_company_search()
        st.divider()

        dataset_choice = render_dataset_selector()
        st.divider()

        # Model selector (before column reference)
        model_changed = render_model_selector()
        st.divider()

        render_column_reference(dataset_choice)

        render_llm_status()

        return dataset_choice, model_changed
