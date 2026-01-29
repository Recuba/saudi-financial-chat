"""Sidebar component for Ra'd AI.

Provides database info, dataset selection, model selection, and column reference.
"""

import streamlit as st
from typing import Dict, Any, Tuple
from utils.data_loader import (
    load_data,
    get_dataset_info,
    get_column_info,
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


def render_database_info() -> None:
    """Render the database information section in collapsible expander."""
    info = get_dataset_info()

    with st.expander("📊 Database Info", expanded=False):
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
                help="Unique financial metrics"
            )

        with col2:
            st.metric(
                label="Periods",
                value=f"{info['periods']:,}",
                help="Total fiscal periods"
            )
            st.metric(
                label="Ratios",
                value=f"{info['ratios']:,}",
                help="Calculated financial ratios"
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

        dataset_choice = render_dataset_selector()
        st.divider()

        # Model selector (before column reference)
        model_changed = render_model_selector()
        st.divider()

        render_column_reference(dataset_choice)

        render_llm_status()

        return dataset_choice, model_changed
