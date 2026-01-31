"""Sidebar component for Ra'd AI.

Provides database info, model selection, column reference, and view information.
Dataset selection is removed - queries are automatically routed to optimal views.
"""

import streamlit as st
from typing import Dict, Any
from utils.data_loader import load_tasi_data, get_view_info, VIEW_NAMES
from utils.llm_config import (
    get_llm_config_status,
    get_api_key,
    get_model_options,
    get_selected_model,
    set_selected_model,
    DEFAULT_MODEL,
)

# View descriptions for the optional View Info section
VIEW_DESCRIPTIONS = {
    "tasi_financials": "Full dataset with all metrics and ratios",
    "latest_financials": "Most recent record per company",
    "latest_annual": "Most recent annual data per company",
    "ticker_index": "Company metadata and identifiers",
    "company_annual_timeseries": "Annual data with YoY growth metrics",
    "sector_benchmarks_latest": "Sector-level aggregates and averages",
    "top_bottom_performers": "Top/bottom 20 companies per metric",
}


def render_database_info() -> None:
    """Render the database information section in collapsible expander."""
    info = get_view_info()

    with st.expander("Database Info", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Companies",
                value=f"{info['total_companies']:,}",
                help="Unique companies in the database"
            )

        with col2:
            st.metric(
                label="Records",
                value=f"{info['total_records']:,}",
                help="Total financial records"
            )

        st.caption(f"Views available: {info['views_available']}")


def render_column_reference() -> None:
    """Render available columns from the main tasi_financials view.

    Columns are grouped by category per metadata.json:
    - identifiers: filing_id, ticker, company_name, etc.
    - kpis: revenue, net_profit, total_assets, etc.
    - ratios: return_on_equity, gross_margin, etc.
    - categories: period_type, sector, company_type, etc.
    """
    st.header("Available Columns")

    data = load_tasi_data()
    df = data["tasi_financials"]
    cols = df.columns.tolist()

    # Group columns by category (per metadata.json)
    identifiers = ["filing_id", "ticker", "company_name", "fiscal_year", "fiscal_quarter"]
    kpis = ["revenue", "net_profit", "total_assets", "total_equity", "total_liabilities",
            "operating_cash_flow", "capex", "free_cash_flow"]
    ratios = ["return_on_equity", "return_on_assets", "gross_margin", "operating_margin",
              "net_margin", "current_ratio", "quick_ratio", "debt_to_equity",
              "debt_to_assets", "asset_turnover", "inventory_turnover", "interest_coverage_ratio"]
    categories = ["period_type", "sector", "company_type", "size_category", "year_quarter"]

    with st.expander(f"View all {len(cols)} columns", expanded=False):
        st.markdown("**Identifiers:**")
        available_ids = [c for c in identifiers if c in cols]
        st.code("\n".join(available_ids))

        st.markdown("**KPIs:**")
        available_kpis = [c for c in kpis if c in cols]
        st.code("\n".join(available_kpis))

        st.markdown("**Ratios:**")
        available_ratios = [c for c in ratios if c in cols]
        st.code("\n".join(available_ratios))

        st.markdown("**Categories:**")
        available_cats = [c for c in categories if c in cols]
        st.code("\n".join(available_cats))

        # Show any other columns not in predefined groups
        other_cols = [c for c in cols if c not in identifiers + kpis + ratios + categories]
        if other_cols:
            st.markdown("**Other:**")
            st.code("\n".join(sorted(other_cols)))


def render_view_info() -> None:
    """Render optional View Info section (collapsed by default).

    Shows which views are available and their purpose.
    """
    with st.expander("View Info", expanded=False):
        st.caption("Queries are automatically routed to the optimal view:")
        for view_name in VIEW_NAMES:
            desc = VIEW_DESCRIPTIONS.get(view_name, "")
            st.markdown(f"**{view_name}**")
            st.caption(desc)


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
        st.success(f"AI Ready", icon="checkmark")
    else:
        st.error("AI not configured", icon="warning")
        with st.expander("Setup required"):
            st.write("Configure your OpenRouter API key in secrets.")
            st.code('OPENROUTER_API_KEY = "sk-or-..."', language="toml")


def render_sidebar() -> bool:
    """Render the complete sidebar.

    Returns:
        model_changed boolean indicating if the AI model was changed
    """
    with st.sidebar:
        render_database_info()
        st.divider()

        # Model selector
        model_changed = render_model_selector()
        st.divider()

        render_column_reference()

        render_view_info()

        render_llm_status()

        return model_changed
