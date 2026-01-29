"""Sidebar component for Ra'd AI.

Provides database info, dataset selection, and column reference.
"""

import streamlit as st
from typing import Dict, Any
from utils.data_loader import (
    load_data,
    get_dataset_info,
    get_column_info,
    DATASET_DISPLAY_NAMES
)
from utils.llm_config import get_llm_config_status


def render_database_info() -> None:
    """Render the database information section with tooltips."""
    st.header("Database Info")

    info = get_dataset_info()

    # Create metrics with full values (no truncation)
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


def render_llm_status() -> None:
    """Render LLM configuration status indicator."""
    status = get_llm_config_status()

    st.divider()

    if status["configured"]:
        st.success(f"AI: {status['model_display']}", icon="✅")
    else:
        st.error("AI not configured", icon="⚠️")
        with st.expander("Setup required"):
            st.write("Configure your OpenRouter API key in secrets.")
            st.code('OPENROUTER_API_KEY = "sk-or-..."', language="toml")


def render_sidebar() -> str:
    """Render the complete sidebar.

    Returns:
        Selected dataset name
    """
    with st.sidebar:
        render_database_info()
        st.divider()

        dataset_choice = render_dataset_selector()
        st.divider()

        render_column_reference(dataset_choice)

        render_llm_status()

        return dataset_choice
