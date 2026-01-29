"""Sidebar component for Ra'd AI.

Provides database info, dataset selection, model selection, and column reference.
"""

import streamlit as st
from typing import Dict, Any, Tuple, List, Optional
import logging

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
    get_model_fetch_error,
    clear_model_cache,
    DEFAULT_MODEL,
)

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300, show_spinner=False)
def _get_cached_unique_values(dataset_name: str, column_name: str) -> List[str]:
    """Get cached unique values for a column.

    Args:
        dataset_name: Name of the dataset
        column_name: Name of the column

    Returns:
        Sorted list of unique values
    """
    try:
        data = load_data()
        df = data.get(dataset_name)
        if df is not None and column_name in df.columns:
            return sorted(df[column_name].unique().tolist())
        return []
    except Exception as e:
        logger.error(f"Error getting unique values for {dataset_name}.{column_name}: {e}")
        return []


@st.cache_data(ttl=300, show_spinner=False)
def _get_cached_column_count(dataset_name: str, column_name: str) -> int:
    """Get cached count of unique values for a column.

    Args:
        dataset_name: Name of the dataset
        column_name: Name of the column

    Returns:
        Count of unique values
    """
    try:
        data = load_data()
        df = data.get(dataset_name)
        if df is not None and column_name in df.columns:
            return df[column_name].nunique()
        return 0
    except Exception as e:
        logger.error(f"Error counting unique values for {dataset_name}.{column_name}: {e}")
        return 0


def render_database_info() -> None:
    """Render the database information section with tooltips."""
    st.header("Database Info")

    try:
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
    except Exception as e:
        logger.error(f"Error rendering database info: {e}")
        st.error("Could not load database info")


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


def _filter_columns(columns: List[str], search_term: str) -> List[str]:
    """Filter columns by search term.

    Args:
        columns: List of column names
        search_term: Search string (case-insensitive)

    Returns:
        Filtered list of columns
    """
    if not search_term:
        return columns
    search_lower = search_term.lower()
    return [c for c in columns if search_lower in c.lower()]


def render_column_reference(dataset_name: str) -> None:
    """Render available columns for the selected dataset.

    Args:
        dataset_name: Name of the currently selected dataset
    """
    st.header("Available Columns")

    try:
        data = load_data()
        df = data.get(dataset_name)

        if df is None:
            st.error(f"Dataset '{dataset_name}' not found")
            return

        # Search box for filtering columns
        search_term = st.text_input(
            "Search columns:",
            placeholder="Type to filter...",
            key=f"col_search_{dataset_name}",
            help="Filter columns by name"
        )

        if dataset_name == "analytics":
            cols = df.columns.tolist()

            # Group columns by category
            company_cols = [c for c in cols if c in [
                'company_name', 'company_folder', 'sector', 'symbol',
                'ticker', 'isin', 'sector_primary', 'industry'
            ]]
            period_cols = [c for c in cols if c in [
                'period_end', 'fiscal_year', 'filing_id', 'currency',
                'currency_code', 'rounding', 'scale_factor'
            ]]
            metric_cols = [c for c in cols if c not in company_cols + period_cols]

            # Apply search filter
            if search_term:
                company_cols = _filter_columns(company_cols, search_term)
                period_cols = _filter_columns(period_cols, search_term)
                metric_cols = _filter_columns(metric_cols, search_term)

            total_filtered = len(company_cols) + len(period_cols) + len(metric_cols)

            with st.expander(f"View columns ({total_filtered}/{len(cols)})", expanded=bool(search_term)):
                if company_cols:
                    st.markdown("**Company Info:**")
                    st.code("\n".join(company_cols))

                if period_cols:
                    st.markdown("**Period Info:**")
                    st.code("\n".join(period_cols))

                if metric_cols:
                    st.markdown("**Financial Metrics:**")
                    st.code("\n".join(sorted(metric_cols)))

                if not (company_cols or period_cols or metric_cols):
                    st.info("No columns match your search")

        elif dataset_name == "filings":
            cols = df.columns.tolist()
            filtered_cols = _filter_columns(cols, search_term)
            with st.expander(f"View columns ({len(filtered_cols)}/{len(cols)})", expanded=bool(search_term)):
                if filtered_cols:
                    st.code("\n".join(filtered_cols))
                else:
                    st.info("No columns match your search")

        elif dataset_name == "facts":
            cols = df.columns.tolist()
            filtered_cols = _filter_columns(cols, search_term)

            st.markdown("**Columns:**")
            st.code("\n".join(filtered_cols) if filtered_cols else "No matches")

            metric_count = _get_cached_column_count("facts", "metric")
            with st.expander(f"Available Metrics ({metric_count})", expanded=False):
                metrics = _get_cached_unique_values("facts", "metric")
                filtered_metrics = _filter_columns(metrics, search_term)
                if filtered_metrics:
                    st.code("\n".join(filtered_metrics))
                else:
                    st.info("No metrics match your search")

        elif dataset_name == "ratios":
            cols = df.columns.tolist()
            filtered_cols = _filter_columns(cols, search_term)

            st.markdown("**Columns:**")
            st.code("\n".join(filtered_cols) if filtered_cols else "No matches")

            ratio_count = _get_cached_column_count("ratios", "ratio")
            with st.expander(f"Available Ratios ({ratio_count})", expanded=False):
                ratios = _get_cached_unique_values("ratios", "ratio")
                filtered_ratios = _filter_columns(ratios, search_term)
                if filtered_ratios:
                    st.code("\n".join(filtered_ratios))
                else:
                    st.info("No ratios match your search")

    except Exception as e:
        logger.error(f"Error rendering column reference: {e}")
        st.error("Could not load column information")


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

    # Show any fetch errors
    fetch_error = get_model_fetch_error()
    if fetch_error:
        st.warning(f"Using fallback models: {fetch_error}", icon="⚠️")

    # Get available models
    model_options = get_model_options(api_key)

    # Safety check - ensure we have options
    if not model_options:
        logger.error("No model options available, using default")
        model_options = {DEFAULT_MODEL: "Gemini 2.0 Flash (Default)"}

    # Get current selection
    current_model = get_selected_model()

    # Safe fallback if current model not in options
    if current_model not in model_options:
        current_model = DEFAULT_MODEL
        if current_model not in model_options:
            # Use first available model safely
            available_models = list(model_options.keys())
            if available_models:
                current_model = available_models[0]
            else:
                st.error("No AI models available")
                return False

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

    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄", help="Refresh model list", key="refresh_models"):
            clear_model_cache()
            st.rerun()

    # Check if model changed
    model_changed = selected_model != get_selected_model()
    if model_changed:
        set_selected_model(selected_model)
        logger.info(f"Model changed to: {selected_model}")

    return model_changed


def render_llm_status() -> None:
    """Render LLM configuration status indicator."""
    status = get_llm_config_status()

    st.divider()

    if status["configured"]:
        # Show compact status
        model_name = status['model_display']
        # Truncate long model names
        if len(model_name) > 30:
            model_name = model_name[:27] + "..."
        st.success("AI Ready", icon="✅")

        # Show warnings if any
        for warning in status.get("warnings", []):
            st.warning(warning, icon="⚠️")

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
